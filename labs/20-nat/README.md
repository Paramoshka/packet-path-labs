# Lab 20 — NAT

Translate an RFC1918 source address at a Linux router and observe conntrack/stateful return traffic.

## Topology

```text
inside 10.0.0.10 -- NAT -- 198.51.100.2 outside
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Capture inside and outside interfaces and compare source addresses.
- Inspect NAT rules and conntrack entries.
- Replace MASQUERADE with explicit SNAT as an exercise.

## Useful checks

- `docker exec clab-pp20-inside ping -c 2 198.51.100.2`
- `docker exec clab-pp20-nat iptables -t nat -nvL`


