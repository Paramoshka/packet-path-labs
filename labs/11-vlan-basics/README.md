# Lab 11 — VLAN Basics

Use a Linux bridge with VLAN filtering to model access ports and inspect the forwarding database.

## Topology

```text
h1 -- access VLAN10 -- sw1 -- access VLAN10 -- h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect bridge VLAN membership and FDB learning.
- Move h2 to VLAN20 and observe loss of connectivity.
- Add a tagged trunk in the next lab.

## Useful checks

- `docker exec clab-pp11-sw1 bridge vlan show`
- `docker exec clab-pp11-sw1 bridge fdb show`


