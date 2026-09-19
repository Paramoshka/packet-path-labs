# Lab 08 — ECMP

Create equal-cost paths and inspect multiple next hops in both FRR and the Linux kernel.

## Topology

```text
      r2
     /  \
r1        r4
     \  /
      r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Verify two equal-cost next hops from R1 to R4.
- Inspect `ip nexthop` / `nhid` objects.
- Generate multiple flows and observe hash-based path selection.

## Useful checks

- `docker exec clab-pp08-r1 vtysh -c "show ip route 4.4.4.4/32"`
- `docker exec clab-pp08-r1 ip route show 4.4.4.4`


