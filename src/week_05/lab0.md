---
title: "Lab 0: Build nettools:week05"
---

# Lab 0: Build nettools:week05

The `nettools:week04` image already gives every node `iproute2`, `tcpdump`, `lldpd`, and `iperf3`, plus an entrypoint that runs `lldpd` in the background and then `exec`s whatever command you pass it. Week 5 needs that same passthrough behavior where `rtr1` and `collector` both run a long-lived telemetry daemon as their main process. This build only adds packages and a utility script:

- **`hsflowd`** — the sFlow host agent, run on `rtr1` in Lab 1.
- **`softflowd`** — the NetFlow/IPFIX exporter, run on `rtr1` in Lab 2.
- **`nfdump`** (provides `nfcapd` and `nfdump`) — the NetFlow collector/query toolkit, run on `collector` in Lab 2.
- **`goflow2`** — a single binary that decodes sFlow, NetFlow v9, and IPFIX; run on `collector` in Lab 1 (and usable as an alternative to `nfcapd`/`nfdump` in Lab 2 if you'd rather have one tool for both labs).
- **`summarize-flow.py`** — a self-contained Python utility script to summarize flows.

*Note: Some of these packages are available in Alpine packages, but some are not. This weeks Dockerfile includes checking a repo out of GitHub, compiling, and installing software. This is a key milestone in your use of Docker, as you are truly containerizing an application from source and not simply installing packages. Congrats!*

---

## Step 1: Create the build directory

Begin by creating the same general directory structure as you have used before. 

```bash
mkdir -p $HOME/container-lab/week05/image
cd $HOME/container-lab/week05/image
```

## Step 2: Write the Dockerfile

<details>
<summary>Show <code>Dockerfile</code> contents</summary>

```dockerfile
# Dockerfile
FROM nettools:week04

# softflowd: NetFlow/IPFIX exporter (Lab 2, runs on rtr1)
# nfdump: provides nfcapd (collector) and nfdump (query tool) (Lab 2, runs on collector)
RUN apk add --no-cache softflowd nfdump

# hsflowd: sFlow host agent (Lab 1, runs on rtr1). Not packaged for Alpine,
# so build from source -- see the two callouts below for why FEATURES="HOST"
# needs this exact dependency list, and why the sed patch is required.
RUN apk add --no-cache \
      git build-base clang linux-headers \
      libnfnetlink-dev libpcap-dev \
      libvirt-dev libxml2-dev jq \
      dbus-dev pkgconf util-linux-dev openssl-dev \
    && git clone https://github.com/sflow/host-sflow.git /tmp/host-sflow \
    && cd /tmp/host-sflow \
    && sed -i '/crashFD/d' src/Linux/hsflowd.c \
    && make FEATURES="HOST" \
    && make install \
    && rm -rf /tmp/host-sflow

# goflow2: single-binary sFlow/NetFlow/IPFIX collector (Lab 1, runs on collector)
# GitHub releases ship a bare binary for this asset, not an archive --
# confirm the current version/asset name before building (the releases page
# JS-renders its asset list, so check via the API instead of the web UI:
# curl -s https://api.github.com/repos/netsampler/goflow2/releases/tags/v<VERSION> | grep name).
ARG GOFLOW2_VERSION=2.2.6
RUN wget -O /usr/local/bin/goflow2 \
      "https://github.com/netsampler/goflow2/releases/download/v${GOFLOW2_VERSION}/goflow2-${GOFLOW2_VERSION}-linux-amd64" \
    && chmod +x /usr/local/bin/goflow2

COPY summarize-flow.py /summarize-flow.py
```

</details>

The last line of the Dockerfile copies a utility script that will help you summarize flow data during the lab. See the below code, and write it to `summarize-flow.py` in the same directory as the Dockerfile.

<details>
<summary>Show <code>summarize-flow.py</code> contents</summary>

```python
#!/usr/bin/env python3
import json
import sys

HOST1, HOST2 = "10.5.1.10", "10.5.2.10"

def direction(src, dst):
    if src == HOST1 and dst == HOST2:
        return "host1 -> host2"
    if src == HOST2 and dst == HOST1:
        return "host2 -> host1"
    return f"other ({src} -> {dst})"

def iter_records(path):
    # goflow2's -transport.file output doesn't reliably put a newline
    # between JSON objects, so reading line-by-line can split a record in
    # half. raw_decode() pulls one JSON value at a time from the buffer
    # and reports where it stopped, regardless of what separates records.
    decoder = json.JSONDecoder()
    with open(path) as f:
        content = f.read()
    idx, n = 0, len(content)
    while idx < n:
        while idx < n and content[idx].isspace():
            idx += 1
        if idx >= n:
            break
        rec, idx = decoder.raw_decode(content, idx)
        yield rec

totals = {}  # direction -> {"samples": n, "raw_packets": n, "raw_bytes": n, "rate": n}

for rec in iter_records(sys.argv[1] if len(sys.argv) > 1 else "lab1-samples.jsonl"):
    if rec.get("type") != "SFLOW_5":
        continue  # skip counter samples -- this script only estimates from packet samples
    d = direction(rec.get("src_addr"), rec.get("dst_addr"))
    t = totals.setdefault(d, {"samples": 0, "raw_packets": 0, "raw_bytes": 0, "rate": rec["sampling_rate"]})
    t["samples"] += 1
    t["raw_packets"] += rec.get("packets", 1)
    t["raw_bytes"] += rec.get("bytes", 0)

print(f"{'Direction':<20} {'Samples':>10} {'Est. Packets':>14} {'Est. Bytes':>14}")
for d, t in totals.items():
    est_packets = t["raw_packets"] * t["rate"]
    est_bytes = t["raw_bytes"] * t["rate"]
    print(f"{d:<20} {t['samples']:>10} {est_packets:>14,} {est_bytes:>14,}")
```

</details><br />

**Why this exact package list:** `FEATURES="HOST"` is not a minimal build — per the [host-sflow Linux Makefile](https://github.com/sflow/host-sflow/blob/master/src/Linux/Makefile), it expands to a fixed list of modules: `NFLOG PCAP TCP DOCKER KVM OVS DBUS SYSTEMD PSAMPLE DENT DROPMON NLROUTE`. Each of those needs its own headers/libraries, all pulled directly from the Makefile's `CFLAGS_<MODULE>`/`LIBS_<MODULE>` definitions:

| Module(s) | Needs | Package(s) above |
|---|---|---|
| PSAMPLE, DROPMON, NLROUTE | kernel netlink UAPI headers | `linux-headers` |
| NFLOG | `libnfnetlink.h`, `-lnfnetlink` | `libnfnetlink-dev` |
| PCAP | `pcap.h`, `-lpcap` | `libpcap-dev` |
| KVM | `libvirt.h`, `libxml2`, `-lvirt -lxml2` | `libvirt-dev libxml2-dev` |
| DBUS | `pkg-config dbus-1` | `dbus-dev pkgconf` |
| SYSTEMD | DBUS's flags, plus `-luuid -lcrypto` | `util-linux-dev openssl-dev` |
| TCP, DOCKER, OVS, DENT | no extra headers/libs (DOCKER only needs `-lm`, part of musl) | *(none)* |

**Why the `sed` patch:** `hsflowd.c` writes crash-backtrace diagnostics to a file descriptor (`sp->crashFD`) on `SIGSEGV`, a debug-only feature that only compiles against glibc/uClibc's `backtrace()` (gated by `HAVE_BACKTRACE` in the header). Alpine uses musl libc, which doesn't have it — but the `.c` file references `sp->crashFD` unconditionally instead of behind the same guard, so it fails to compile on any musl-based system, independent of which `FEATURES` you chose. Deleting every line containing `crashFD` removes only that diagnostic feature; it has no effect on sFlow sampling, polling, or export, which is all this lab actually uses.

## Step 3: Build and tag the image

```bash
docker build -t nettools:week05 .
```

## Step 4: Verify

```bash
docker run --rm nettools:week05 hsflowd -h
docker run --rm nettools:week05 softflowd -h
docker run --rm nettools:week05 nfcapd -h
docker run --rm nettools:week05 nfdump -h
docker run --rm nettools:week05 goflow2 -h
```

Each command should print usage information and return immediately, same as the version checks in [Week 4 Lab 0](../week_04/lab0). If any command isn't found, revisit the corresponding install step above — package availability and the exact Alpine repo (`main` vs `community`) can shift between releases.
