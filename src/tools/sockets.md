---
title: Socket Programming
---

# Socket Programming

This page covers low-level socket programming and kernel TCP state observation. These are reference tools — useful for understanding what TCP is doing below the API surface, debugging connection issues, and building intuition about the protocol mechanics covered in Week 4.

All examples require Python 3 and either root/sudo or `CAP_NET_RAW` capability for the raw socket sections. Run them on the lab host or inside a container with `--privileged`.

---

## Observing live TCP state with `ss`

`ss` (socket statistics) reads directly from the kernel's TCP state — it's the modern replacement for `netstat`. The `-tip` flags give you per-socket TCP internal variables:

```bash
ss -tip
```

Key fields:

| Field | Meaning |
|-------|---------|
| `cwnd` | Congestion window in segments — how many MSS the sender may have in flight |
| `ssthresh` | Slow-start threshold — above this, AIMD applies instead of exponential growth |
| `rtt` | Smoothed RTT estimate / RTT variance (format: `rtt/rttvar`) |
| `retrans` | Number of retransmitted segments on this socket |
| `unacked` | Segments sent but not yet acknowledged |
| `rcv_space` | Receive buffer size (flow control window) |

Useful invocations:

```bash
# All TCP sockets with internals
ss -tip

# Filter to a specific destination
ss -tip dst 10.4.0.2

# Watch cwnd live during an iperf3 test
watch -n 0.5 'ss -tip dst 10.4.0.2 | grep cwnd'

# Show only ESTABLISHED sockets
ss -tip state established
```

*Exercise:* Start an iperf3 server on one host and a client on another (no impairment). Watch `cwnd` grow during slow start. Count the RTTs until it stops growing exponentially and transitions to linear AIMD growth. Does the transition happen near `ssthresh`?

---

## Raw ICMP with Python

The standard `ping` is built on ICMP echo request/reply. Here it is as a raw socket — this illustrates how raw sockets bypass the transport layer entirely and write directly to IP:

```python
#!/usr/bin/env python3
"""Minimal raw ICMP ping. Requires root or CAP_NET_RAW."""
import socket, struct, time, os

def checksum(data: bytes) -> int:
    s = 0
    for i in range(0, len(data) - 1, 2):
        s += (data[i] << 8) + data[i + 1]
    if len(data) % 2:
        s += data[-1] << 8
    s = (s >> 16) + (s & 0xffff)
    return ~(s + (s >> 16)) & 0xffff

def ping(dest: str, count: int = 4) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(2)

    for seq in range(count):
        # Build ICMP echo request (type=8, code=0)
        header = struct.pack("!BBHHH", 8, 0, 0, os.getpid() & 0xFFFF, seq)
        payload = b"ping" * 4
        cs = checksum(header + payload)
        packet = struct.pack("!BBHHH", 8, 0, cs, os.getpid() & 0xFFFF, seq) + payload

        sent_at = time.time()
        sock.sendto(packet, (dest, 0))

        try:
            reply, addr = sock.recvfrom(1024)
            rtt_ms = (time.time() - sent_at) * 1000
            # ICMP reply is after 20-byte IP header
            icmp_type = reply[20]
            print(f"Reply from {addr[0]}: seq={seq} type={icmp_type} rtt={rtt_ms:.2f}ms")
        except socket.timeout:
            print(f"seq={seq}: timeout")

        time.sleep(1)

    sock.close()

if __name__ == "__main__":
    import sys
    ping(sys.argv[1] if len(sys.argv) > 1 else "8.8.8.8")
```

```bash
sudo python3 ping.py 10.4.0.2
```

*What to notice:* you're building the ICMP header by hand with `struct.pack`, computing the checksum yourself, and sending it directly to IP. There's no `connect()`, no stream, no ACKs. Raw sockets drop you below every transport-layer abstraction.

---

## Observing a TCP handshake with Scapy

Scapy lets you capture and decode packets at the Python level, with full protocol dissection. This snippet captures one complete TCP three-way handshake and prints the key fields:

```python
#!/usr/bin/env python3
"""Capture a TCP handshake. Run before initiating a connection to the target."""
from scapy.all import sniff, TCP, IP

TARGET_HOST = "10.4.0.2"
TARGET_PORT = 5201   # iperf3 default

def show_handshake(pkt):
    if TCP not in pkt:
        return
    if pkt[IP].dst not in (TARGET_HOST,) and pkt[IP].src not in (TARGET_HOST,):
        return

    flags = pkt[TCP].flags
    flag_str = ""
    if flags & 0x02: flag_str += "SYN "
    if flags & 0x10: flag_str += "ACK "
    if flags & 0x01: flag_str += "FIN "
    if flags & 0x04: flag_str += "RST "

    print(f"{pkt[IP].src}:{pkt[TCP].sport} → {pkt[IP].dst}:{pkt[TCP].dport}  "
          f"flags=[{flag_str.strip()}]  seq={pkt[TCP].seq}  ack={pkt[TCP].ack}  "
          f"win={pkt[TCP].window}")

print(f"Sniffing for TCP to/from {TARGET_HOST}:{TARGET_PORT}. Start a connection now.")
sniff(
    filter=f"tcp and host {TARGET_HOST} and port {TARGET_PORT}",
    prn=show_handshake,
    count=6,   # SYN + SYN-ACK + ACK + data + FIN + FIN-ACK
    store=False
)
```

```bash
sudo python3 capture_handshake.py
# In another terminal: iperf3 -c 10.4.0.2 -t 3
```

*What to notice:* the sequence numbers. The SYN carries the ISN (initial sequence number, random); the SYN-ACK carries the server's ISN and acknowledges the client's; the ACK acknowledges the server's. After the handshake, `seq` increments by the number of bytes sent. This is the foundation of TCP's reliable delivery.

---

## Crafting a TCP SYN with Scapy

Scapy can also *send* crafted packets. This example sends a raw TCP SYN to a target and prints the SYN-ACK response — without going through the OS TCP stack:

```python
#!/usr/bin/env python3
"""Send a raw TCP SYN and receive the SYN-ACK. Requires root."""
from scapy.all import IP, TCP, sr1, conf

conf.verb = 0   # suppress Scapy's default output

TARGET = "10.4.0.2"
PORT   = 5201

syn = IP(dst=TARGET) / TCP(dport=PORT, flags="S", seq=1000)
response = sr1(syn, timeout=2)

if response is None:
    print("No response (port filtered or host unreachable)")
elif response[TCP].flags & 0x12:   # SYN-ACK
    print(f"SYN-ACK received from {TARGET}:{PORT}")
    print(f"  Server ISN: {response[TCP].seq}")
    print(f"  Ack of our SYN: {response[TCP].ack}")
    print(f"  Server window: {response[TCP].window}")
    # Send RST to cleanly close — otherwise the kernel will send RST on its own
    rst = IP(dst=TARGET) / TCP(dport=PORT, flags="R", seq=response[TCP].ack)
    sr1(rst, timeout=1)
elif response[TCP].flags & 0x14:   # RST-ACK
    print(f"RST received: port {PORT} is closed on {TARGET}")
```

```bash
sudo python3 syn_probe.py
```

*What to notice:* the server's SYN-ACK `ack` field is always our `seq + 1`. The ISN (`seq` in the SYN-ACK) is the server's random starting point. The OS kernel, running in parallel, will see the inbound SYN-ACK and send a RST (because it has no state for this connection) — Scapy's raw socket bypasses the kernel TCP stack, but the kernel still sees the replies on the wire.

> **Port filtering note:** if the target is a ContainerLab container and `iperf3 -s` isn't running, you'll get a RST. Start the iperf3 server first.

---

## Further reading

- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) — the standard C-level introduction to BSD sockets. Covers `socket()`, `bind()`, `connect()`, `send()`, `recv()` with working examples.
- [Scapy documentation](https://scapy.readthedocs.io/) — full API reference. The "Interactive tutorial" section covers crafting arbitrary protocol stacks.
- [`ss` manual page](https://man7.org/linux/man-pages/man8/ss.8.html) — `ss -tip` is the most useful single invocation; the manual covers the full filter language.
