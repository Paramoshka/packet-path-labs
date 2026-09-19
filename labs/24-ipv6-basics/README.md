# Lab 24 — IPv6 Basics and NDP

Repeat the first L2 lab with IPv6: link-local addresses, Neighbor Discovery and ICMPv6 replace IPv4 ARP behavior.

## Topology

```text
h1 2001:db8:1::1/64 ---- 2001:db8:1::2/64 h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect automatically created `fe80::/64` link-local addresses.
- Flush IPv6 neighbors and capture ICMPv6 Neighbor Solicitation/Advertisement.
- Compare NDP with ARP from Lab 01.

## Useful checks

- `docker exec clab-pp24-h1 ip -6 neigh`
- `docker exec clab-pp24-h1 ping -6 -c 2 2001:db8:1::2`


