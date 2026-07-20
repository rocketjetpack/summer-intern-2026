---
title: "Lab 0: Prepare the FRR Router Image"
---

# Lab 0: Prepare the FRR Router Image

This Lab 0 is different from the weekly image builds: there is nothing to build. The OSPFv3 lab's routers use the official FRRouting container image as-is. What this lab does instead is pull that image, verify it, and introduce the one configuration file that controls what it runs: the `daemons` file.

---

## Step 1: Pull and pin the FRR image

```bash
docker pull quay.io/frrouting/frr:10.6.1
```

The tag is pinned deliberately, the same practice as the `goflow2` version pin in [Week 5's Lab 0](../../week_05/lab0). `10.6.1` is the current stable release as of early July 2026; if the pull fails or you want to check for a newer stable, the tag list is at [quay.io/repository/frrouting/frr](https://quay.io/repository/frrouting/frr?tab=tags). Avoid `master`: lab instructions and dev builds drift apart.

## Step 2: Verify

```bash
docker run --rm quay.io/frrouting/frr:10.6.1 zebra --version
docker run --rm quay.io/frrouting/frr:10.6.1 ospf6d --version
```

Both should print FRR version information and return immediately.

## Step 3: Understand what you just pulled

FRR is not one program. It's a suite of cooperating daemons:

- **`zebra`** is the kernel liaison. Every other daemon hands its routes to zebra, and zebra decides what gets installed into the kernel's forwarding table. It is the RIB-to-FIB step from this topic's [Objectives](./objectives), running as an actual process you can observe.
- **One daemon per routing protocol**: `ospf6d` speaks OSPFv3, `ospfd` speaks OSPFv2, `bgpd` speaks BGP, `isisd` speaks IS-IS, and so on. Each maintains its own protocol state and feeds candidate routes to zebra.
- **`vtysh`** is the unified CLI shell that fronts all of them at once, so `show ipv6 ospf6 neighbor` and (next month) `show bgp summary` live in one place.

Which daemons actually start is controlled by `/etc/frr/daemons`, a plain file of `name=yes|no` lines read at container start. The image ships with everything off; each lab bind-mounts its own copy in. This topic's version enables exactly what OSPFv3 needs:

```
# daemons -- OSPFv3 only
zebra=yes
ospf6d=yes
vtysh_enable=yes

bgpd=no
ospfd=no
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
```

Save this as `daemons` now, where [Lab 1](./lab1) expects to find it:

```bash
mkdir -p $HOME/container-lab/stretch-ospfv3
cd $HOME/container-lab/stretch-ospfv3
# write the daemons file above into $HOME/container-lab/stretch-ospfv3/daemons
```

Two lines in that file are worth a second look before moving on:

- **`bgpd=no`** is this program's whole trajectory compressed into one line. The BGP weeks flip it to `yes`, on this same image, in this same kind of file. The routing suite doesn't change; only which of its daemons is awake.
- **`bfdd=no`** is the BFD liveness daemon mentioned in the objectives' failure-detection discussion. It stays off here so that Lab 1 can demonstrate what hello/dead timers do unassisted, which is exactly the gap BFD exists to close.

## Step 4: Confirm the kernel prerequisites

Unlike the VXLAN stretch topic's kernel-module concerns, OSPFv3 needs nothing exotic: IPv6 and multicast support, enabled by default on any modern kernel. The one thing worth confirming on the ContainerLab host is that IPv6 hasn't been administratively disabled:

```bash
sysctl net.ipv6.conf.default.disable_ipv6
```

A value of `0` means IPv6 is available (the double negative is the kernel's, not ours). If it prints `1`, resolve that with the lab host's administrator before deploying Lab 1; per-container forwarding sysctls are handled inside the topology file and need nothing from you here.
