# Lab 09 — OSPF Failure and Convergence

Break a redundant topology and watch OSPF remove the failed adjacency, flood new LSAs and install the alternate path.

## Topology

```text
r1 ---- r2
|        |
r4 ---- r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Continuously ping across the square and shut one link.
- Capture OSPF on the surviving links during reconvergence.
- Measure failure detection and route installation time.

## Useful checks

- `docker exec clab-pp09-r1 vtysh -c "show ip ospf neighbor"`
- `docker exec clab-pp09-r1 vtysh -c "show ip route ospf"`


