# Lab 02 — Linux Router

Route packets between two subnets and watch L2 headers change while L3 source/destination stay constant.

## Topology

```text
pc1 -- 10.0.1.0/24 -- r1 -- 10.0.2.0/24 -- pc2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Disable `ip_forward`, remove routes, and rebuild connectivity one step at a time.
- Capture on both router interfaces and compare MAC addresses.
- Observe TTL decreasing by one at the router.

## Useful checks

- `docker exec clab-pp02-pc1 ip route get 10.0.2.2`
- `docker exec clab-pp02-pc1 ping -c 2 10.0.2.2`


