#!/usr/bin/env python3
"""
Generate Part 1 of Week 9 Lab 2 ("Selective Route Acceptance at a Dual-Edge
Boundary"): the mentor-operated infrastructure the intern peers with but
never configures.

Produces, under ./build/:
  - daemons                    (shared FRR daemons file, bgpd=yes)
  - isp1-frr.conf, isp2-frr.conf, rtr1-frr.conf, rtr2-frr.conf
  - part1.clab.yml             (containerlab topology, incl. bridge nodes)
  - ADDRESSING.md              (the address/ASN table to cross-check against
                                 src/week_09/lab2.md before publishing)

Topology: isp1 (public Internet, full table) feeds rtr1; isp2 (Internet2,
a real subset of isp1's routes) feeds rtr2. rtr1 and rtr2 both relay
EVERYTHING they learn, unfiltered, to both of the intern's switches
(sw1/sw2, built in Part 2) via two shared host bridges. Nothing here
performs any outbound filtering: the entire point is that the intern must
construct her own acceptance policy rather than receive an already-curated
feed. Without that policy, both switches would see the same ~250 overlapping
prefixes twice (once via each router) and two competing default routes,
arbitrated only by BGP's own tiebreakers rather than by design.

The ~500/~250 "full table" prefixes are synthetic, drawn from two
IANA/IETF-reserved, non-Internet-routable blocks so nothing here can
collide with or be mistaken for a real route:
  - IPv4: 198.18.0.0/15   (RFC 2544, benchmarking)
  - IPv6: 2001:2::/48     (RFC 5180, benchmarking)

Only the Python 3 standard library is used (ipaddress, random, dataclasses,
pathlib). Verified against Python 3.12; confirm `python3 --version` on the
actual lab host before running there, since that has not been checked from
this environment.
"""

from __future__ import annotations

import ipaddress
import random
from dataclasses import dataclass
from pathlib import Path

SEED = 90900          # fixed seed: regenerating produces the identical table
V4_BLOCK = ipaddress.ip_network("198.18.0.0/15")
V6_BLOCK = ipaddress.ip_network("2001:2::/48")
V4_TARGET = 500
V6_TARGET = 500
SUBSET_FRACTION = 0.5  # isp2's routes are exactly half of isp1's, by value

# Weighted toward /24 so ~500 prefixes fit inside the /15 (131072 addresses)
# with headroom for the bump allocator's alignment waste: expected
# consumption is ~105,000 addresses (80% of capacity) at these weights.
V4_LENGTH_WEIGHTS = {24: 60, 25: 22, 26: 10, 27: 5, 23: 2, 22: 1}
# A /48 has 2**80 addresses in absolute terms, but that intuition is
# misleading close to the block's own prefix length: a /50 is only 4 bits
# longer than /48, so just 4 of them exist in the whole block. Lengths here
# are kept at /56 or longer (>= 8 bits inside the block) so ~500 prefixes
# use well under half the available /64-equivalent space (~26,500 of 65,536).
V6_LENGTH_WEIGHTS = {56: 15, 58: 15, 60: 25, 62: 20, 64: 25}

OUT = Path(__file__).parent / "build"

FRR_IMAGE = "quay.io/frrouting/frr:10.6.1"


@dataclass
class Node:
    name: str
    asn: int
    router_id: str
    loop6: str
    loop4: str


NODES = {
    "isp1": Node("isp1", 64503, "10.9.0.1", "2001:db8:9:0::1/128", "192.0.2.1/32"),
    "isp2": Node("isp2", 64504, "10.9.0.2", "2001:db8:9:0::2/128", "192.0.2.2/32"),
    "rtr1": Node("rtr1", 64505, "10.9.0.3", "2001:db8:9:0::3/128", "192.0.2.3/32"),
    "rtr2": Node("rtr2", 64506, "10.9.0.4", "2001:db8:9:0::4/128", "192.0.2.4/32"),
    # sw1/sw2 (AS 64500, reused from Lab 1's rtr-org) are NOT generated here:
    # the intern builds and addresses them in Part 2. Their bridge-segment
    # addresses are fixed below only because rtr1/rtr2's pre-written
    # configs need to know what to expect.
}

# isp-to-rtr point-to-point links: global /127 (v6) and /30 (v4).
P2P_LINKS = [
    # (isp_name, rtr_name, if, v6_net, v4_net)
    ("isp1", "rtr1", "eth1", "2001:db8:9:f1::/127", "198.51.100.0/30"),
    ("isp2", "rtr2", "eth1", "2001:db8:9:f2::/127", "198.51.100.4/30"),
]

# Bridge segments: each rtr's downstream-facing interface, plus the two
# addresses reserved for sw1/sw2 (assigned by the intern in Part 2, but
# fixed here so rtr1/rtr2's neighbor statements can be pre-written).
BRIDGE_SEGMENTS = {
    "br-w9l2-r1": {
        "router": "rtr1", "router_if": "eth2",
        "v6_net": "2001:db8:9:f5::/125", "v4_net": "198.51.100.16/29",
        "router_v6": "2001:db8:9:f5::1", "router_v4": "198.51.100.17",
        "sw1_v6": "2001:db8:9:f5::2", "sw1_v4": "198.51.100.18",
        "sw2_v6": "2001:db8:9:f5::3", "sw2_v4": "198.51.100.19",
    },
    "br-w9l2-r2": {
        "router": "rtr2", "router_if": "eth2",
        "v6_net": "2001:db8:9:f6::/125", "v4_net": "198.51.100.24/29",
        "router_v6": "2001:db8:9:f6::1", "router_v4": "198.51.100.25",
        "sw1_v6": "2001:db8:9:f6::2", "sw1_v4": "198.51.100.26",
        "sw2_v6": "2001:db8:9:f6::3", "sw2_v4": "198.51.100.27",
    },
}

SW_ASN = 64500

DEFAULT4_STATIC = "0.0.0.0/0"
DEFAULT6_STATIC = "::/0"

DAEMONS = """# daemons -- BGP only (Week 9 Lab 2, Part 1)
zebra=yes
bgpd=yes
vtysh_enable=yes

ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no
pimd=no
ldpd=no
nhrpd=no
eigrpd=no
babeld=no
sharpd=no
staticd=no
pbrd=no
bfdd=no
fabricd=no
"""


# ---------------------------------------------------------------------------
# Prefix generation: a bump allocator walks the block from its start,
# aligning each new prefix to its own length boundary. No randomness in
# placement (avoids fragmentation waste); randomness only picks each
# prefix's length, from the weighted table, seeded for reproducibility.
# ---------------------------------------------------------------------------

def weighted_lengths(weights: dict[int, int], count: int, rng: random.Random) -> list[int]:
    lengths, wts = zip(*weights.items())
    return rng.choices(lengths, weights=wts, k=count)


def bump_allocate(block, lengths: list[int]) -> list:
    result = []
    cursor = int(block.network_address)
    block_end = int(block.broadcast_address)
    for length in lengths:
        size = 1 << (block.max_prefixlen - length)
        aligned = (cursor + size - 1) // size * size
        if aligned + size - 1 > block_end:
            continue  # out of room; skip rather than overrun the block
        net = ipaddress.ip_network(f"{ipaddress.ip_address(aligned)}/{length}")
        result.append(net)
        cursor = aligned + size
    return result


def generate_prefixes() -> tuple[list[str], list[str], list[str], list[str]]:
    """Returns (isp1_v4, isp1_v6, isp2_v4, isp2_v6). isp2's lists are an
    exact subset (half the count) of isp1's, not independently generated:
    Internet2-reachable destinations really are also reachable via the
    public Internet, just preferentially routed."""
    rng = random.Random(SEED)
    v4_lengths = weighted_lengths(V4_LENGTH_WEIGHTS, V4_TARGET, rng)
    v6_lengths = weighted_lengths(V6_LENGTH_WEIGHTS, V6_TARGET, rng)
    v4_nets = bump_allocate(V4_BLOCK, v4_lengths)
    v6_nets = bump_allocate(V6_BLOCK, v6_lengths)
    assert sum(n.num_addresses for n in v4_nets) <= V4_BLOCK.num_addresses

    isp1_v4 = [str(n) for n in v4_nets]
    isp1_v6 = [str(n) for n in v6_nets]
    subset_n4 = int(len(isp1_v4) * SUBSET_FRACTION)
    subset_n6 = int(len(isp1_v6) * SUBSET_FRACTION)
    # A deterministic sample (not just the first N, so the subset isn't
    # trivially "the first half of the address space") but seeded, so
    # regenerating is still byte-identical.
    isp2_v4 = sorted(rng.sample(isp1_v4, subset_n4),
                      key=lambda p: int(ipaddress.ip_network(p).network_address))
    isp2_v6 = sorted(rng.sample(isp1_v6, subset_n6),
                      key=lambda p: int(ipaddress.ip_network(p).network_address))
    return isp1_v4, isp1_v6, isp2_v4, isp2_v6


# ---------------------------------------------------------------------------
# Config rendering
# ---------------------------------------------------------------------------

def frr_conf_isp(name: str, peer_name: str, own_if: str, own_v4: str, own_v6: str,
                  peer_v4: str, peer_v6: str, peer_asn: int,
                  v4_prefixes: list[str], v6_prefixes: list[str]) -> str:
    n = NODES[name]
    lines = [
        "frr defaults traditional",
        f"hostname {name}",
        "log stdout informational",
        "!",
        "interface lo",
        f" ip address {n.loop4}",
        f" ipv6 address {n.loop6}",
        "!",
        f"interface {own_if}",
        f" ip address {own_v4}",
        f" ipv6 address {own_v6}",
        "!",
    ]
    for p in v4_prefixes:
        lines.append(f"ip route {p} blackhole")
    lines.append(f"ip route {DEFAULT4_STATIC} blackhole")
    for p in v6_prefixes:
        lines.append(f"ipv6 route {p} blackhole")
    lines.append(f"ipv6 route {DEFAULT6_STATIC} blackhole")
    v4_peer_ip = peer_v4.split("/")[0]
    v6_peer_ip = peer_v6.split("/")[0]
    lines += [
        "!",
        f"router bgp {n.asn}",
        f" bgp router-id {n.router_id}",
        " no bgp ebgp-requires-policy",
        f" neighbor {v4_peer_ip} remote-as {peer_asn}",
        f" neighbor {v6_peer_ip} remote-as {peer_asn}",
        " address-family ipv4 unicast",
        f"  neighbor {v4_peer_ip} activate",
        "  redistribute static",
        f"  network {DEFAULT4_STATIC}",
        " exit-address-family",
        " address-family ipv6 unicast",
        f"  neighbor {v6_peer_ip} activate",
        "  redistribute static",
        f"  network {DEFAULT6_STATIC}",
        " exit-address-family",
        "!",
    ]
    return "\n".join(lines)


def frr_conf_rtr(name: str, isp_link: dict, bridge_key: str) -> str:
    n = NODES[name]
    seg = BRIDGE_SEGMENTS[bridge_key]
    lines = [
        "frr defaults traditional",
        f"hostname {name}",
        "log stdout informational",
        "!",
        "interface lo",
        f" ip address {n.loop4}",
        f" ipv6 address {n.loop6}",
        "!",
        f"interface {isp_link['if']}",
        f" ip address {isp_link['own_v4']}",
        f" ipv6 address {isp_link['own_v6']}",
        "!",
        f"interface {seg['router_if']}",
        f" ip address {seg['router_v4']}/29",
        f" ipv6 address {seg['router_v6']}/125",
        "!",
        f"router bgp {n.asn}",
        f" bgp router-id {n.router_id}",
        " no bgp ebgp-requires-policy",
        f" neighbor {isp_link['peer_v4']} remote-as {isp_link['peer_asn']}",
        f" neighbor {isp_link['peer_v6']} remote-as {isp_link['peer_asn']}",
        f" neighbor {seg['sw1_v4']} remote-as {SW_ASN}",
        f" neighbor {seg['sw1_v6']} remote-as {SW_ASN}",
        f" neighbor {seg['sw2_v4']} remote-as {SW_ASN}",
        f" neighbor {seg['sw2_v6']} remote-as {SW_ASN}",
        " address-family ipv4 unicast",
        f"  neighbor {isp_link['peer_v4']} activate",
        f"  neighbor {seg['sw1_v4']} activate",
        f"  neighbor {seg['sw2_v4']} activate",
        " exit-address-family",
        " address-family ipv6 unicast",
        f"  neighbor {isp_link['peer_v6']} activate",
        f"  neighbor {seg['sw1_v6']} activate",
        f"  neighbor {seg['sw2_v6']} activate",
        " exit-address-family",
        "!",
    ]
    # Deliberately no outbound filtering anywhere in this config: rtr1/rtr2
    # relay everything they learn to both switches, unfiltered. Constructing
    # the acceptance policy is the intern's job in Part 2, not something
    # pre-baked here.
    return "\n".join(lines)


def render_topology() -> None:
    # Bridge-node endpoint names (the part after the colon on a
    # "br-...:name" link) become veth interfaces in the HOST's root
    # network namespace, not inside any container namespace, so they must
    # be unique across the whole host, not just within one bridge's links.
    # Part 2 attaches two more links to each of these same bridges; its
    # endpoint names (w9l2-r{1,2}-sw{1,2}) must stay distinct from these.
    yml = f"""name: week09-lab2-part1
topology:
  nodes:
    isp1:
      kind: linux
      image: {FRR_IMAGE}
      binds:
        - daemons:/etc/frr/daemons
        - isp1-frr.conf:/etc/frr/frr.conf
    isp2:
      kind: linux
      image: {FRR_IMAGE}
      binds:
        - daemons:/etc/frr/daemons
        - isp2-frr.conf:/etc/frr/frr.conf
    rtr1:
      kind: linux
      image: {FRR_IMAGE}
      binds:
        - daemons:/etc/frr/daemons
        - rtr1-frr.conf:/etc/frr/frr.conf
    rtr2:
      kind: linux
      image: {FRR_IMAGE}
      binds:
        - daemons:/etc/frr/daemons
        - rtr2-frr.conf:/etc/frr/frr.conf
    br-w9l2-r1:
      kind: bridge
    br-w9l2-r2:
      kind: bridge
  links:
    - endpoints: ["isp1:eth1", "rtr1:eth1"]
    - endpoints: ["isp2:eth1", "rtr2:eth1"]
    - endpoints: ["rtr1:eth2", "br-w9l2-r1:w9l2-r1-rtr1"]
    - endpoints: ["rtr2:eth2", "br-w9l2-r2:w9l2-r2-rtr2"]
"""
    (OUT / "part1.clab.yml").write_text(yml)


def render_addressing_doc(isp1_v4, isp1_v6, isp2_v4, isp2_v6) -> None:
    lines = [
        "# Week 9 Lab 2, Part 1: generated addressing",
        "",
        f"Generated with SEED={SEED}. isp1 (public Internet): "
        f"{len(isp1_v4)} IPv4 / {len(isp1_v6)} IPv6 + default. "
        f"isp2 (Internet2): {len(isp2_v4)} IPv4 / {len(isp2_v6)} IPv6 + "
        "default, an exact subset of isp1's routes.",
        "",
        "Source blocks: 198.18.0.0/15 (RFC 2544) and 2001:2::/48 (RFC 5180).",
        "",
        "Cross-check every value below against src/week_09/lab2.md before",
        "publishing; if they diverge, this file is correct (it's what was",
        "actually deployed).",
        "",
        "## ASNs and router IDs",
        "",
        "| Node | ASN | Router ID |",
        "|---|---|---|",
    ]
    for name, n in NODES.items():
        lines.append(f"| {name} | {n.asn} | {n.router_id} |")
    lines.append(f"| sw1 / sw2 (intern-built) | {SW_ASN} | intern's choice |")
    lines += ["", "## Bridge segments (Part 2 hand-off points)", ""]
    for br, seg in BRIDGE_SEGMENTS.items():
        lines += [
            f"### {br}",
            f"- v4: `{seg['v4_net']}`. {seg['router']} `{seg['router_v4']}`, sw1 `{seg['sw1_v4']}`, sw2 `{seg['sw2_v4']}`",
            f"- v6: `{seg['v6_net']}`. {seg['router']} `{seg['router_v6']}`, sw1 `{seg['sw1_v6']}`, sw2 `{seg['sw2_v6']}`",
            "",
        ]
    (OUT / "ADDRESSING.md").write_text("\n".join(lines))


def build() -> None:
    OUT.mkdir(exist_ok=True)
    isp1_v4, isp1_v6, isp2_v4, isp2_v6 = generate_prefixes()

    (OUT / "daemons").write_text(DAEMONS)
    (OUT / "isp1-v4-routes.txt").write_text("\n".join(isp1_v4) + "\n")
    (OUT / "isp1-v6-routes.txt").write_text("\n".join(isp1_v6) + "\n")
    (OUT / "isp2-v4-routes.txt").write_text("\n".join(isp2_v4) + "\n")
    (OUT / "isp2-v6-routes.txt").write_text("\n".join(isp2_v6) + "\n")

    isp1_link = P2P_LINKS[0]
    isp2_link = P2P_LINKS[1]

    def link_addrs(link):
        _, _, _, v6_net, v4_net = link
        v6n = ipaddress.ip_network(v6_net)
        v4n = ipaddress.ip_network(v4_net)
        isp_v6, rtr_v6 = v6n[0], v6n[1]
        hosts4 = list(v4n.hosts())
        isp_v4, rtr_v4 = hosts4[0], hosts4[1]
        return isp_v4, isp_v6, rtr_v4, rtr_v6

    isp1_v4a, isp1_v6a, rtr1_v4a, rtr1_v6a = link_addrs(isp1_link)
    (OUT / "isp1-frr.conf").write_text(frr_conf_isp(
        "isp1", "rtr1", "eth1", f"{isp1_v4a}/30", f"{isp1_v6a}/127",
        f"{rtr1_v4a}/30", f"{rtr1_v6a}/127", NODES["rtr1"].asn, isp1_v4, isp1_v6))

    isp2_v4a, isp2_v6a, rtr2_v4a, rtr2_v6a = link_addrs(isp2_link)
    (OUT / "isp2-frr.conf").write_text(frr_conf_isp(
        "isp2", "rtr2", "eth1", f"{isp2_v4a}/30", f"{isp2_v6a}/127",
        f"{rtr2_v4a}/30", f"{rtr2_v6a}/127", NODES["rtr2"].asn, isp2_v4, isp2_v6))

    rtr1_isp_link = {
        "if": "eth1", "own_v4": f"{rtr1_v4a}/30", "own_v6": f"{rtr1_v6a}/127",
        "peer_v4": str(isp1_v4a), "peer_v6": str(isp1_v6a), "peer_asn": NODES["isp1"].asn,
    }
    rtr2_isp_link = {
        "if": "eth1", "own_v4": f"{rtr2_v4a}/30", "own_v6": f"{rtr2_v6a}/127",
        "peer_v4": str(isp2_v4a), "peer_v6": str(isp2_v6a), "peer_asn": NODES["isp2"].asn,
    }
    (OUT / "rtr1-frr.conf").write_text(frr_conf_rtr("rtr1", rtr1_isp_link, "br-w9l2-r1"))
    (OUT / "rtr2-frr.conf").write_text(frr_conf_rtr("rtr2", rtr2_isp_link, "br-w9l2-r2"))

    render_topology()
    render_addressing_doc(isp1_v4, isp1_v6, isp2_v4, isp2_v6)

    print(f"isp1: {len(isp1_v4)} IPv4 / {len(isp1_v6)} IPv6 + default")
    print(f"isp2: {len(isp2_v4)} IPv4 / {len(isp2_v6)} IPv6 + default "
          f"(exact subset of isp1)")
    print(f"Output written to {OUT}/")


if __name__ == "__main__":
    build()
