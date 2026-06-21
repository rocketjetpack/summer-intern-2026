---
title: "Lab 0: Build nettools:week04"
---

# Lab 0: Build nettools:week04

The `nettools:week03` image from the Docker lab includes `iproute2`, `ping`, and `tcpdump` — sufficient for Week 3's routing and switching labs. Week 4 needs one additional tool:

- **`iperf3`** — measures TCP/UDP throughput between two hosts; used in Lab 1 to observe how congestion and loss affect achievable bandwidth.

This build also fixes a limitation in the `nettools:week03` entrypoint. The original `entrypoint.sh` always blocks on `tail -f /dev/null`, which means `docker run --rm nettools:week03 <command>` never returns — the entrypoint ignores whatever command you pass. The fix is the standard `exec "$@"` pattern: if arguments are provided, execute them; otherwise fall back to the keep-alive tail.

---

## Step 1: Create the build directory

```bash
mkdir -p $HOME/container-lab/week04/image
cd $HOME/container-lab/week04/image
```

## Step 2: Write the entrypoint

The existing nettools container from week 3 cannot accept arbitrary commands at startup time. Let's fix this by creating a new entrypoint.sh script for the updated container. 

```bash
#!/bin/bash
# entrypoint.sh
lldpd
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    exec tail -f /dev/null
fi
```

```bash
chmod +x entrypoint.sh
```

When this container is run it will launch `lldpd` in the background, then either execute a supplied command or start an endless tail process to ensure the container does not exit until the user specifically stops it through `docker stop`.

## Step 3: Write the Dockerfile

```dockerfile
# Dockerfile
FROM nettools:week03

RUN apk add --no-cache iperf3

COPY entrypoint.sh /entrypoint.sh
```

Copying `entrypoint.sh` over the existing one is enough — the `ENTRYPOINT` instruction in week03's Dockerfile already points to `/entrypoint.sh`, so no change to that line is needed.

## Step 4: Build and tag the image

```bash
docker build -t nettools:week04 .
```

## Step 5: Verify

```bash
docker run --rm nettools:week04 iperf3 --version
docker run --rm nettools:week04 ip -V
docker run --rm nettools:week04 tcpdump --version
```

Each command should print version information and return immediately. If any command hangs instead of returning, the entrypoint was not replaced correctly — confirm `entrypoint.sh` is in the same directory as the Dockerfile and re-run the build.
