---
title: "Lab 0: Prepare the FRR Router Image"
---

# Lab 0: Prepare the FRR Router Image

There is nothing to build this week. The BGP labs' routers use the official FRRouting container image as-is; this lab pulls that image, verifies it, and writes the one configuration file that controls what it runs. If you already worked through the OSPFv3 stretch topic, you have seen this image before and this will take five minutes; the daemons file here differs by exactly the line that topic foreshadowed.

---

## Step 1: Pull and pin the FRR image

```bash
docker pull quay.io/frrouting/frr:10.6.1
```

The tag is pinned deliberately, the same practice as the `goflow2` version pin in [Week 5's Lab 0](../week_05/lab0). `10.6.1` remains a current stable release; if the pull fails or you want to check what has been published since, the tag list is at [quay.io/repository/frrouting/frr](https://quay.io/repository/frrouting/frr?tab=tags). Avoid `master`: lab instructions and dev builds drift apart. FRR is also the routing software the production deployment pairs with the Juniper gear in Week 10, so time spent in its CLI now is paid back directly.

## Step 2: Verify

```bash
docker run --rm quay.io/frrouting/frr:10.6.1 zebra --version
docker run --rm quay.io/frrouting/frr:10.6.1 bgpd --version
```

Both should print FRR version information and return immediately.

## Step 3: Understand what you just pulled

FRR is not one program. It's a suite of cooperating daemons:

- **`zebra`** is the kernel liaison. Every routing daemon hands its routes to zebra, and zebra arbitrates (by administrative distance) what gets installed into the kernel's forwarding table. It is the RIB-to-FIB step from the [Basics page](../week_08/objectives), running as an actual process you can observe.
- **One daemon per routing protocol**: `bgpd` speaks BGP, `ospf6d` speaks OSPFv3, `isisd` speaks IS-IS, and so on. Each maintains its own protocol state and feeds candidate routes to zebra. This week wakes up `bgpd`.
- **`vtysh`** is the unified CLI shell fronting all of them at once. Its prompt, its `configure` mode, and its `?`-completion are the dialect ancestor of the Juniper CLI you'll meet in Week 10.

Which daemons actually start is controlled by `/etc/frr/daemons`, a plain file of `name=yes|no` lines read at container start. The image ships with everything off; each lab bind-mounts its own copy in. This week's version:

```
# daemons -- BGP only
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
```

Save it where [Lab 1](./lab1) expects to find it:

```bash
mkdir -p $HOME/container-lab/week09
cd $HOME/container-lab/week09
# write the daemons file above into $HOME/container-lab/week09/daemons
```

One line deserves the pause: `bgpd=yes`. Everything else about how these containers run (the image, the bind-mount, zebra's arbitration) is unchanged from any other FRR deployment; the entire difference between "an OSPF router" and "a BGP router" is which daemon wakes up. The routing suite is a toolbox, and protocols are the tools.

## Step 4: Confirm the kernel prerequisites

BGP needs nothing exotic from the kernel: TCP and IPv6, and the labs enable per-container IPv6 forwarding from the topology file. The one thing worth confirming on the ContainerLab host is that IPv6 hasn't been administratively disabled:

```bash
sysctl net.ipv6.conf.default.disable_ipv6
```

A value of `0` means IPv6 is available (the double negative is the kernel's, not ours). If it prints `1`, resolve that with the lab host's administrator before deploying Lab 1.
