# Validation record

## Offline checks

Run from the repository root with Python 3 and PyYAML available:

```sh
make check
git diff --check
sha256sum -c MANIFEST.sha256
```

`make check` validates all 39 topologies, unique names/endpoints, local bind
sources, README index coverage, local lab links and shell-script syntax. Eight
unit tests include missing mounts, unknown/reused interfaces, accidental eth0
links, malformed command types and duplicate YAML keys. These checks do not
replace deployment. The new inline startup commands were also shell syntax checked.

## Runtime environment

Validation used Docker 29.9.2 on Linux, Containerlab 0.78.2 (container image),
Alpine 3.22 for new service nodes, and FRR 10.7.1 for BGP nodes. Existing Linux
labs used their default network-multitool image. Host kernel capabilities and
package/image versions can change behavior; throughput numbers are not portable.

Only test-created labs were modified. Existing exercises used isolated copies
named `ppcheck05`, `ppcheck20`, `ppcheck21`, `ppcheck22`, and `ppcheck24`, with
bind sources resolved to the repository. Test containers were destroyed afterward.

## Coverage

The table records executed assertions, not just successful container creation.

| Lab | Runtime checks |
|---|---|
| 05 | Initial R1 BGP table contains its own loopback and only `3.3.3.3/32`; explicit policy baseline |
| 20 | Inside-to-outside ping through NAT; conntrack available |
| 21 | Forwarded ping, stateful nftables rule and conntrack available |
| 22 | Small ping succeeds; 1400-byte DF payload fails at the MTU bottleneck |
| 24 | Advertised prefix produces a SLAAC address and an RA-learned default via link-local gateway |
| 30 | HTTP succeeds; closed port refuses; firewall drop times out; removing rule restores HTTP |
| 31 | TCP transfer before and during netem delay/loss; qdisc removal |
| 32 | Both BIND configs and zone validate; A, NXDOMAIN, empty AAAA answer, TCP DNS |
| 33 | dnsmasq configs validate; relayed DHCP supplies address/gateway/DNS; server ping and DNS resolution |
| 34 | Both source-policy routes; asymmetric reply works with filtering off, fails with strict and succeeds with loose rp_filter |
| 35 | Two-way cross-site traffic; restricting AllowedIPs breaks it; restoring AllowedIPs repairs it |
| 36 | Both VIPs on gw1; daemon failure moves both to gw2; traffic recovers; restart preempts; tracked link failure switches gateway |
| 37 | HTB+FIFO and HTB+fq_codel configurations carry TCP traffic; root qdisc removal |
| 38 | Restricted export, deliberate route leak, restrictive import, maximum-prefix shutdown and recovery |
| 39 | Working DNS/HTTP; each of five injected faults causes expected failure; targeted repairs restore service |

## Limits

Not every extended exercise is automated or executed. In particular: packet-by-
packet capture interpretation, DNS cache-expiry timing, DHCP lease renewal/expiry,
DSCP classification, quantitative QoS comparisons, NAT hairpin/DNAT, conntrack
entry deletion and the TCP PMTU-black-hole extension remain learner exercises.
Labs 01–04, 06–19 and 23/25–29 were not redeployed for this change; they received
offline checks only. Advanced EVPN/MPLS labs retain their experimental status.

The scenarios in lab 39 were injected and repaired individually on a working
test deployment; learners should redeploy between exam scenarios for a clean start.
Use each README's baseline and acceptance steps when reproducing the checks.
