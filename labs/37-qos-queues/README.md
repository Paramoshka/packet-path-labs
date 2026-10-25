# Lab 37 — QoS and queueing delay

Compare FIFO queueing with fair queueing at the same bottleneck rate.
Prerequisites: lab 31.

## Topology

`h1 10.37.1.2 — r1 — h2 10.37.2.2 (iperf3 server)`

## Experiments

1. On r1 create an HTB root and a 10 Mbit/s class:
   `tc qdisc add dev eth2 root handle 1: htb default 10`, then
   `tc class add dev eth2 parent 1: classid 1:10 htb rate 10mbit ceil 10mbit`.
2. Attach a FIFO: `tc qdisc add dev eth2 parent 1:10 handle 10: pfifo limit 1000`.
   From h1 run `iperf3 -c 10.37.2.2 -t 30`; concurrently ping h2 from h1.
   Record idle/loaded latency and `tc -s qdisc show dev eth2` on r1.
3. Replace only the child queue: first
   `tc qdisc del dev eth2 parent 1:10`, then
   `tc qdisc add dev eth2 parent 1:10 handle 10: fq_codel`.
   Repeat with the same class rate, endpoints and duration. Compare loaded
   latency, backlog, drops and goodput. Fair queueing is not itself a rate limiter.
4. Optional: add another HTB class and classify DSCP-marked traffic into it.
   Show that marking alone changes no scheduling until a filter uses the mark.
5. Remove the root qdisc to reset: `tc qdisc del dev eth2 root`.

## Acceptance

Show both configurations at the same shaped rate and explain the latency tradeoff.
A lower drop count alone does not prove a better queue. Do not expect physical
NIC performance from a virtual topology. HTB/fq_codel require host kernel support.

Reference: [tc](https://www.man7.org/linux/man-pages/man8/tc.8.html).

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
