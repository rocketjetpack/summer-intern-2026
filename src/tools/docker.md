---
title: Docker Lab
---

# Docker Lab

Containerlab (Week 3) runs every node in your topology as a Docker container, and the Podman lab reuses almost the same commands. This lab builds the mental model you'll need for both — and ends with you building the custom host image that Labs 1-3 use for every Linux node in their topologies.

**This lab should be done on the lab host configured for you to have privileged access to.**

## What is a container, and why do they exist?

A **container** is an isolated process: its own filesystem, network namespace, and process tree, but running directly on the host's kernel — no hypervisor, no separate guest OS. That's the key difference from a VM, which virtualizes an entire machine (its own kernel, boot process, etc.) and is correspondingly heavier and slower to start.

Containers exist to solve "works on my machine": an **image** bundles an application together with everything it needs (libraries, config, a base OS filesystem), so it behaves the same on your laptop, the lab server, and production. For this internship, that means a `.clab.yml` topology can describe *exactly* what software each emulated device runs, and `containerlab deploy` reproduces it identically every time — no manual setup steps to forget.

See [What is a container? (Docker Docs)](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) for a short visual explanation.

## Images vs. containers

- An **image** is a read-only template — a filesystem plus metadata (what to run, as what user, etc.).
- A **container** is a running (or stopped) instance of an image — its own process, filesystem, and network namespace.

## Run your first container

Start an interactive shell inside a minimal Linux image:

```bash
docker run -it --rm alpine sh
```

Poke around (`ip addr`, `cat /etc/os-release`, `ps aux`), then `exit`. The `--rm` flag cleans the container up automatically when it exits — without it, `docker ps -a` would still show it as `Exited`.

Notice that once you `exit`, the container is gone. That's fine for a one-off shell, but every node in a Containerlab topology needs to keep running so you can come back to it — which brings us to:

## Enter a running container

Start a container *detached* (in the background), keeping it alive with a command that never exits:

```bash
docker run -d --name scratch alpine tail -f /dev/null
```

`docker ps` now shows `scratch` as `Up`. Get a shell inside it with `exec`:

```bash
docker exec -it scratch sh
```

`exec` starts a *new* process inside the container's existing namespaces — the container keeps running when you exit that shell (compare to `docker run -it --rm`, where exiting the shell stops and removes the whole container). This is exactly how you'll interact with running Containerlab nodes: `containerlab deploy` starts them all detached, and you `docker exec` (or `containerlab exec`) into whichever one you need.

Clean up: `docker stop scratch && docker rm scratch`.

Verify the container has been removed with `docker ps -a` (the list should be empty).

*In case you aren't familiar with `&&` in bash, it essentially says "run the first command, and if it succeeds then run the next command too.*

## Container networking — bridges as broadcast domains

*Truly understanding container networking is a long road. This step is here so that you understand the fundamental idea of Docker networks and what ContainerLab does to virtually connect devices.*

This is the part that connects directly back to Week 3's "interface" and "link" definitions.

1. Create a user-defined network: `docker network create lab-net`.
2. Start two containers attached to it:
  - `docker run -dit --name c1 --network lab-net alpine sh`  
  - `docker run -dit --name c2 --network lab-net alpine sh`  
3. Exec into a shell in `c1` with `docker exec -it c1 sh`. Run `ping c2` — Docker's embedded DNS resolves container names on the same user-defined network.
4. Run `docker network inspect lab-net` and `docker exec c1 ip addr`. Find each container's IP and its `eth0`.

Each container's `eth0` is one end of a **virtual ethernet pair**; the other end is plugged into a Linux bridge named `lab-net`. That bridge *is* a broadcast domain, just implemented in software. See the [Docker networking overview](https://docs.docker.com/engine/network/) and [bridge network driver docs](https://docs.docker.com/engine/network/drivers/bridge/) for more.

Clean up: `docker rm -f c1 c2 && docker network rm lab-net`.

*Tip: `docker inspect` is a very useful command to understand the runtime state of essentially anything in Docker.*

## Build a moderately customized Alpine network-tools image

Plain `alpine` doesn't ship `ip`, `ping`, `tcpdump`, or `lldpd` — all tools you'll need on the Linux hosts in Labs 1-3. Rather than hunting for a pre-built image with the right combination, build your own.

Write a `Dockerfile`:

```dockerfile
FROM alpine:latest

RUN apk add --no-cache bash iproute2 iputils tcpdump lldpd

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

and an `entrypoint.sh` next to it:

```bash
#!/bin/bash
lldpd
exec tail -f /dev/null
```

Make the `entrypoint.sh` script exectuable with `chmod 755 entrypoint.sh`  

`lldpd` daemonizes itself (forks to the background) and starts advertising LLDP out of every interface. `exec tail -f /dev/null` then becomes the container's foreground process — the same "keep it running" trick from the previous section, now baked into the image itself instead of typed at the command line.

Build and tag it:

```bash
docker build -t nettools:week03 .
```

Test it the same way you tested `scratch` above:

```bash
docker run -d --name nettools-test nettools:week03
docker exec -it nettools-test bash
# inside: ip addr, ping, tcpdump -i eth0, traceroute 1.1.1.1
```

`nettools:week03` is the image **Labs 1-3 use for every Linux host** — reference it as the `image:` for `kind: linux` nodes in those `.clab.yml` files. See the [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) for the full instruction set (`COPY`, `ENV`, `EXPOSE`, etc.) if you want to extend it further.

Clean up: `docker rm -f nettools-test`.

## Persist data with a volume

```bash
docker volume create lab-data
docker run --rm -v lab-data:/data alpine sh -c "echo hello > /data/hello.txt"
docker run --rm -v lab-data:/data alpine cat /data/hello.txt
```

The second container sees the file the first one wrote — the volume outlives any individual container. See the [volumes docs](https://docs.docker.com/engine/storage/volumes/).

Clean up: `docker volume rm lab-data`.

## Clean up

A final sweep, if you want to start fresh before moving on:

```bash
docker ps -a            # anything still around?
docker rm -f <name>     # remove any leftover containers
docker images           # nettools:week03 should still be here — keep it!
```

## Going further

- [Docker Get Started guide](https://docs.docker.com/get-started/) — a fuller walkthrough covering everything above plus Docker Compose.
- [`docker container` CLI reference](https://docs.docker.com/reference/cli/docker/container/) — every container subcommand.
