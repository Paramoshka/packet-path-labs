# Lab 38 — BGP route leaks and prefix limits

A multihomed customer must not accidentally become transit between providers.
Prerequisites: labs 04–07 and 18. This lab uses FRR, not Alpine package installation.

## Topology

`origin AS65004 — up1 AS65002 — customer AS65001 — up2 AS65003`

Origin advertises `198.51.100.0/24`. Customer owns `203.0.113.0/24` and learns
origin's prefix from up1. Initially customer exports only its own prefix to up2.
The up2 import is deliberately permissive so the export failure is observable.
The isolated documentation prefixes are never connected to real BGP neighbors.

## Experiments

1. Inspect customer and up2 BGP tables. Customer knows both prefixes; up2 knows
   only `203.0.113.0/24`. Check the outgoing OWN-ONLY map on customer.
2. On customer replace the outbound map for `10.38.34.2` with ALLOW-ALL.
   Soft-refresh out toward up2. Now up2 should learn `198.51.100.0/24` with
   AS path `65001 65002 65004`: provider-learned reachability leaked through a customer.
3. On up2 create an inbound prefix-list/route-map permitting only the customer's
   `203.0.113.0/24` from neighbor `10.38.34.1`. Re-evaluate inbound routes.
   The leaked route should disappear even while customer still sends it.
4. Restore the permissive import temporarily. On up2 configure
   `neighbor 10.38.34.1 maximum-prefix 1` in IPv4 unicast. Receiving the two
   accepted prefixes should exceed the limit and shut down the session.
   Inspect neighbor details/logs. A prefix limit is not a prefix authorization rule.
5. Restore customer's OWN-ONLY export before clearing the session. Keep limit 1
   and confirm the session recovers with one accepted route. Then restore the
   restrictive import on up2 as a second independent defense.

## Acceptance

Capture the leaked AS path, prove both export/import protection, trigger the
limit and recover without immediately repeating the fault. Explain why RPKI
origin validation alone would not identify every route leak: a leak can retain
an authorized origin AS. RPKI infrastructure is outside this lab.

Reference: [FRR BGP](https://docs.frrouting.org/en/stable-10.7/bgp.html).

## Lifecycle

From this directory:

```sh
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

Run host-side `docker exec` commands as a user with Docker access. Commands
inside a node affect that container, not the host. This lab uses the FRR image;
Internet access is needed only if the image must be pulled.
Runtime edits disappear on destroy/deploy. Save intentional changes in the
mounted source configs or topology and verify them with a fresh deployment.
