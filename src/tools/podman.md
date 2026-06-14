---
title: Podman Lab
---

# Podman Lab — Prometheus + Grafana
# UNDER CONSTRUCTION

[Podman](https://podman.io/) is a daemonless, rootless-by-default alternative to Docker. Its CLI is close enough to Docker's that most commands from the [Docker Lab](./docker) work by just typing `podman` instead of `docker`. The one new concept worth knowing up front is the **pod** — a group of containers that share a network namespace, so they can reach each other over `localhost`. See [What is Podman?](https://docs.podman.io/) and the [Podman tutorials](https://docs.podman.io/en/latest/Tutorials.html) if this is your first time using it.

This lab runs on **your workstation**, as your normal user — no `sudo`, no root daemon. It deploys a small standalone **Prometheus + Grafana** stack — the same monitoring tools you'll use later in the program for telemetry and dashboarding — with **persistent storage**, so the stack survives a reboot or a `podman` upgrade. For now it's self-contained (Prometheus just monitors itself); wiring it up to scrape real devices is a future step.

## 0. Rootless basics

Everything below runs **without `sudo`**. Rootless Podman runs containers as your own Linux user, using user namespaces to map "root inside the container" to your unprivileged UID on the host. If you've never used rootless Podman before, skim the [rootless tutorial](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) — it covers the one-time setup most distros already handle for you.

## 1. Create a pod

```bash
podman pod create --name monitoring -p 9090:9090 -p 3000:3000
```

This opens Prometheus's port (9090) and Grafana's port (3000) on your workstation, both landing in the same pod. See [`podman pod create`](https://docs.podman.io/en/stable/markdown/podman-pod-create.1.html).

## 2. Create volumes for persistent storage

```bash
podman volume create prometheus-data
podman volume create grafana-data
```

Named volumes are managed by Podman and live under your home directory — independent of any container's lifecycle. We'll mount these into Prometheus and Grafana below so each keeps its data (metrics history, dashboards, data sources) across restarts.

Why named volumes instead of bind-mounting a host directory? Grafana's image runs as UID `472` *inside* the container; under rootless Podman, a bind-mounted host directory you own wouldn't be writable by that UID without extra `chown`/`--userns` gymnastics. Podman-managed volumes sidestep this — Podman handles the UID mapping for you.

## 3. Run Prometheus

Create a minimal `prometheus.yml` that scrapes Prometheus itself:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
```

Run the container, mounting that config in and persisting its data to `prometheus-data`:

```bash
podman run -d --pod monitoring --name prometheus \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  -v prometheus-data:/prometheus \
  docker.io/prom/prometheus:latest
```

Confirm it's up at `http://localhost:9090` and that **Status → Targets** shows the `prometheus` job as `UP`. See [Prometheus: Getting started](https://prometheus.io/docs/prometheus/latest/getting_started/) and the [configuration reference](https://prometheus.io/docs/prometheus/latest/configuration/configuration/).

## 4. Run Grafana

```bash
podman run -d --pod monitoring --name grafana \
  -v grafana-data:/var/lib/grafana \
  docker.io/grafana/grafana:latest
```

Browse to `http://localhost:3000` (default login `admin`/`admin`, you'll be asked to change it). Dashboards, data sources, and your admin password now live in `grafana-data` rather than disappearing if the container is removed.

## 5. Connect Grafana to Prometheus

Add Prometheus as a data source — because both containers are in the same pod, Grafana can reach Prometheus at `http://localhost:9090`. Follow [Configure the Prometheus data source](https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/), then build a quick panel (e.g. graph the `up` metric) per [Get started with Grafana and Prometheus](https://grafana.com/docs/grafana/latest/fundamentals/getting-started/first-dashboards/get-started-grafana-prometheus/).

## 6. Clean up (or pause)

```bash
podman pod stop monitoring
podman pod rm monitoring
```

This removes the containers but **not** the volumes — `prometheus-data` and `grafana-data` (and everything in them) survive, ready to be reattached the next time you run steps 3-4. If you really want to discard everything:

```bash
podman volume rm prometheus-data grafana-data
```

## What's next

This stack currently monitors itself — not very interesting yet. The natural next step (a future lab) is pointing Prometheus at real targets: a [`node_exporter`](https://github.com/prometheus/node_exporter) running on the Week 3 Containerlab hosts, or telemetry exported from `sw1`/`rtr1`. Keep this pod (and its volumes) around — you'll extend it rather than start over.
