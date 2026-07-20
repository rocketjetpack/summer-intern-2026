---
title: "Lab 1: Dual-Stack Operations"
---

# Lab 1: Dual-Stack Operations

**Before proceeding, complete [Week 7's Lab 1](../../week_07/lab1)** and read [this topic's objectives](./objectives); this lab assumes both.

Week 7's Lab 1 built an IPv6-only world. This lab builds the world you'll actually operate in: both families at once. The same `host1 - rtr1 - host2` topology comes up dual-stacked, and the experiments are about the seams: which family a client picks and why, what a dual-stack service sees, which of several source addresses gets used, and (the main event) what happens to a client when its preferred family silently breaks.

A note on method: several steps ask you to observe what an implementation does rather than telling you what it will do. That's deliberate. Address-selection and fallback behavior genuinely differ between libcs, tools, and versions, and "check, don't assume" is the actual operational skill here.

**This lab should be done on the lab host configured for you to have privileged access to.**

## Topology and addressing plan

Same shape as Week 7's Lab 1, now carrying two networks per link:

| Link | IPv4 | IPv6 |
|---|---|---|
| host1 to rtr1 | `10.7.1.0/24` (rtr1 `.1`, host1 `.10`) | `2001:db8:7:1::/64` (rtr1 `::1`, host1 `::10`) |
| rtr1 to host2 | `10.7.2.0/24` (rtr1 `.1`, host2 `.10`) | `2001:db8:7:2::/64` (rtr1 `::1`, host2 `::10`) |

## Step 0: Prepare the work directory

```bash
mkdir -p $HOME/container-lab/stretch-dualstack/lab1
cd $HOME/container-lab/stretch-dualstack/lab1
```

## Step 1: Write the topology file

Addressing is pre-configured this time (Week 7's Lab 1 already made you do it by hand; this lab's subject is what happens *after* addressing works).

<details>
<summary>Show <code>lab1.clab.yml</code> contents</summary>

```yaml
name: dualstack-lab1
topology:
  nodes:
    host1:
      kind: linux
      image: nettools:week05
      exec:
        - ip addr add 10.7.1.10/24 dev eth1
        - ip -6 addr add 2001:db8:7:1::10/64 dev eth1
        - ip route add 10.7.2.0/24 via 10.7.1.1
        - ip -6 route add 2001:db8:7:2::/64 via 2001:db8:7:1::1
    rtr1:
      kind: linux
      image: nettools:week05
      exec:
        - ip addr add 10.7.1.1/24 dev eth1
        - ip addr add 10.7.2.1/24 dev eth2
        - ip -6 addr add 2001:db8:7:1::1/64 dev eth1
        - ip -6 addr add 2001:db8:7:2::1/64 dev eth2
        - sysctl -w net.ipv4.ip_forward=1
        - sysctl -w net.ipv6.conf.all.forwarding=1
    host2:
      kind: linux
      image: nettools:week05
      exec:
        - ip addr add 10.7.2.10/24 dev eth1
        - ip -6 addr add 2001:db8:7:2::10/64 dev eth1
        - ip route add 10.7.1.0/24 via 10.7.2.1
        - ip -6 route add 2001:db8:7:1::/64 via 2001:db8:7:2::1
  links:
    - endpoints: ["host1:eth1", "rtr1:eth1"]
    - endpoints: ["rtr1:eth2", "host2:eth1"]
```

</details><br />

Notice the doubling: two address families means two `addr add` lines per interface, two static routes per host, and two forwarding sysctls on the router. (The routes are specific rather than defaults because every ContainerLab node already has default routes pointing at its management interface; Week 7's Lab 1 Step 6 has the full story.) Nothing is shared. That doubling *is* dual stack.

## Step 2: Deploy and verify both networks independently

```bash
containerlab deploy -t lab1.clab.yml
docker exec -it clab-dualstack-lab1-host1 ping -c 2 10.7.2.10
docker exec -it clab-dualstack-lab1-host1 ping -c 2 2001:db8:7:2::10
```

Both must work before continuing. If only one does, you have a working network and a broken network occupying the same cables, which is a preview of Step 6 rather than a blocker to it, but fix it anyway: the point of this step is knowing how to check each family on its own.

## Step 3: Give host2 a name, and see which family wins

Selection behavior only becomes visible when a *name* resolves to both families, so give `host2` two entries in `host1`'s hosts file:

```bash
docker exec -it clab-dualstack-lab1-host1 sh -c 'echo "10.7.2.10 host2" >> /etc/hosts && echo "2001:db8:7:2::10 host2" >> /etc/hosts'
```

Now ask the resolver directly what order it offers candidates in. Python's `getaddrinfo` is a clean window into the libc behavior every client on the box inherits:

```bash
docker exec -it clab-dualstack-lab1-host1 python3 -c "
import socket
for family, _, _, _, sockaddr in socket.getaddrinfo('host2', 80, proto=socket.IPPROTO_TCP):
    print('IPv6' if family == socket.AF_INET6 else 'IPv4', sockaddr[0])
"
```

Then check what two everyday tools actually do with that ordering (the first line of `ping host2` names the address it chose; for `wget` you'll see the family in the server log in Step 5):

```bash
docker exec -it clab-dualstack-lab1-host1 ping -c 1 host2
```

**Questions:**
- What order did `getaddrinfo` return? Does it match RFC 6724's general preference for IPv6 when both are usable?
- Did `ping` follow the same preference? (Don't assume tools agree with the resolver's ordering, or with each other; record what you actually saw.)

## Step 4: Source address selection

Destinations aren't the only thing being selected; the client also picks which of its own addresses to source from. Give `host1` a second IPv6 address, a ULA, then ask the kernel what it would choose for each kind of destination:

```bash
docker exec -it clab-dualstack-lab1-host1 ip -6 addr add fd00:7:1::10/64 dev eth1
docker exec -it clab-dualstack-lab1-host1 ip -6 route get 2001:db8:7:2::10
docker exec -it clab-dualstack-lab1-host1 ip -6 route get fd00:7:1::1
```

The `src` field in each answer is the kernel applying RFC 6724's source-selection rules live: the global destination gets the global source, and the ULA destination gets the ULA source, with no configuration telling it to.

**Question:** why is matching scope the right default? Sketch what would happen to the return traffic if the kernel sourced a packet to a global destination from `fd00:7:1::10`.

## Step 5: Run a dual-stack service and read its logs

Start a dual-stack HTTP server on `host2` (binding `::` on Linux accepts both families by default), then hit it from `host1` by name:

```bash
docker exec -d clab-dualstack-lab1-host2 sh -c 'cd /tmp && python3 -m http.server 8000 --bind :: > /tmp/http.log 2>&1'
docker exec -it clab-dualstack-lab1-host1 wget -q -O /dev/null http://host2:8000/ && echo OK
docker exec -it clab-dualstack-lab1-host1 wget -q -O /dev/null http://10.7.2.10:8000/ && echo OK
docker exec -it clab-dualstack-lab1-host2 cat /tmp/http.log
```

Read the two client addresses in the log. The by-name request shows which family `wget` preferred (compare against Step 3's prediction). The forced-IPv4 request appears as something stranger: `::ffff:10.7.1.10`, a **v4-mapped address**. That's one socket serving both families, representing IPv4 clients inside IPv6 address syntax. It exists in the server's logs and APIs only; no packet on the wire carries it.

**Question:** an access-control list on this server matches clients against `10.7.1.0/24` and is evaluated against the address exactly as logged. What happens, and what's the fix?

## Step 6: Break IPv6 silently, and time the damage

The main event. Black-hole IPv6 forwarding on the router while leaving every address, route, and AAAA-equivalent hosts entry in place, so clients still *believe* IPv6 works:

```bash
docker exec -it clab-dualstack-lab1-rtr1 sysctl -w net.ipv6.conf.all.forwarding=0
```

Confirm the deception: `ping -c 2 2001:db8:7:2::10` from `host1` now fails, but `ip -6 route` on `host1` still shows a perfectly healthy-looking route toward `host2`'s network. Nothing on `host1` knows anything is wrong. Now time the naive client (the `-T` flag caps how long busybox wget waits per attempt; without it you're at the kernel's TCP timeout, which is minutes):

```bash
docker exec -it clab-dualstack-lab1-host1 sh -c 'time wget -T 15 -q -O /dev/null http://host2:8000/ && echo SUCCEEDED || echo FAILED'
```

Watch what it does: does it hang for the full 15 seconds on the IPv6 attempt? Does it then fall back to IPv4 and succeed, or fail outright? Implementations differ here, and whichever you observed, the user experience was decided by the client's fallback logic, not by the network's IPv4 health, which was perfect the whole time.

Now compare what you measured against the arithmetic. Set the first slider to the timeout you just used, and see what a Happy Eyeballs client would have done with the same broken network:

```js
const v6Timeout = view(Inputs.range([1, 120], {step: 1, value: 15, label: "Naive client's connect timeout (s)"}));
const heDelayMs = view(Inputs.range([100, 2000], {step: 50, value: 250, label: "Happy Eyeballs head start (ms)"}));
const v4ConnectMs = view(Inputs.range([1, 300], {step: 1, value: 40, label: "Working IPv4 connect time (ms)"}));
```

```js
const naiveMs = v6Timeout * 1000 + v4ConnectMs;
const heMs = heDelayMs + v4ConnectMs;
display(html`
  <div style="background:#f8f8f8;border-left:4px solid #1565c0;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    IPv6 path silently broken; IPv4 path healthy.<br>
    Naive sequential client: waits out the full v6 timeout, then connects over v4:
    <strong>${(naiveMs / 1000).toFixed(2)}s</strong> to a working connection.<br>
    Happy Eyeballs client: gives v6 a ${heDelayMs}ms head start, then races v4:
    <strong>${(heMs / 1000).toFixed(2)}s</strong>.<br>
    That's <strong>${(naiveMs / heMs).toFixed(0)}x</strong> faster, and the user never learns IPv6 was down at all.
  </div>
`);
```

That last line cuts both ways: Happy Eyeballs protects users from broken IPv6, and by doing so lets an unnoticed IPv6 outage persist for months, because nothing visibly fails. Hold that thought for the final questions. Then compare against *absent* (rather than broken) IPv6 by removing the IPv6 hosts entry and re-running the timing:

```bash
docker exec -it clab-dualstack-lab1-host1 sh -c "sed -i '/2001:db8:7:2::10/d' /etc/hosts"
docker exec -it clab-dualstack-lab1-host1 sh -c 'time wget -T 15 -q -O /dev/null http://host2:8000/ && echo SUCCEEDED || echo FAILED'
```

Instant success over IPv4. Same broken network, radically different experience, and the only difference is whether the client was *told* about the IPv6 address it couldn't reach.

Restore everything for the record:

```bash
docker exec -it clab-dualstack-lab1-host1 sh -c 'echo "2001:db8:7:2::10 host2" >> /etc/hosts'
docker exec -it clab-dualstack-lab1-rtr1 sysctl -w net.ipv6.conf.all.forwarding=1
```

**Questions:**
- Rank the three scenarios you measured (working v6, broken v6, absent v6) by time-to-working-connection. Why is broken worse than absent, mechanically? What does each case return to the client, and when?
- Every v4 counter on `rtr1` looked perfect throughout the outage. Which of the observation tools from earlier weeks (interface counters from Week 4, flow telemetry from Week 5) would have caught the v6 black hole, and what specifically would it have shown?

## Step 7: Clean up

```bash
containerlab destroy -t lab1.clab.yml --cleanup
```

---

## Bonus challenge: build a Happy Eyeballs client

Python's `asyncio` implements RFC 8305 directly: `asyncio.open_connection(..., happy_eyeballs_delay=0.25)`. Re-break IPv6 as in Step 6, then race the same connection a naive client struggled with:

```bash
docker exec -it clab-dualstack-lab1-host1 python3 -c "
import asyncio, time
async def main():
    t0 = time.monotonic()
    reader, writer = await asyncio.open_connection('host2', 8000, happy_eyeballs_delay=0.25)
    print(f'connected in {time.monotonic() - t0:.3f}s to', writer.get_extra_info('peername')[0])
    writer.close(); await writer.wait_closed()
asyncio.run(main())
"
```

Compare the connect time against your naive-client measurement, and check which address family it landed on. Then re-enable IPv6 forwarding and run it again: does it go back to preferring IPv6? What does that tell you about how thoroughly Happy Eyeballs hides the difference between a healthy and a half-broken dual-stack network?

## Final questions

- Write the one-paragraph incident report for Step 6 as if it happened in production: what users saw, what the network team's IPv4-centric dashboard showed, and what the actual fault was. Where's the gap?
- The Week 10 production deployment adds IPv6 BGP alongside working IPv4 on the same routers. Using this lab's two-independent-networks model: what's the blast radius on IPv4 if the new IPv6 configuration is wrong, and which specific things (interfaces? sessions? filters?) are shared enough to be worth double-checking anyway?
