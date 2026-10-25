# Lab 05 — BGP Filtering

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

## Explore

- Inspect which R3 prefixes reach R1.
- Edit the prefix-list and apply inbound/outbound policies.
- Use soft clear to re-evaluate policy without resetting TCP.

## Useful checks

- `docker exec clab-pp05-r1 vtysh -c "show bgp ipv4 unicast summary"`
- `docker exec clab-pp05-r1 vtysh -c "show bgp ipv4 unicast"`

## Baseline and policy checks

All eBGP directions have explicit policies. R2 exports only `3.3.3.3/32`
toward R1; R3 originates both `3.3.3.3/32` and `33.33.33.33/32`.
R1 should have its own loopback and only the first R3 prefix in BGP.
`Established` proves session establishment, not route exchange. `(Policy)` in
summary means a required policy is missing; numeric zero means no prefixes.

## Extended exercises

1. Add an exact permit for `33.33.33.33/32` to R2's `TO-R1` list.
   Predict R1's table, then check it. R2 should advertise two prefixes to R1.
2. In R2's privileged vtysh mode, run `clear bgp 10.0.12.1 soft out`.
   Compare neighbor uptime before/after: the session must stay established.
   Policy edits may already trigger updates automatically.
3. Keep both outbound permits on R2. Create a prefix-list and a route-map on
   R1 that accept only one R3 prefix; attach the map to R2 with `in`.
   R2 can advertise two while R1 accepts one. Compare both summaries.
4. Replace the allowed prefix on R1 without changing the neighbor binding.
   Verify the old route disappears and the new one appears.
5. Study prefix lengths: add `192.0.2.0/24`, `192.0.2.0/25`,
   `192.0.2.128/25`, and `192.0.2.64/26` to R3's loopback and originate them
   with BGP `network` statements. Each statement needs an exact route locally.
   Compare `permit 192.0.2.0/24`, `permit 192.0.2.0/24 le 25`, and
   `permit 192.0.2.0/24 ge 25 le 26` on R2. Temporarily restore R1's
   `ALLOW-ALL in` so that only the outbound filter is under test.
6. Put an explicit deny for `192.0.2.0/25` before a covering permit, then
   after it. Explain first-match processing and the implicit deny at the end.
   A route-map `match` succeeds only for prefixes permitted by its prefix-list;
   a denied match can continue to later route-map rules.

Success: explain the difference between a missing policy, a nonmatching
prefix-list entry, and a matching route-map deny. Show evidence at sender and
receiver, not just a successful ping.

## Persistence

vtysh changes are runtime changes. The startup configs are mounted read-only;
`write memory` is not the way to update these repository files. Record the
commands, edit `configs/r*.conf` on the host to preserve selected changes, then
destroy/deploy the lab to verify them. Redeployment otherwise restores this baseline.

Reference: [FRR BGP policies](https://docs.frrouting.org/en/stable-10.7/bgp.html).
