# Lab 27 — MPLS Basics with LDP

Add an MPLS label-forwarding plane on top of an OSPF underlay and inspect LDP label bindings.

## Topology

```text
r1 ==== MPLS/LDP ==== r2 ==== MPLS/LDP ==== r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Ensure the host kernel has MPLS modules available.
- Inspect LDP neighbors and label bindings.
- Capture ethertype 0x8847 after labels are installed.

## Useful checks

- `docker exec clab-pp27-r2 vtysh -c "show mpls ldp neighbor"`
- `docker exec clab-pp27-r2 ip -f mpls route`

Note: this lab depends on MPLS support in the host kernel.

