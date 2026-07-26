# Week 9 Lab 2, Part 1: mentor setup

This is operational tooling, not curriculum content. It builds and deploys
the "given" infrastructure for `src/week_09/lab2.md`: two upstream feeds and
two edge routers, all pre-configured, which the intern's own `sw1`/`sw2`
peer with in Part 2. The intern never sees this directory or its output;
they only see the two host bridges' addresses, published in `lab2.md`'s
addressing table.

Not published to the site: everything here lives outside `src/`, so
Observable Framework never builds it into a page.

## What gets built, and why it's shaped this way

- `isp1` (AS 64503): the public Internet. Originates 500 IPv4 + 500 IPv6
  synthetic routes plus a default, feeding `rtr1` (AS 64505).
- `isp2` (AS 64504): Internet2. Originates 250 IPv4 + 250 IPv6 routes plus
  a default, feeding `rtr2` (AS 64506). Those 250+250 are an **exact
  subset** of isp1's routes, not an independently generated set: this
  mirrors reality, since R&E institutions reachable via Internet2 are also
  reachable via the public Internet, just preferentially routed.
- `rtr1` and `rtr2` each relay **everything** they learn, unfiltered, to
  **both** of the intern's switches. There is no outbound filtering
  anywhere in this Part 1 configuration, deliberately: the entire point of
  the lab is that the intern must construct her own acceptance policy
  rather than receive an already-curated feed. Left unfiltered, both
  switches will see the 250 overlapping prefixes twice (once via each
  router) and two competing default routes, with no say from anyone over
  which one BGP's own tiebreakers happen to prefer. That's the mess the
  intern's policy work in Part 2 resolves on purpose.
- `rtr1`/`rtr2` each face a host Linux bridge (`br-w9l2-r1`,
  `br-w9l2-r2`) instead of a directly wired container: the hand-off point
  where the intern's own, separately-deployed `sw1`/`sw2` topology attaches
  later. Confirmed via the containerlab docs that a `kind: bridge` node
  attaches to a pre-existing host bridge and that independently-deployed
  topologies can share one; this isn't a workaround, it's the documented
  way to link two labs.
- Both `rtr1` and `rtr2` connect to **both** switches (a full mesh, not a
  single-homed pair), matching the production design this lab mirrors:
  whichever switch traffic lands on, it has a direct, local route to both
  the public-Internet default and the Internet2 specifics, without needing
  to transit its MCLAG peer switch first.
- The ~500/~250 routes are synthetic, drawn from two IANA/IETF-reserved,
  non-Internet-routable blocks so nothing here can be confused with a real
  route: **198.18.0.0/15** ([RFC 2544](https://www.rfc-editor.org/rfc/rfc2544.html),
  benchmarking) for IPv4, **2001:2::/48**
  ([RFC 5180](https://www.rfc-editor.org/rfc/rfc5180.html), benchmarking)
  for IPv6.

The `no bgp ebgp-requires-policy` shortcut appears on every session in this
Part 1 configuration, the same one Lab 1 introduces and names explicitly as
a lab-only convenience. That's deliberate here too: these four boxes are
trusted mentor-operated plumbing the intern never configures, so nothing
here is a policy lesson being skipped, only sidestepped where it isn't
meant to be seen. All of the actual policy work is Part 2's job.

## Prerequisites

- `docker` and `containerlab` on the lab host (same as every other lab in
  this program).
- `python3`: confirm with `python3 --version` on the **lab host**
  specifically. This was only verified locally in the planning environment
  (3.12.3, stdlib only); it has not been checked on the actual lab host.
- Root or `sudo` for bridge creation.

## Step 1: Generate the configuration

```bash
cd ops/week09-lab2-part1
python3 generate.py
```

This writes everything below to `./build/` (git-ignored; rerun any time,
the output is deterministic: same seed, same routes, byte-identical):

- `daemons`, `isp1-frr.conf`, `isp2-frr.conf`, `rtr1-frr.conf`,
  `rtr2-frr.conf`
- `part1.clab.yml`: the containerlab topology, including the two bridge
  nodes
- `isp1-v4-routes.txt` / `isp1-v6-routes.txt` / `isp2-v4-routes.txt` /
  `isp2-v6-routes.txt`: the generated prefix lists, useful for spot-checking
  (e.g. confirming isp2's set really is a subset, or picking a shared
  prefix to demonstrate the pre-policy overlap with)
- `ADDRESSING.md`: every ASN, router ID, and bridge-segment address the
  script assigned. **This is the source of truth.** If anything here
  disagrees with `src/week_09/lab2.md`'s published addressing table, this
  file is right and the lab page needs a fix before it can be safely
  published.

## Step 2: Create the host bridges

Containerlab does not create bridges itself; they must exist before deploy:

```bash
sudo ip link add br-w9l2-r1 type bridge
sudo ip link set br-w9l2-r1 up
sudo ip link add br-w9l2-r2 type bridge
sudo ip link set br-w9l2-r2 up
```

Important gotcha, confirmed against the containerlab docs after hitting it
directly: for a `kind: bridge` node, the name after the colon in a link
endpoint (e.g. `br-w9l2-r1:w9l2-r1-rtr1`) is **not** an interface inside
some container's namespace. A bridge node has no container namespace at
all; that name becomes a veth interface created directly in the **host's
root network namespace**. That means it must be unique across the entire
host, not just within one bridge's own links, and reusing something generic
like `eth1` on two different bridge nodes in the same deploy fails with
`Root network namespace endpoint "eth1" defined by multiple nodes [...]`.
`generate.py` already names these `w9l2-r1-rtr1` / `w9l2-r2-rtr2`, and
Part 2's `sw1`/`sw2` topology uses `w9l2-r1-sw{1,2}` / `w9l2-r2-sw{1,2}`;
if this topology is ever extended with another link onto either bridge,
give it its own globally-unique name, not `eth1`/`eth2`/`eth3`. It's also
worth a quick `ip link show` before first deploy if this lab host runs
other persistent bridges or containerlab topologies, in case one of them
already holds one of these six names.

## Step 3: Deploy

```bash
cd build
containerlab deploy -t part1.clab.yml
```

Give it a minute, then confirm both edge routers are receiving what they
should from their upstreams:

```bash
docker exec -it clab-week09-lab2-part1-rtr1 vtysh -c 'show bgp ipv4 unicast summary'
docker exec -it clab-week09-lab2-part1-rtr2 vtysh -c 'show bgp ipv4 unicast summary'
```

`rtr1` should show ~500 prefixes from `isp1`; `rtr2` should show ~250 from
`isp2`. The `rtr1`/`rtr2` neighbor statements toward `sw1`/`sw2` are already
written and waiting; they'll simply stay in `Active` until the intern's own
Part 2 deploy brings `sw1`/`sw2` up against the same bridges.

## Step 4: Leave it running

Unlike every other lab in this program, Part 1 is meant to be deployed once
and left up for the whole time the intern is working through Part 2 (and
potentially across multiple interns/cohorts, since it's read-only from
their side). There is no "Step 5: clean up" here for lab-session hygiene;
`containerlab destroy -t part1.clab.yml --cleanup` only when actually
decommissioning it. Note the containerlab docs' cleanup caveat: destroying
the lab does **not** remove `iptables` FORWARD-chain rules it added; manual
`iptables` cleanup if this host's `iptables` state needs to stay tidy
afterward.

## Before publishing `lab2.md`

1. Confirm the upstream sessions in Step 3.
2. Cross-check `build/ADDRESSING.md` line-for-line against `lab2.md`'s
   addressing table.
3. Deploy Part 2 (the intern's own topology, `src/week_09/lab2.md`) against
   this running Part 1 and confirm the full lab, end to end, including the
   pre-policy overlap the intern is meant to observe before writing her
   acceptance policy, before uncommenting the Lab 2 sidebar entry in
   `observablehq.config.js`.
