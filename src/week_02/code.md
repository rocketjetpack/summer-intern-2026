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

### Exercise 1 — Build and inspect a packet

Use `scapy` to construct and inspect packet objects without sending them. No special privileges are needed for this — you are just building Python objects and reading their fields.

#### Workstation and Lmod Note

**For this you can use any system that has a modern Python3 installed. If you do this on your workstation you should first run the commands in a terminal:**

`module load python3`  
`python3 -m venv /home/$USER/lab-venv`  
`source /home/$USER/lab-venv/bin/activate`  
`pip3 install scapy`  

These commands will load the current cluster version of Python3 into your environment, then use it to create a Python virtual environment on your local NVMe drive and activate it. This will allow you to use `pip` to install software when you normally would not be able to on your workstation.

```python
from scapy.all import Ether, IP, UDP, DNS, DNSQR, ARP

# Build a DNS query packet layer by layer and inspect the result
pkt = Ether() / IP(dst="8.8.8.8") / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"))
pkt.show()        # full field-by-field breakdown
pkt.summary()     # one-line summary
```

This simple program builds a DNS request that would be transmitted to the destination IP of 8.8.8.8 (a public DNS server operated by Google) requesting a resolution for "example.com". Notice how the output reveals the nested composition following the OSI model: the DNS query is the payload of a UDP datagram, that datagram is the payload of an IP packet, and that IP packet is the payload of an Ethernet frame. Each layer of the model encapsulates the entirity of the higher tiers data as the payload (e.g. Layer 3 (IP) encapsulates Layer 4(UDP)).

Try the same thing with `Ether()/ARP()`. Notice how `.show()` labels every field and its value — this is the same structure Wireshark shows you, just in Python form.

As you experiment with Scapy and packet generation try to identify which layers are present and how they are always encapsulated within a lower layers data structure.

***Caution**: Layers 5 (Session) and 6 (Presentation) are not always present. These layers are ticky and frequently will not appear in packet data. For exmaple, the DNS query above has Layers 7 (Application: DNS), 4 (Transport: UDP), 3 (Network: IP), 2 (Data Link: Ethernet).*

---

### Exercise 2 — Treat a capture as a dataset

**Before loading the pcap file you will need to `gunzip` the Gzip file and put the The-Ultimate-PCAP.pcapng file in the same place as your Python script (or modify the code below to load it from where you put the file).**

Scapy can read pcap files from disk without any special permissions. Use the same **Ultimate PCAP** from the Wireshark lab above. You are not sending anything — you are loading the file and querying it like a structured dataset.

```python
from scapy.all import rdpcap

packets = rdpcap("The-Ultimate-PCAP.pcapng")  # adjust the filename/path as needed
print(f"Loaded {len(packets)} packets")
packets[0].show()   # inspect the first packet to get your bearings
```

Work through the tasks below in order — each one builds on the last.

---

#### Task A — Protocol distribution

Count how many packets belong to each protocol. `pkt.lastlayer().name` gives you the name of the innermost (highest) layer Scapy could decode.

```python
from collections import Counter

proto_counts = Counter()
for pkt in packets:
    proto_counts[pkt.lastlayer().name] += 1

for proto, count in proto_counts.most_common(15):
    print(f"{proto:<30} {count}")
```

Once you have that working, try counting **bytes** instead of packets — replace the `+= 1` with `+= len(pkt)` and compare the two ranked lists.

**Questions to investigate:**

1. What is the most common protocol by packet count? Does the top of the list change when you rank by bytes instead? What does a big gap between the two rankings tell you about how that protocol behaves on the wire?

2. Some layer names you see will be things like `Raw` or `Padding`. Why would Scapy label a packet that way, and what does it mean for your counts? *This one is kind of tricky, and generally revolves more around what Scapy **can't** decode, such as encrypted data.*

---

#### Task B — DNS query log

Filter the capture down to DNS traffic and build a log of every query paired with its answer.

```python
from scapy.all import DNS, DNSQR, DNSRR, IP

for pkt in packets:
    try:
        if not pkt.haslayer(DNS):
            continue

        dns = pkt[DNS]

        if dns.qr == 0 and dns.qd:   # qr=0 is a query
            qname = dns.qd.qname.decode().rstrip(".")
            print(f"QUERY  {pkt[IP].src:<16} → {qname}")

        elif dns.qr == 1 and dns.an:  # qr=1 is a response, an=answer section
            name = dns.an.rrname.decode().rstrip(".")
            rdata = dns.an.rdata
            ttl   = dns.an.ttl
            rcode = dns.rcode
            print(f"ANSWER {name:<40} → {rdata}  (TTL {ttl}s, rcode {rcode})")
    except Exception as e:
        # We dont really care about exceptions, some packets fail to parse which is fine
        # just ignore them and move on.
        continue
```

Extend this into a dictionary keyed by query name so you can look up "what did this name resolve to?" in later tasks.

**Questions to investigate:**

3. DNS is a heavily cached protocol in that a client system will maintain a local cache of recently resolved queries so that it doesn't
have to repeat queries for records where it already knows the name. In DNS, TTL stands for (Time To Live). Who determines what the TTL for a record is? How does this relate to DNS caching? What circumstances would lead one to set a lower or higher TTL?

4. The rcode section of a DNS header indicates the type of response. Explore the PCAP contents to see what types of rcodes are found? What is the rcode telling the client about the request? *Hint: There are 6 rcode values currently widely adopted though more have been proposed.*

If you would like to explore the fields of a DNS packet more deeply, I recommend the following RFCs:  
  - RFC1034 - Domain Name: Concepts and Facilities (1987): Original concept of DNS  
  - RFC1035 - Domain Names: Implementation and Specification (1987): Defines the structure of DNS protocol and the original RCODEs  
  - RFC2136 - Dynamic Updtaes in the DNS (1997):" Intorudces 5 additional RCODEs  

In silly software that shows creative methods to use DNS and specifically caching, the [dnsfs](https://github.com/benjojo/dnsfs) repo explores a way to store arbitrary data in DNS caches.

---

#### Task C — IP conversation table

Build a table showing every pair of IP addresses that exchanged traffic, and how many bytes flowed in each direction.

```python
from scapy.all import IP
from collections import defaultdict

from scapy.all import IP
from collections import defaultdict

conversations = {}

for pkt in packets:
    if not pkt.haslayer(IP):
        continue

    src = pkt[IP].src
    dst = pkt[IP].dst
    size = len(pkt)

    # Find existing conversation in either direction
    if (src, dst) in conversations:
        conv = conversations[(src, dst)]
        conv["fwd"] += size

    elif (dst, src) in conversations:
        conv = conversations[(dst, src)]
        conv["rev"] += size

    else:
        conversations[(src, dst)] = {
            "fwd": size,   # SRC -> DST
            "rev": 0,      # DST -> SRC
            "pkts": 0,
        }
        conv = conversations[(src, dst)]

    conv["pkts"] += 1

top = sorted(
    conversations.items(),
    key=lambda kv: kv[1]["fwd"] + kv[1]["rev"],
    reverse=True
)

print(f"{'SRC':<16} {'DST':<16} {'SRC→DST bytes':>10} {'DST→SRC bytes':>10} {'pkts':>6}")

for (src, dst), v in top[:20]:
    print(
        f"{src:<16} {dst:<16} "
        f"{v['fwd']:>10} {v['rev']:>10} {v['pkts']:>6}"
    )
```

**Questions to investigate:**

5. Look at theese conversations by total bytes in each direction. Are they symmetric (roughly equal bytes each direction) or asymmetric? What kind of traffic would you expect to look symmetric? What kind of traffic would you expect to look asymmetric, and in which direction would the asymmetry present?

6. Take one IP address that appears prominently in your conversation table. Search your DNS answer log from Task B — does that IP show up as an answer to any query? What does it mean that the network layer routes by IP address despite humans initiating connections using names?

## General Thoughts

The goal of these labs are to help you begin to think of network communication as a type of "conversation" between two systems. Computer software communication requires the same three basic requirements:  
  - A sender  
  - A receiver  
  - A common language

In networking, the "common language" is not a single protocol but a *stack* of them with each layer speaking only to the layer directly above and below it. That is the layered model you have read about, and these labs were designed to make this concrete rather than abstract. Wireshark lets you *see* it visually, Scapy's `pkt.show()` lets you *construct* it in code, and the pcap analysis exercises let you *query* it at scale.

ARP and DNS both fit into this picture as the protocols that make conversations *possible* before any application data moves at all. DNS answers "who am I trying to reach?" at the name level; ARP answers "how do I physically reach the next hop?" at the link level. Without both working correctly, the conversation never starts. This is why network problems often turn out to be caused by name resolution or reachability failures rather than any faults in the application itself.

The progression from Wireshark → Scapy construction → programmatic pcap analysis is also intentional. Clicking through Wireshark is valuable for building intuition, but it doesn't scale. You cannot click through a million packets. Writing code that reads a capture as a dataset, filters it, aggregates it, and surfaces anomalies is exactly the skill that underlies network monitoring and observability tooling. The conversation table in Task C, for example, is a stripped-down version of what flow-analysis systems do continuously on live traffic. 
