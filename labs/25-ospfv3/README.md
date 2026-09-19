# Lab 25 — OSPFv3

Run OSPFv3 for IPv6 and compare its interface-centric configuration and link-local neighbor behavior with OSPFv2.

## Topology

```text
r1 ==== IPv6 ==== r2 ==== IPv6 ==== r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect OSPFv3 neighbors and routes.
- Capture protocol 89 and note link-local source addresses.
- Compare the LSDB with Lab 03.

## Useful checks

- `docker exec clab-pp25-r1 vtysh -c "show ipv6 ospf6 neighbor"`
- `docker exec clab-pp25-r1 vtysh -c "show ipv6 route ospf6"`


