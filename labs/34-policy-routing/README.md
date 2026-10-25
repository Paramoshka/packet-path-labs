# Lab 34 — Source policy routing and asymmetry

Choose an egress by source address and diagnose reverse-path filtering.
Prerequisites: labs 02 and 13.

## Topology

Client has `10.34.1.2/24` toward isp1 (`.1`) and `10.34.2.2/24` toward isp2 (`.1`).
Both ISPs connect to one server: isp1 uses `10.34.3.1/30` toward server
`10.34.3.2`, isp2 uses `10.34.4.1/30` toward server `10.34.4.2`. The server
owns `198.18.0.1/32` on loopback, reachable through either provider.
The main table initially sends that destination through isp1. No host default
route is modified. Reverse-path filtering starts disabled in these containers.

## Experiments

1. On client inspect `ip rule` and `ip route get 198.18.0.1`.
   Capture on both eth1/eth2 while pinging the destination.
2. Add table 101's connected route for `10.34.1.0/24 dev eth1` and a route for
   `198.18.0.1/32 via 10.34.1.1`. Do the equivalent in table 102 via eth2.
   Add rules with distinct priorities 101/102, selecting these tables for
   sources `10.34.1.2/32` and `10.34.2.2/32` respectively.
3. Compare `ip route get 198.18.0.1 from 10.34.1.2` and the `.2.2` source.
   Use `ping -I 10.34.1.2` and `ping -I 10.34.2.2` to prove both paths.
4. Remove the two source rules to return to the main-table baseline. On server
   replace the route to `10.34.1.0/24` with a route via `10.34.4.1 dev eth2`.
   Replies now travel server → isp2 → client eth2, while requests use client eth1.
5. On client set `net.ipv4.conf.eth2.rp_filter=1` with `sysctl -w`. Capture
   replies arriving on eth2 even though ping fails. Set it to 2 and repeat.
   Inspect both `conf.all.rp_filter` and the interface setting: Linux uses their max.

## Acceptance

Prove source-based choice with route lookup and capture. Explain why strict
reverse-path validation rejects the asymmetric reply and how loose validation
changes that check. Restore with destroy/deploy.

Reference: [Linux IP sysctls](https://docs.kernel.org/networking/ip-sysctl.html).

## Lifecycle

From this directory:

```sh
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

Run host-side `docker exec` commands as a user with Docker access. Commands
inside a node affect that container, not the host. New Linux nodes install
packages at deployment time; Internet access to Alpine repositories is required.
Runtime edits disappear on destroy/deploy. Save intentional changes in the
mounted source configs or topology and verify them with a fresh deployment.
