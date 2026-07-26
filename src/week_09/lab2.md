---
title: "Lab 2: Selective Route Acceptance at a Dual-Edge Boundary"
---

# Lab 2: Selective Route Acceptance at a Dual-Edge Boundary

**Before starting**, complete [Lab 1](./lab1); this lab assumes its FRR fundamentals (session states, RFC 8212's default-deny, reading a BGP table). What's new here is scale, a dual-upstream design, and a lesson Lab 1 only hinted at: accepting a route is a decision you make, not a fact you passively receive.

This lab hands you a **working IPv4 setup already built**: interface addressing, BGP sessions, and the exact acceptance policy this scenario calls for, pre-written into `sw1`/`sw2`'s starting configuration. Deploy it, read it, and confirm it does what it claims before touching anything. Then your actual task starts: build the identical design again, from nothing, for IPv6, using the given IPv4 blocks as the pattern to mirror rather than something to invent from scratch.

## The scenario

Two upstream feeds sit at your organization's edge. `rtr1` peers with `isp1`, which represents the public Internet: a full table, roughly five hundred IPv4 and five hundred IPv6 routes, plus a default. `rtr2` peers with `isp2`, which represents Internet2, the national research and education network: a smaller table, half the size of the public one, plus its own default. That smaller table is not arbitrary; it's an actual subset of the larger one, because every Internet2-reachable destination is also reachable via the public Internet. Internet2 is simply the preferred, more direct path to those specific destinations.

You will not build `rtr1`, `rtr2`, `isp1`, or `isp2`, or see their configuration, for the same reason you'd never see a real ISP's router configuration: they're already running, maintained by someone else, and your job starts at the peering session, not before it. What you need to know about them is this: **both routers forward everything they learn, completely unfiltered, to both of your switches.** Nobody upstream has curated anything for you; that decision is entirely downstream, at the switches, which is exactly why acceptance policy has to exist there at all. Peer with both `rtr1` and `rtr2` and accept whatever arrives, with no policy, and you'd get the public Internet's full table, Internet2's full table, and two separate default routes, all mixed together, with the 250-ish overlapping prefixes arriving twice, decided only by BGP's own tiebreakers rather than anything you intended. That is the actual starting condition of a dual-homed edge. The IPv4 half of it has already been solved for you, as a worked example; the IPv6 half is where you build the same solution yourself.

Your job is the pair of switches behind them, `sw1` and `sw2`. Both are full-mesh peered with both `rtr1` and `rtr2`, and both are connected directly to each other over what represents an MCLAG (multi-chassis link aggregation) peer link. That full mesh is deliberate: whichever switch traffic happens to land on, it needs a direct route to both the public-Internet default and the Internet2 specifics, without ever needing to cross over to its partner switch first to reach an egress router. One honest limitation: real MCLAG needs a vendor-specific control-plane protocol (Cisco's vPC, Arista's MLAG, and so on) to make two switches present as one logical unit; FRR doesn't implement that, so the peer link in this lab is real and addressed, but it isn't running an actual MCLAG protocol. Treat it as the physical link that role would occupy, not a working implementation of it.

The routes themselves are synthetic and deliberately inert: drawn from two IANA/IETF-reserved blocks set aside for network benchmarking, [198.18.0.0/15](https://www.rfc-editor.org/rfc/rfc2544.html) (IPv4, RFC 2544) and [2001:2::/48](https://www.rfc-editor.org/rfc/rfc5180.html) (IPv6, RFC 5180). Nothing in this lab is reachable, and nothing needs to be: the point is to observe *which path gets chosen and why*, not to deliver a packet anywhere.

**This lab should be done on the lab host configured for you to have privileged access to.**

## Topology and addressing

![Lab 2 topology: isp1 (public Internet, full table) feeds rtr1; isp2 (Internet2, a real subset) feeds rtr2; both rtr1 and rtr2 connect to both sw1 and sw2 via host bridges, full mesh; sw1 and sw2 also connect directly to each other over an MCLAG-representing peer link](./topology2.svg)

`rtr1` and `rtr2` are already deployed and already peering upstream by the time you start. The two boxes labeled `br-w9l2-*` are host bridges, not containers you create; they already exist too. Your topology attaches to them, and separately links `sw1` directly to `sw2`.

Fixed facts about the upstream side (do not change these; `rtr1`/`rtr2` were configured to expect exactly this):

| | ASN | Peers on `br-w9l2-r1` | Peers on `br-w9l2-r2` |
|---|---|---|---|
| `rtr1` | 64505 | v4 `198.51.100.17`, v6 `2001:db8:9:f5::1` | n/a |
| `rtr2` | 64506 | n/a | v4 `198.51.100.25`, v6 `2001:db8:9:f6::1` |

Your addressing, on the two bridge segments and the direct peer link:

| | ASN | Router ID | Loopback |
|---|---|---|---|
| `sw1` | 64500 | 10.9.0.5 | `2001:db8:9:0::5/128`, `192.0.2.5/32` |
| `sw2` | 64500 | 10.9.0.6 | `2001:db8:9:0::6/128`, `192.0.2.6/32` |

| Segment | Prefix | `sw1` | `sw2` |
|---|---|---|---|
| `br-w9l2-r1` (v4) | `198.51.100.16/29` | `198.51.100.18` | `198.51.100.19` |
| `br-w9l2-r1` (v6) | `2001:db8:9:f5::/125` | `2001:db8:9:f5::2` | `2001:db8:9:f5::3` |
| `br-w9l2-r2` (v4) | `198.51.100.24/29` | `198.51.100.26` | `198.51.100.27` |
| `br-w9l2-r2` (v6) | `2001:db8:9:f6::/125` | `2001:db8:9:f6::2` | `2001:db8:9:f6::3` |
| MCLAG peer link (v4) | `198.51.100.28/30` | `198.51.100.29` | `198.51.100.30` |
| MCLAG peer link (v6) | `2001:db8:9:f7::/127` | `2001:db8:9:f7::` | `2001:db8:9:f7::1` |

One deliberate simplification: every session in this lab peers on **global** addresses, not link-locals. A bridge segment carries three routers (`rtr1`/`rtr2` plus both switches), and predicting which auto-assigned `fe80::` belongs to which peer ahead of time isn't practical the way it was on Lab 1's point-to-point links. Link-local next-hops were Lab 1's and Week 7's lesson; this lab's lesson is policy, so global addressing here is a legitimate simplification, not an oversight.

`sw1` and `sw2` share AS 64500, the same number Lab 1's `rtr-org` used: they're still one organization, now with two redundant switches instead of one router.

## Step 0: Prepare the work directory

```bash
mkdir -p $HOME/container-lab/week09/lab2
cd $HOME/container-lab/week09/lab2
cp ../daemons .   # the same daemons file from Lab 0 (bgpd=yes)
```

## Step 1: Write the pre-seeded starting configs

This is the given foundation, not something you compose: full interface addressing (both address families, since the physical links exist regardless of which protocol runs over them), the two IPv4 BGP sessions, and IPv4's acceptance policy already applied and correct. Nothing about the IPv4 half is left for you to figure out.

<details>
<summary>Show <code>sw1-frr.conf</code> contents</summary>

```
frr defaults traditional
hostname sw1
log stdout informational
!
interface lo
 ip address 192.0.2.5/32
 ipv6 address 2001:db8:9:0::5/128
!
interface eth1
 ip address 198.51.100.18/29
 ipv6 address 2001:db8:9:f5::2/125
!
interface eth2
 ip address 198.51.100.26/29
 ipv6 address 2001:db8:9:f6::2/125
!
interface eth3
 ip address 198.51.100.29/30
 ipv6 address 2001:db8:9:f7::/127
!
ip prefix-list ONLY-DEFAULT4 seq 5 permit 0.0.0.0/0
ip prefix-list DENY-DEFAULT4 seq 5 deny 0.0.0.0/0
ip prefix-list DENY-DEFAULT4 seq 10 permit 0.0.0.0/0 le 32
route-map RTR1-IN4 permit 10
 match ip address prefix-list ONLY-DEFAULT4
route-map RTR2-IN4 permit 10
 match ip address prefix-list DENY-DEFAULT4
!
router bgp 64500
 bgp router-id 10.9.0.5
 neighbor 198.51.100.17 remote-as 64505
 neighbor 198.51.100.25 remote-as 64506
 address-family ipv4 unicast
  neighbor 198.51.100.17 activate
  neighbor 198.51.100.17 route-map RTR1-IN4 in
  neighbor 198.51.100.25 activate
  neighbor 198.51.100.25 route-map RTR2-IN4 in
 exit-address-family
!
```

</details>

<details>
<summary>Show <code>sw2-frr.conf</code> contents</summary>

```
frr defaults traditional
hostname sw2
log stdout informational
!
interface lo
 ip address 192.0.2.6/32
 ipv6 address 2001:db8:9:0::6/128
!
interface eth1
 ip address 198.51.100.19/29
 ipv6 address 2001:db8:9:f5::3/125
!
interface eth2
 ip address 198.51.100.27/29
 ipv6 address 2001:db8:9:f6::3/125
!
interface eth3
 ip address 198.51.100.30/30
 ipv6 address 2001:db8:9:f7::1/127
!
ip prefix-list ONLY-DEFAULT4 seq 5 permit 0.0.0.0/0
ip prefix-list DENY-DEFAULT4 seq 5 deny 0.0.0.0/0
ip prefix-list DENY-DEFAULT4 seq 10 permit 0.0.0.0/0 le 32
route-map RTR1-IN4 permit 10
 match ip address prefix-list ONLY-DEFAULT4
route-map RTR2-IN4 permit 10
 match ip address prefix-list DENY-DEFAULT4
!
router bgp 64500
 bgp router-id 10.9.0.6
 neighbor 198.51.100.17 remote-as 64505
 neighbor 198.51.100.25 remote-as 64506
 address-family ipv4 unicast
  neighbor 198.51.100.17 activate
  neighbor 198.51.100.17 route-map RTR1-IN4 in
  neighbor 198.51.100.25 activate
  neighbor 198.51.100.25 route-map RTR2-IN4 in
 exit-address-family
!
```

</details><br />

Read the policy block before moving on, because you'll be reproducing its shape from memory in a few minutes. Two prefix-lists, shaped oppositely on purpose: `ONLY-DEFAULT4` has a single `permit` entry, and a prefix-list with any entry at all denies everything that doesn't match one, so "only the default" costs one line. `DENY-DEFAULT4` needs two: deny the one exception, then explicitly re-permit everything else (`le 32`, so no prefix is too specific to match). Each prefix-list is wired to a `route-map`, and each route-map is applied `in` to exactly one neighbor under `address-family ipv4 unicast`. That's the whole pattern: prefix-list, route-map, applied inbound, per neighbor, per family.

## Step 2: Write the topology file and deploy

The two bridge nodes below are not new: they're the same `br-w9l2-r1`/`br-w9l2-r2` that `rtr1`/`rtr2` already attach to. Containerlab lets independently-deployed topologies share a pre-existing bridge; that's exactly what's happening. One coordination detail that's easy to get wrong: for a bridge node, the name after the colon in a link (`br-w9l2-r1:w9l2-r1-sw1`, below) isn't an interface inside some container's namespace, the way `eth1` is for every other node in this program. A bridge has no container namespace at all; that name becomes a veth interface created directly in the **host's root namespace**, which means it must be unique across the *entire host*, not just within this one bridge's own links. `rtr1`/`rtr2` already claimed `w9l2-r1-rtr1` and `w9l2-r2-rtr2` on these two bridges; reusing something as generic as `eth1` or `eth2` here would collide with whatever else happens to be using that name on the same host, possibly including the other bridge's own links. The `sw1`-`sw2` link is new and entirely yours: a direct connection, not through either bridge, so its endpoint names live inside `sw1`/`sw2`'s own namespaces as usual.

<details>
<summary>Show <code>lab2.clab.yml</code> contents</summary>

```yaml
name: week09-lab2-part2
topology:
  nodes:
    sw1:
      kind: linux
      image: quay.io/frrouting/frr:10.6.1
      binds:
        - daemons:/etc/frr/daemons
        - sw1-frr.conf:/etc/frr/frr.conf
    sw2:
      kind: linux
      image: quay.io/frrouting/frr:10.6.1
      binds:
        - daemons:/etc/frr/daemons
        - sw2-frr.conf:/etc/frr/frr.conf
    br-w9l2-r1:
      kind: bridge
    br-w9l2-r2:
      kind: bridge
  links:
    - endpoints: ["sw1:eth1", "br-w9l2-r1:w9l2-r1-sw1"]
    - endpoints: ["sw2:eth1", "br-w9l2-r1:w9l2-r1-sw2"]
    - endpoints: ["sw1:eth2", "br-w9l2-r2:w9l2-r2-sw1"]
    - endpoints: ["sw2:eth2", "br-w9l2-r2:w9l2-r2-sw2"]
    - endpoints: ["sw1:eth3", "sw2:eth3"]
```

</details><br />

```bash
containerlab deploy -t lab2.clab.yml
docker exec -it clab-week09-lab2-part2-sw1 ip -6 addr show dev eth1
```

If the bridges don't exist yet on this host, that's the one thing you can't fix from your side; check with whoever runs Part 1 before going further.

## Step 3: Confirm the given IPv4 foundation actually works

Enter `sw1`'s CLI and check what the pre-seeded config already achieved, with nothing more typed:

```bash
docker exec -it clab-week09-lab2-part2-sw1 vtysh -c 'show bgp ipv4 unicast summary'
```

Both sessions should already be `Established`: `rtr1`'s showing exactly 1 prefix, `rtr2`'s showing close to 250. Confirm the shape is what the scenario calls for:

```bash
docker exec -it clab-week09-lab2-part2-sw1 vtysh -c 'show bgp ipv4 unicast'
docker exec -it clab-week09-lab2-part2-sw1 vtysh -c 'show ip route bgp'
```

One `B` route for `0.0.0.0/0` via `rtr1`, and roughly 250 specific `B` routes via `rtr2`. This is the finished design from Lab 2's scenario, already running, before you've written a single line. Nothing here is a mystery to solve; it's a worked example to read. Go back to Step 1's config and find, concretely: which single prefix-list entry makes "only the default" work in one line, and which two entries make "everything but the default" take two. You'll write the IPv6 equivalents of exactly these four lines yourself in Step 5.

## Step 4: Add IPv6 neighbors yourself, and meet RFC 8212 again

The IPv4 half is done. IPv6 is entirely your job, starting now, and you build it the same way Lab 1 had you build BGP from nothing: live, in `vtysh`, one piece at a time. Start with neighbors only, no policy yet:

```
configure
router bgp 64500
 neighbor 2001:db8:9:f5::1 remote-as 64505
 neighbor 2001:db8:9:f6::1 remote-as 64506
 address-family ipv6 unicast
  neighbor 2001:db8:9:f5::1 activate
  neighbor 2001:db8:9:f6::1 activate
 exit-address-family
end
```

Check the result:

```
show bgp ipv6 unicast summary
```

Both sessions reach `Established`, but where a prefix count belongs, you'll see `(Policy)`, the exact marker Lab 1's Step 5 introduced. This isn't a mistake; it's RFC 8212 doing precisely what it did there: an eBGP session with no configured import policy accepts nothing. The IPv4 sessions never showed you this, because Step 1 handed you their policy already written. IPv6 shows it to you because you haven't written it yet.

**Question:** the IPv4 sessions in this same config never passed through a visible `(Policy)` state that you personally watched clear. Did RFC 8212 not apply to them, or did something else account for why you never saw it?

## Step 5: Write the IPv6 acceptance policy, mirroring the given IPv4 pattern

Same design intent as IPv4, same shape of filter, translated one address family over. From `rtr1`, accept only the default; from `rtr2`, accept everything except the default:

```
configure
ipv6 prefix-list ONLY-DEFAULT6 seq 5 permit ::/0
ipv6 prefix-list DENY-DEFAULT6 seq 5 deny ::/0
ipv6 prefix-list DENY-DEFAULT6 seq 10 permit ::/0 le 128
route-map RTR1-IN6 permit 10
 match ipv6 address prefix-list ONLY-DEFAULT6
route-map RTR2-IN6 permit 10
 match ipv6 address prefix-list DENY-DEFAULT6
router bgp 64500
 address-family ipv6 unicast
  neighbor 2001:db8:9:f5::1 route-map RTR1-IN6 in
  neighbor 2001:db8:9:f6::1 route-map RTR2-IN6 in
 exit-address-family
end
clear bgp ipv6 unicast *
```

Every line here is the IPv4 block from Step 1 with the same structure: `ip` became `ipv6`, `0.0.0.0/0` became `::/0`, `le 32` became `le 128` (the full address length changed, the *shape* of the policy didn't). Confirm it landed:

```
show bgp ipv6 unicast summary
```

`(Policy)` should be gone, replaced by real counts: 1 from `rtr1`, close to 250 from `rtr2`, the same shape IPv4 already had.

**Question:** IPv4's `DENY-DEFAULT4` used `le 32`; IPv6's used `le 128`. What would `DENY-DEFAULT6` actually match if you had mistakenly written `le 32` instead (a plausible copy-paste mistake going the other direction, from v6 back to v4)? Would FRR reject the line, silently match nothing, or something else?

## Step 6: Repeat the IPv6 build on `sw2`

`sw2`'s starting config from Step 1 already carries the same finished IPv4 block `sw1`'s did, addressed for `sw2`. What it doesn't have is IPv6, for the same reason `sw1` didn't: that part is yours to build on every box, not something to deploy once and forget. Repeat Steps 4 and 5 on `sw2`, addresses adjusted:

<details>
<summary>Show the full IPv6 addition for <code>sw2</code></summary>

```
configure
ipv6 prefix-list ONLY-DEFAULT6 seq 5 permit ::/0
ipv6 prefix-list DENY-DEFAULT6 seq 5 deny ::/0
ipv6 prefix-list DENY-DEFAULT6 seq 10 permit ::/0 le 128
route-map RTR1-IN6 permit 10
 match ipv6 address prefix-list ONLY-DEFAULT6
route-map RTR2-IN6 permit 10
 match ipv6 address prefix-list DENY-DEFAULT6
router bgp 64500
 neighbor 2001:db8:9:f5::1 remote-as 64505
 neighbor 2001:db8:9:f6::1 remote-as 64506
 address-family ipv6 unicast
  neighbor 2001:db8:9:f5::1 activate
  neighbor 2001:db8:9:f5::1 route-map RTR1-IN6 in
  neighbor 2001:db8:9:f6::1 activate
  neighbor 2001:db8:9:f6::1 route-map RTR2-IN6 in
 exit-address-family
end
```

Identical to `sw1`'s, because the design doesn't change per switch, only the router typing it does.

</details><br />

Confirm both address families on `sw2` reach the same shape as `sw1`: IPv4 already correct from the start, IPv6 now matching it: exactly 1 prefix from `rtr1`, close to 250 from `rtr2`, in both families.

## Step 7: Prove the design, not just the session count, in both families

On `sw1`, pick an address inside one of `rtr2`'s (Internet2's) IPv4 prefixes and check the kernel's forwarding decision:

```bash
docker exec -it clab-week09-lab2-part2-sw1 ip route get <an address from one of rtr2's IPv4 prefixes>
```

The next-hop should land on `rtr2`. Now pick an address that is **not** in any prefix you saw from `rtr2`, anything outside the benchmarking blocks entirely, like `8.8.8.8`:

```bash
docker exec -it clab-week09-lab2-part2-sw1 ip route get 8.8.8.8
```

This one resolves via `rtr1`'s default. Same mechanism, two different outcomes, decided entirely by whether a specific route exists. Now do the same for IPv6, the half you actually built yourself:

```bash
docker exec -it clab-week09-lab2-part2-sw1 ip -6 route get <an address from one of rtr2's IPv6 prefixes>
docker exec -it clab-week09-lab2-part2-sw1 ip -6 route get 2001:4860:4860::8888
```

The first lands on `rtr2`, the second on `rtr1`'s default, exactly mirroring the IPv4 result. This is the actual proof that Steps 4-5 worked, not just that `show bgp` reported the right numbers.

Also confirm the point of the full mesh: run all four commands on `sw2` as well. Every one should resolve identically, via `sw2`'s own direct sessions to `rtr1` and `rtr2`, without anything needing to cross the `sw1`-`sw2` link at all.

## Step 8: Fail `rtr2` and watch the fallback, in both families

With the addresses from Step 7 in hand, disable `sw1`'s sessions to `rtr2`, IPv4 and IPv6 together:

```
configure
router bgp 64500
 neighbor 198.51.100.25 shutdown
 neighbor 2001:db8:9:f6::1 shutdown
end
```

`show bgp ipv4 unicast summary` and `show bgp ipv6 unicast summary` both show the session drop and its prefix count go to 0. Re-run `ip route get` and `ip -6 route get` for the Internet2 addresses from Step 7: both now resolve via `rtr1`'s default, the only route left for either. This is graceful degradation, in both address families identically: losing Internet2 doesn't black-hole those destinations, it just routes them less optimally, over the public Internet instead. Bring the sessions back:

```
configure
router bgp 64500
 no neighbor 198.51.100.25 shutdown
 no neighbor 2001:db8:9:f6::1 shutdown
end
```

and confirm both specific routes reclaim their paths once the sessions re-establish.

**Question:** during that outage, did any traffic need to cross the `sw1`-`sw2` peer link to keep working? What scenario, involving this same topology, actually would require it?

## Step 9: Clean up

```bash
containerlab destroy -t lab2.clab.yml --cleanup
```

Part 1 (`isp1`, `isp2`, `rtr1`, `rtr2`, and the bridges) is not yours to destroy; leave it running.

---

## Final questions

- Step 4 showed `(Policy)` on the IPv6 sessions, but the IPv4 sessions in the exact same `router bgp 64500` block never showed it to you directly. Both address families are governed by the identical RFC 8212 rule. What actually differed between them, and where did IPv4's policy compliance actually get satisfied?
- Internet2's routes are a real subset of the public Internet's, not a disjoint set. Why does that make operational sense, and what would change about this lab's design if Internet2 instead advertised destinations the public Internet had no route to at all?
- Sketch what the real MCLAG peer link between `sw1` and `sw2` would need, beyond the addressed interface this lab gave it, to actually behave like one logical switch to a downstream device.
- A third upstream is added, an AS representing a direct peering arrangement with one large content provider, advertising only that provider's own prefixes (no default, no broad table). Should it be filtered like `rtr1` (default-only) or like `rtr2` (everything-but-default), and why does neither quite fit?
- You wrote the IPv6 policy by mechanically translating the IPv4 one, line for line. Look back at Step 5's question about `le 32` versus `le 128`. What general risk does "translate the syntax, keep the numbers" carry that "understand the intent, rebuild the numbers" doesn't?
