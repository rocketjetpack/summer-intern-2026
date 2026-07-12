---
title: "Lab 1: IPv6 Addressing & Neighbor Discovery"
---

# Lab 1: IPv6 Addressing & Neighbor Discovery

**Before starting**, read [IPv6 Basics](./basics) (this lab exercises it directly), and confirm IPv6 isn't administratively disabled on the ContainerLab host: `sysctl net.ipv6.conf.default.disable_ipv6` should print `0` (the double negative is the kernel's, not ours). If it prints `1`, resolve that with the lab host's administrator first.

Previous weeks' topologies came up fully addressed by the topology file. This one deliberately does not: the deployment gives you bare links and a forwarding-enabled router, and the addressing is the lab. You'll find the addresses the kernel already created without asking, watch Neighbor Discovery do ARP's job over multicast, then build global addressing and IPv6 static routes by hand, ending with the one v6-ism that matters most for the rest of the program: a route whose next-hop is a link-local address.

The topology is Week 5's familiar shape minus the collector: `host1` connects through `rtr1` to `host2`, using `nettools:week05` (no new image; its tools are all IPv6-capable).

**This lab should be done on the lab host configured for you to have privileged access to.**

## Step 0: Prepare the work directory

```bash
mkdir -p $HOME/container-lab/week07/lab1
cd $HOME/container-lab/week07/lab1
```

## Step 1: Write the topology file

<details>
<summary>Show <code>lab1.clab.yml</code> contents</summary>

```yaml
name: week07-lab1
topology:
  nodes:
    host1:
      kind: linux
      image: nettools:week05
    rtr1:
      kind: linux
      image: nettools:week05
      exec:
        - sysctl -w net.ipv6.conf.all.forwarding=1
    host2:
      kind: linux
      image: nettools:week05
  links:
    - endpoints: ["host1:eth1", "rtr1:eth1"]
    - endpoints: ["rtr1:eth2", "host2:eth1"]
```

</details><br />

Note what's missing compared to every previous week: no `ip addr add` lines at all. The only configuration is enabling IPv6 forwarding on `rtr1` (the v6 counterpart of the `ip_forward` sysctl from Week 5).

## Step 2: Deploy and find the addresses you didn't configure

```bash
containerlab deploy -t lab1.clab.yml
docker exec -it clab-week07-lab1-host1 ip -6 addr show dev eth1
```

Despite configuring nothing, `eth1` already has an address: an `fe80::...` link-local with scope `link`. Every IPv6 interface gets one automatically the moment it comes up. Compare it to the interface's MAC address (`ip link show dev eth1`): on most kernels the link-local is derived from the MAC by the EUI-64 procedure (flip the seventh bit of the first byte, insert `ff:fe` in the middle). Check whether the pattern holds for your containers.

Also look at the multicast groups the interface joined without asking:

```bash
docker exec -it clab-week07-lab1-host1 ip -6 maddr show dev eth1
```

You should see `ff02::1` (all-nodes) and an `ff02::1:ffXX:XXXX` entry: the **solicited-node** group for the link-local address. Paste your link-local into the [Code Lab](./address-anatomy) and confirm it derives the same solicited-node group the kernel joined.

## Step 3: Ping a link-local (and fail correctly first)

Find `rtr1`'s link-local on `eth1` (`docker exec clab-week07-lab1-rtr1 ip -6 addr show dev eth1`) and paste it below. Every later command that needs it will fill itself in; leave it blank and you can substitute by hand instead.

```js
const rtr1Field = html`<input type="text" placeholder="fe80::..." spellcheck="false" autocomplete="off"
  style="font-family:monospace;font-size:1em;width:100%;max-width:420px;padding:8px 10px;box-sizing:border-box;border:1px solid #1565c0;border-radius:4px;background:var(--theme-background,white);color:var(--theme-foreground,inherit)">`;
display(html`<div style="background:var(--theme-background-alt,#f5f5f5);border-left:4px solid #1565c0;border-radius:6px;padding:12px 16px;margin:8px 0;max-width:560px">
  <div style="font-weight:bold;margin-bottom:6px">rtr1's eth1 link-local</div>
  ${rtr1Field}
  <div style="font-size:0.85em;opacity:0.75;margin-top:6px">the <code>fe80::</code> address with scope <code>link</code> in <code>ip -6 addr show dev eth1</code></div>
</div>`);
const rtr1Input = Generators.input(rtr1Field);
```

```js
const rtr1LL = (rtr1Input ?? "").trim().split("%")[0] || "<rtr1-link-local>";
```

```js
{
  const v = (rtr1Input ?? "").trim();
  if (v && !v.toLowerCase().startsWith("fe80")) display(html`<div style="background:#fff3e0;border-left:4px solid #e65100;padding:8px 14px;margin:4px 0;font-family:monospace;font-size:0.9em">That doesn't look like a link-local; expected it to start with <strong>fe80</strong>. Check <code>ip -6 addr show dev eth1</code> for the address with scope <code>link</code>.</div>`);
}
```

Now, from `host1`, try the obvious thing:

```js
display(html`<pre><code>docker exec -it clab-week07-lab1-host1 ping -c 3 ${rtr1LL}</code></pre>`);
```

This fails (typically "Invalid argument"), and the failure is the lesson: a link-local address doesn't say which link it's valid on, and `host1` refuses to guess. Supply the zone ID:

```js
display(html`<pre><code>docker exec -it clab-week07-lab1-host1 ping -c 3 ${rtr1LL}%eth1</code></pre>`);
```

**Question:** `host1` has exactly one non-loopback interface, so the kernel could plausibly have guessed. Why is refusing still the right behavior for a router with dozens of interfaces, several of which might see the same link-local on the far end?

## Step 4: Watch Neighbor Discovery replace ARP

Flush `host1`'s neighbor cache so the resolution happens fresh, start a capture, and ping the router's link-local again:

```js
display(html`<pre><code>docker exec -it clab-week07-lab1-host1 ip -6 neigh flush dev eth1
docker exec -d clab-week07-lab1-host1 sh -c 'tcpdump -i eth1 -n icmp6 -c 20 > /tmp/nd.txt 2>&1'
docker exec -it clab-week07-lab1-host1 ping -c 2 ${rtr1LL}%eth1
docker exec -it clab-week07-lab1-host1 cat /tmp/nd.txt</code></pre>`);
```

In the capture, before any echo request can be sent, find:
- a **neighbor solicitation** from `host1`, addressed not to the router and not to broadcast, but to an `ff02::1:ff...` solicited-node multicast address, asking "who has this address";
- a **neighbor advertisement** from `rtr1` answering with its link-layer address.

That pair is ARP's request/reply, rebuilt on ICMPv6 and multicast. Now inspect the result:

```bash
docker exec -it clab-week07-lab1-host1 ip -6 neigh show dev eth1
```

The entry starts `REACHABLE`. Wait 30 seconds or so and run it again: it decays to `STALE`. Unlike the ARP table's binary present/absent, the neighbor cache tracks how much it currently trusts each entry (`REACHABLE`, `STALE`, `DELAY`, `PROBE`), and re-verifies on use.

**Questions:**
- The NS went to a multicast group whose membership is derived from the target address's last 24 bits. On a segment with 500 hosts, roughly how many of them process this NS, versus how many process an IPv4 ARP broadcast?
- What traffic would you expect a `STALE` entry to trigger the next time it's actually used? (Watch for it: ping again after the entry goes stale, with tcpdump running.)

## Step 5: Configure global addressing (and catch DAD in the act)

Plan, from the documentation prefix: `host1`/`rtr1` share `2001:db8:7:1::/64`, `rtr1`/`host2` share `2001:db8:7:2::/64`. Start a capture on `host1` first so you can see what address assignment itself triggers:

```bash
docker exec -d clab-week07-lab1-host1 sh -c 'tcpdump -i eth1 -n icmp6 -c 6 > /tmp/dad.txt 2>&1'
docker exec -it clab-week07-lab1-host1 ip -6 addr add 2001:db8:7:1::10/64 dev eth1
docker exec -it clab-week07-lab1-host1 cat /tmp/dad.txt
```

The capture shows a neighbor solicitation **sent by `host1` for its own new address, from the unspecified source `::`**. That's Duplicate Address Detection: claim the address only if nobody answers. Silence here is success. Now finish the addressing:

```bash
docker exec -it clab-week07-lab1-rtr1 ip -6 addr add 2001:db8:7:1::1/64 dev eth1
docker exec -it clab-week07-lab1-rtr1 ip -6 addr add 2001:db8:7:2::1/64 dev eth2
docker exec -it clab-week07-lab1-host2 ip -6 addr add 2001:db8:7:2::10/64 dev eth1
```

Note that `ip -6 addr show` on any interface now lists the GUA *and* the link-local side by side. Both stay; neither replaces the other.

## Step 6: Static routes, two ways

`host1` can reach `rtr1` but not `host2` (different /64, no route). Before adding one, look at the routes `host1` already has:

```bash
docker exec -it clab-week07-lab1-host1 ip -6 route show
```

There's already a default route, and it isn't yours: it points out `eth0`, the management interface ContainerLab attaches to every node so the lab tooling can reach it (the `3fff:...` addresses belong to that management network). This is why adding your own default route would fail with `File exists`, and why an unrouted ping right now gets a "no route" error back from a `3fff:...` gateway you never configured. Leave the management plumbing alone and add a route for exactly the network you need; Week 3's longest-prefix match means the specific route wins for lab traffic no matter what the default says:

```bash
docker exec -it clab-week07-lab1-host1 ip -6 route add 2001:db8:7:2::/64 via 2001:db8:7:1::1
docker exec -it clab-week07-lab1-host2 ip -6 route add 2001:db8:7:1::/64 via 2001:db8:7:2::1
docker exec -it clab-week07-lab1-host1 ping -c 3 2001:db8:7:2::10
docker exec -it clab-week07-lab1-host1 traceroute -6 2001:db8:7:2::10
```

End-to-end works. Now the v6-native way. Delete `host1`'s route and re-add it with `rtr1`'s **link-local** as the next-hop:

```js
display(html`<pre><code>docker exec -it clab-week07-lab1-host1 ip -6 route del 2001:db8:7:2::/64
docker exec -it clab-week07-lab1-host1 ip -6 route add 2001:db8:7:2::/64 via ${rtr1LL} dev eth1
docker exec -it clab-week07-lab1-host1 ping -c 3 2001:db8:7:2::10</code></pre>`);
```

It works identically (note the mandatory `dev eth1`: link-locals need their link named, the routing table's version of the zone ID). This is not a curiosity. It is how IPv6 routing normally operates: router-to-router next-hops are link-locals, and when a dynamic routing protocol installs routes (the weeks 8-10 BGP labs, or the [OSPFv3 stretch topic](../stretch/ospfv3/lab1) if you want the preview now), the next-hops it writes are `fe80::` addresses. A router's global addresses could renumber completely without a single next-hop changing.

**Question:** what operational advantage does that renumbering-independence give a large network, compared to IPv4's globally addressed next-hops?

## Step 7: Clean up

```bash
containerlab destroy -t lab1.clab.yml --cleanup
```

---

## Final questions

- Sketch, from memory, every address `rtr1` ended the lab holding across its two interfaces plus loopback. How many are there? Which would appear in a routing table's next-hop column, and which in a routing protocol's router-ID field?
- Nothing in this lab used broadcast even once. What replaced ARP's broadcast? In a network using DHCP, what other broadcast dependency would IPv6 have to replace, and does it?
- A /64 was used on both host-facing links here. Where in this topology would a /127 have been appropriate instead, if anywhere? (The [OSPFv3 stretch topic](../stretch/ospfv3/lab1)'s triangle topology, with its three router-to-router links, answers this.)
