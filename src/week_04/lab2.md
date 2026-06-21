---
title: "Lab 2: Querying Network Data with the LibreNMS API"
---

# Lab 2: Querying Network Data with the LibreNMS API

Lab 1 worked entirely on infrastructure you built and broke yourself. This lab is a short introduction to a different skill: pulling real operational data out of a network monitoring platform (in this case, LibreNMS), which tracks thousands of and interfaces and provides a convenient REST API.

This isn't a deep-dive into any one metric. It's a small exercise to expose you to an additional tool that you can explore and use.

Unlike Lab 1, this lab should be run on your workstation.

---

## Step 0: Credentials

You'll be issued an API token. Export it along with the instance URL — never hardcode API credentials in a script you might commit:

```bash
export LIBRENMS_URL="https://librenms.example.internal"
export LIBRENMS_API_KEY="<your-token>"
```

All commands below use `$LIBRENMS_URL`/`$LIBRENMS_API_KEY` as placeholders. Substitute your real values at the shell, not in any file you save.

## Step 1: First call

Every request authenticates with an `X-Auth-Token` header. Confirm your key works and look at the raw shape of a response before writing any code. The following query will print a list of all API endpoints that are exposed.

```bash
curl -s -H "X-Auth-Token: $LIBRENMS_API_KEY" \
  "$LIBRENMS_URL/api/v0" | jq | less
```

## Step 2: Devices

Most endpoints accept a `columns` parameter to limit the fields returned — useful once you're pulling thousands of records instead of paging through `less`. The devices endpoint also takes a `type` parameter that filters server-side: `all`, `active` (not ignored/disabled), `up`, `down`, `disabled`, `ignored`. This instance has plenty of stale, decommissioned, or otherwise dead entries, so filter to `up` here rather than pulling everything and sorting it out yourself:

```python
import os
import requests

LIBRENMS_URL = os.environ["LIBRENMS_URL"]
API_KEY = os.environ["LIBRENMS_API_KEY"]
HEADERS = {"X-Auth-Token": API_KEY}

resp = requests.get(
    f"{LIBRENMS_URL}/api/v0/devices",
    headers=HEADERS,
    params={"type": "up", "columns": "device_id,hostname,sysName,os,uptime"},
    timeout=30,
)
resp.raise_for_status()
devices = resp.json()["devices"]
up_device_ids = {int(d["device_id"]) for d in devices}

print(f"{len(devices)} devices currently up")
for d in devices[:10]:
    print(f"  {d['hostname']:30s} {d.get('os', '?'):10s} uptime={d.get('uptime')}")
```

**Question:** Drop `type=up` and re-run with no `type` param at all. How many more devices show up? 

*Note: Our LibreNMS needs some cleanup as there are quite a few devices that have been removed from the network but not removed from LibreNMS.*

> `up_device_ids` carries forward into Step 3. Neither of those endpoints has its own "only up devices" filter, so it's on you to apply one.

## Step 3: Ports and a derived metric

`/api/v0/ports` returns interface-level data across every device in one call — no need to loop per-device. Most fields here are raw SNMP counters (RFC 2863's `ifTable`): `ifSpeed`, `ifInOctets`/`ifOutOctets`, and their `_rate` variants.

```python
resp = requests.get(
    f"{LIBRENMS_URL}/api/v0/ports",
    headers=HEADERS,
    params={"columns": "device_id,ifName,ifSpeed,ifOperStatus,ifInOctets_rate,ifOutOctets_rate"},
    timeout=30,
)
resp.raise_for_status()
ports = resp.json()["ports"]
print(f"{len(ports)} ports total")

ports = [p for p in ports if int(p["device_id"]) in up_device_ids]
print(f"{len(ports)} ports on devices that are actually up")

# Not every field is directly useful as-is — utilization is a simple example
# of turning two raw counters into something meaningful: bits/sec as a
# fraction of link speed.
up_ports = [p for p in ports if p.get("ifOperStatus") == "up" and (p.get("ifSpeed") or 0) > 0]
busiest = max(
    up_ports,
    key=lambda p: max(p.get("ifInOctets_rate") or 0, p.get("ifOutOctets_rate") or 0) * 8 / p["ifSpeed"],
)
util = max(busiest.get("ifInOctets_rate") or 0, busiest.get("ifOutOctets_rate") or 0) * 8 / busiest["ifSpeed"]
print(f"Busiest port seen: device {busiest['device_id']} / {busiest['ifName']} at {util:.1%} of {busiest['ifSpeed']:,} bps")
```

*Note: It's worth knowing that LibreNMS is polling infrequently, somewhere around 5 minutes. Any rate field exposed by the API, or any rate calculations you may do using other fields will inherently represent averaged values over the polling window.*

---

