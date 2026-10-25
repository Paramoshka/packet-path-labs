# Lab 36 — VRRP gateway failover

Move a virtual gateway between two routers without reconfiguring endpoints.
Prerequisites: labs 01–02 and 09. Two switches are Linux bridges inside containers.

## Topology

Client `10.36.0.10` uses VIP `10.36.0.1`; server `10.36.1.10` uses VIP
`10.36.1.254` for the return path. gw1 owns `.2` on both LANs, gw2 owns `.3`.
Two synchronized VRRP instances keep both VIPs on the same active gateway.
With both healthy, gw1's priority 150 beats gw2's 100.

## Experiments

1. Inspect `ip -4 addr` on both gateways. After election, both VIPs should be
   on gw1 only. Ping `10.36.1.10` continuously from client and capture ARP/VRRP
   on lan's br0. VRRP here uses configured unicast peers.
2. Stop keepalived on gw1 using `pkill -TERM keepalived` inside gw1. Measure
   packet loss and observe VIPs/neighbor-cache changes. A graceful stop can
   fail over faster than an unannounced failure; do not infer a universal timeout.
3. Restart it with `keepalived --use-file=/etc/lab/keepalived.conf --log-console`.
   Observe default preemption and gw1 taking the addresses back.
4. Drop gw1 eth2 with `ip link set eth2 down`. Confirm interface tracking
   moves both instances to the backup. Restore with `ip link set eth2 up`.
   Do not stop/start the Docker container: that is not a link-restoration test.
5. Discuss why losing VRRP advertisements alone can cause two active nodes,
   and why moving an IP does not synchronize NAT/conntrack session state.

## Acceptance

Traffic recovers through gw2 with unchanged endpoint routes. Show that both
VIPs move, the backup forwards real traffic, and recovery/preemption behaves
as configured. Keepalived syntax: `keepalived --config-test -f /etc/lab/keepalived.conf`.

Reference: [Keepalived VRRP configuration](https://www.keepalived.org/documentation/keepalived-conf/).

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
