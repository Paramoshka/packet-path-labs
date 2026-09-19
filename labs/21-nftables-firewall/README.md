# Lab 21 — nftables Firewall

Build a stateful forwarding firewall: ICMP is allowed, everything else is dropped unless it belongs to an established flow.

## Topology

```text
h1 -- fw[nftables] -- h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect counters while pinging.
- Start a TCP listener and see the default drop policy.
- Add a TCP allow rule and compare state tracking on replies.

## Useful checks

- `docker exec clab-pp21-fw nft list ruleset`
- `docker exec clab-pp21-h1 ping -c 2 10.0.2.2`


