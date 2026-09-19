# Lab 12 — Inter-VLAN Routing

Build a router-on-a-stick: two access VLANs share one tagged trunk to a router with 802.1Q subinterfaces.

## Topology

```text
h10(VLAN10) -- sw1 == trunk 10,20 == r1
h20(VLAN20) --/
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Capture tagged frames on the trunk and untagged frames on access ports.
- Inspect `eth1.10` and `eth1.20` on the router.
- Break one VLAN on the trunk and troubleshoot the resulting failure.

## Useful checks

- `docker exec clab-pp12-r1 ip -d link show`
- `docker exec clab-pp12-h10 ping -c 2 10.20.20.20`


