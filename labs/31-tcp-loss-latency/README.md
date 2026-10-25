# Lab 31 — TCP under loss and latency

Measure throughput and retransmissions instead of treating reachability as performance.
Prerequisites: labs 22 and 30.

## Topology

`h1 10.31.1.2 — r1 (.1 on each subnet) — h2 10.31.2.2`

h2 runs an iperf3 server. The baseline has no artificial impairment.

## Experiments

1. Run `docker exec clab-pp31-h1 iperf3 -c 10.31.2.2 -t 10` and record throughput
   and retransmissions. Measure baseline RTT with ping.
2. On r1 run `tc qdisc replace dev eth2 root netem delay 50ms`.
   Repeat. This affects only packets leaving eth2: the added round-trip delay
   is approximately 50 ms, not 100 ms. Add the same on eth1 for both directions.
3. Replace eth2's qdisc with `tc qdisc replace dev eth2 root netem delay 50ms loss 1%`.
   Capture on r1 eth2 and compare TCP retransmissions, ACKs and transfer duration.
   Measurements vary; do not use an exact Mbps value as a pass criterion.
4. During a longer transfer inspect `ss -ti` on h1 for RTT, congestion window
   and retransmission information. Compare one flow with `iperf3 -P 4`.
5. On r1 delete the eth2 root qdisc (`tc qdisc del dev eth2 root`) and also
   eth1's if you added it. Verify latency and throughput return toward baseline.

## Acceptance

Provide a table of baseline / delay / delay+loss / restored results with RTT,
throughput and retransmissions. Explain why loss harms TCP even when ping replies.
Do not claim that four flows make the physical link four times faster.

Reference: [netem](https://www.man7.org/linux/man-pages/man8/tc-netem.8.html).

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
