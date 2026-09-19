# Lab 04 — eBGP Basics

Use three autonomous systems to study BGP policy and path propagation.

## Topology

```text
AS65001 r1 ---- AS65002 r2 ---- AS65003 r3
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

The router configurations disable `bgp ebgp-requires-policy`. With FRR's
`traditional` defaults, eBGP sessions without explicit import and export
policies reach `Established`, but discard route advertisements and show
`(Policy)` in the summary. Explicit filtering is introduced in Lab 05.

## Explore

- Inspect BGP session establishment over TCP/179.
- Follow AS_PATH as a prefix crosses autonomous systems.
- Compare the BGP RIB with the Linux FIB.

To capture the session between `r2` and `r3`, run this on the host:

```bash
sudo ip netns exec clab-pp04-r2 \
  tshark -i eth2 -f "tcp port 179" -O bgp
```

In another terminal, reset that session:

```bash
docker exec clab-pp04-r2 vtysh -c "clear ip bgp 10.0.23.2"
```

Look for the NOTIFICATION that closes the old session, the TCP handshake,
BGP OPEN and KEEPALIVE messages, and the UPDATE exchange. Both peers may open
TCP connections simultaneously; BGP collision detection then closes one of
them. On `r2`, `eth1` captures the `r1`--`r2` link and `eth2` captures the
`r2`--`r3` link.

## Useful checks

- `docker exec clab-pp04-r1 vtysh -c "show bgp ipv4 unicast summary"`
- `docker exec clab-pp04-r1 vtysh -c "show bgp ipv4 unicast"`
- `docker exec clab-pp04-r1 vtysh -c "show ip route bgp"`
- `docker exec clab-pp04-r1 ip route`

