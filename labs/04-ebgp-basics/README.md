# Lab 04 — eBGP Basics

Use three autonomous systems to study BGP policy and path propagation.

## Topology

```text
AS65001 r1 ---- AS65002 r2 ---- AS65003 r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect BGP session establishment over TCP/179.
- Follow AS_PATH as a prefix crosses autonomous systems.
- Compare the BGP RIB with the Linux FIB.

## Useful checks

- `docker exec clab-pp04-r1 vtysh -c "show bgp ipv4 unicast summary"`
- `docker exec clab-pp04-r1 vtysh -c "show bgp ipv4 unicast"`


