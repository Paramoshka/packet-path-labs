# Lab 01 — L2, ARP and ICMP

Observe the complete local-LAN packet path: ARP resolution first, then ICMP over Ethernet.

## Topology

```text
pc1 10.0.0.1/24 -------- 10.0.0.2/24 pc2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Flush the neighbor cache and capture `arp or icmp` on `eth1`.
- Match the ARP-learned MAC address with `ip link`.
- Compare management `eth0` with lab `eth1`.

## Useful checks

- `docker exec clab-pp01-pc1 ip neigh`
- `docker exec clab-pp01-pc1 ping -c 2 10.0.0.2`


