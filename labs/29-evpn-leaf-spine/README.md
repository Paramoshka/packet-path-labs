# Lab 29 — EVPN over a Leaf-Spine Underlay

Combine a redundant eBGP underlay with VXLAN VTEPs and an EVPN overlay. The starter keeps the EVPN session leaf-to-leaf so the control plane is easy to inspect; convert it to spine route reflectors as the main extension.

## Topology

```text
          spine1      spine2
           /  \      /  \
         leaf1 ===== leaf2
          |   EVPN    |
         h1          h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Verify leaf loopbacks are reachable through the eBGP underlay.
- Inspect the EVPN session and VNI 100 MAC routes.
- Extension: move EVPN control-plane peering to spine route reflectors.

## Useful checks

- `docker exec clab-pp29-leaf1 vtysh -c "show bgp ipv4 unicast summary"`
- `docker exec clab-pp29-leaf1 vtysh -c "show bgp l2vpn evpn"`
- `docker exec clab-pp29-leaf1 vtysh -c "show evpn vni"`


