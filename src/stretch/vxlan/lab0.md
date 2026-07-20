---
title: "Lab 0: Build nettools:vxlan"
---

# Lab 0: Build nettools:vxlan

Good news: `nettools:week05` already has everything this topic's core mechanism needs. Alpine's `iproute2` package bundles both the VXLAN netlink interface (`ip link add type vxlan`) and the `bridge` command (`bridge fdb`, `bridge link`) in the same package that's been present since [Week 3](../../week_03/objectives); no new packages are required. `tcpdump`, present since the same week, decodes the VXLAN header natively.

This build adds one small convenience script and, more importantly, a **preflight check that belongs on the ContainerLab host itself, not in the image**.

---

## Step 1: Check the host kernel first

VXLAN's `ip link add type vxlan` support comes from the Linux kernel's `vxlan` driver, which every container on a host shares. This is not something a Docker image can provide on its own; the same way `nettools:week04`'s `tc netem` labs depended on the host kernel's queueing-discipline support. Run this directly on the ContainerLab host **before** building anything:

```bash
lsmod | grep vxlan || sudo modprobe vxlan
```

If `modprobe vxlan` fails outright, the running kernel wasn't built with VXLAN support at all, and Lab 1 can't proceed until that's resolved. Check with whoever administers the lab host rather than assuming it's a container-side problem.

## Step 2: Create the build directory

```bash
mkdir -p $HOME/container-lab/stretch-vxlan/image
cd $HOME/container-lab/stretch-vxlan/image
```

## Step 3: Write the helper script

`vxlan-status.sh` is a small diagnostic wrapper Lab 1 will use repeatedly to check a VTEP's state in one shot, rather than typing three separate commands every time:

```bash
#!/bin/sh
# vxlan-status.sh
echo "== VXLAN interfaces =="
ip -d link show type vxlan
echo
echo "== Bridge FDB entries =="
bridge fdb show
echo
echo "== Bridge port membership =="
bridge link show
```

```bash
chmod +x vxlan-status.sh
```

## Step 4: Write the Dockerfile

```dockerfile
# Dockerfile
FROM nettools:week05

COPY vxlan-status.sh /usr/local/bin/vxlan-status.sh
```

## Step 5: Build and tag the image

```bash
docker build -t nettools:vxlan .
```

## Step 6: Verify

```bash
docker run --rm nettools:vxlan which bridge
docker run --rm nettools:vxlan which vxlan-status.sh
docker run --rm --cap-add=NET_ADMIN nettools:vxlan ip link add test100 type vxlan id 100 dstport 4789 2>&1
```

The first two commands should print a path and return immediately. The third actually attempts to create a VXLAN interface; `--cap-add=NET_ADMIN` is required here because a bare `docker run` doesn't grant it by default, whereas ContainerLab's `linux` kind does (the same reason `sysctl -w net.ipv4.ip_forward=1` worked without extra flags in [Week 5](../../week_05/lab1)). If this command errors with something other than "already exists" on a repeat run, revisit Step 1. It almost always means the host kernel's `vxlan` module isn't actually loaded, not a container-side problem.
