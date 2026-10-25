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

## Connection tracking and rule order

1. Start a listener on h2 port 8080. Capture on both firewall interfaces while
   h1 connects: distinguish a dropped SYN from a refused connection (RST).
2. Insert a narrow TCP/8080 permit in the forward chain and establish a flow.
   On fw inspect `conntrack -L -p tcp` and `nft -a list ruleset`.
3. Delete the permit using its rule handle. Compare the existing connection
   with a new connection: the existing flow can still match `ct state established`.
4. Delete only that flow's conntrack entry, identifying protocol, source,
   destination and ports. Observe the next packets. Do not flush the entire
   host conntrack table: all commands here belong inside the fw container.
5. Add counters to the relevant rules and use a narrowly matched `meta nftrace
   set 1` rule plus `nft monitor trace` to explain the verdict for one connection.

Success: explain why changing an allow rule does not necessarily terminate
an existing connection, and prove which rule handles each direction.
Destroy/deploy resets rules and flow state.
Reference: [nftables tracing](https://wiki.nftables.org/wiki-nftables/index.php/Ruleset_debug/tracing).
