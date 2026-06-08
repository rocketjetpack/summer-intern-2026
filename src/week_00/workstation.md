---
title: Workstation
---

# Workstation

The workstation that you have access to is available via SSH and interactive login with keyboard/mouse/monitor. Because this system mounts shared filesystems and has the [Slurm](https://slurm.schedmd.com), root/sudo access is not available here.

This workstation, however, does have access to the necessary networks for your project work this summer. I have installed Wireshark, SNMP tools, and a few other packages. If you require software that cannot be installed in your home directory please let me know.

*For software that will require root permissions we will make use of lab servers hosted in our datacenters that you will have access to.*

I have installed rootless [Podman](https://podman.io/) on your workstation as well.

As we go we will discuss other software that is already operational within the environment that may have relation to your summer project and education.

## Setup checklist

- [ ] Linux comfort (shell, `ip`, `ss`, `tcpdump`), a Python virtual environment (`python -m venv`), and **rootless Podman**.
- [ ] HPC installations make heavy use a modular software. Our cluster uses [Lmod](https://lmod.readthedocs.io/en/latest/) which makes thousands of software packages available on demand.
- [ ] Wireshark, `iperf3`, `net-snmp` tools (`snmpwalk`) — install into the user environment or confirm present.
- [ ] Clone the [project git repo](./repo) — project code, lab notes, and the metric catalog all live there.

## Optional supplements

- **[Cisco Packet Tracer](https://www.netacad.com/courses/packet-tracer)** (free, fully userspace) for extra switching/routing practice.
