# Lab 22 — MTU, Fragmentation and PMTUD

Create an MTU bottleneck and study fragmentation, DF (Don’t Fragment) and Path MTU Discovery.

## Topology

```text
h1 MTU1500 -- r1 -- MTU1200 -- h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Ping with different payload sizes and `-M do`.
- Capture ICMP Fragmentation Needed messages.
- Compare behavior with and without DF.

## Useful checks

- `docker exec clab-pp22-h1 ping -M do -s 1400 -c 1 10.0.2.2`
- `docker exec clab-pp22-h1 tracepath 10.0.2.2`


