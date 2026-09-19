# Lab 05 — BGP Filtering

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

- Inspect which R3 prefixes reach R1.
- Edit the prefix-list and apply inbound/outbound policies.
- Use soft clear to re-evaluate policy without resetting TCP.

## Useful checks

- `docker exec clab-pp05-r1 vtysh -c "show bgp ipv4 unicast summary"`
- `docker exec clab-pp05-r1 vtysh -c "show bgp ipv4 unicast"`


