---
title: Labs
---

## Hands-on lab

1. Download [**The Ultimate PCAP**](https://weberblog.net/the-ultimate-pcap/) - a single ~6 MB capture covering 90+ protocols that opens directly in Wireshark - or, for something lighter, [`dns.cap`](https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/dns.cap) from the [Wireshark Sample Captures](https://wiki.wireshark.org/SampleCaptures) page.<br />**Note: This file is a gzip, but it CAN be opened directly by WireShark.**

2. Open it in Wireshark with **File → Open**. Use the display filter bar to find:
   - **ARP** request and reply *(filter: `arp`)*
   - **DNS** query/response *(filter: `dns`)*
   - **TCP three-way handshake** *(filter: `tcp.flags.syn==1`)*

3. Pick **one** packet and label every layer it's wrapped in, bottom to top: Ethernet → IP → TCP/UDP → application protocol. For each layer, note the field that told you what comes next (e.g., the Ethernet "type" field pointing to IPv4, the IP "protocol" field pointing to TCP).

### Questions to investigate

The frame numbers below are from **The Ultimate PCAP** (open it, then use `Edit → Find Packet → Display filter` or just type `frame.number == <N>` in the filter bar to jump straight to one). Don't just answer *what* happened, try using the surrounding packets to work out *why*.

1. Packet numbers 23594 through 23601 document an ARP request `"Who has 1.1.1.1? Tell 193.24.225.56"` that never gets a reply, even though it's repeated several times. Why does this ARP request never receive a reply? 

2. Packets 23593, 23604, and 23606 are all labeled `"Gratuitous ARP for 193.24.225.56 (Reply)"` and represent an ARP *reply* that nobody asked for. Why would a host send an ARP reply without first receiving a request? What would happen to everyone else's ARP caches when they see it?

3. Packets 19680–19684 show a DNS query for the name `nobody.invalid` answered with rcode 3 (`"No such name."`) The DNS server didn't time out, drop the query, or send back nothing. It sent back a *specific, structured answer saying the name doesn't exist*. What does that tell you about what a protocol response is allowed to carry, beyond just "the data you asked for"? These packets contain information about the acronyms `A,AAAA,SOA,TXT`, what are these?

4. Frames 5990–6004 capture the end of a live SSH session — real encrypted application data is still flowing in frame 5997. Then the client sends `[FIN, ACK]`, the server answers with its own `[FIN, PSH, ACK]`, the client `[ACK]`s it... and the *server* immediately follows up with four `[RST]` packets back to the client. Trace that sequence frame by frame: who closes first, does each side's FIN get acknowledged, and what shows up right after the close looks "done"? What does it mean for a connection to end "cleanly" at the TCP level versus the application actually being finished with it — and what kind of behavior on the server's end would produce exactly this pattern? <br />
*This one is tricky.*

5. Packets 80 and 84 (and several others nearby) are flagged by Wireshark as **`[TCP Retransmission]`**. These represent the exact same segment being sent again. Why would a layer ever resend something it already sent once — and how would it know that it needed to?

6. There is a wealth of very interesting exchanges in this packet capture. I'd encourage you to explore around it, become familiar with the Wireshark interface, and see if you come up with questions you would like to discuss

## Code lab

- Use `scapy` to **construct and inspect** packet objects, (e.g. `Ether()/ARP()` followed by `.show()` or `.summary()`) without sending them on the wire. Building and reading a packet's layers in code is enough to see encapsulation happen; actually transmitting raw frames needs raw-socket access.

- I am still working on another code lab that would start to set the foundation for your project. Let's discuss this.

