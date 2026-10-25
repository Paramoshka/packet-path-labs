# Lab 30 — TCP lifecycle

Observe connection establishment, orderly close, reset and timeout.
Prerequisites: labs 01–02; lab 21 provides optional firewall background.

## Topology and baseline

`client 10.30.0.1/24 — server 10.30.0.2/24:8080`

A small HTTP server listens on TCP/8080. Nothing listens on TCP/8081.
Management eth0 is not part of the experiment.

## Experiments

1. In one host terminal capture `docker exec clab-pp30-server tcpdump -ni eth1 -nn 'tcp port 8080 or tcp port 8081'`.
2. In another run `docker exec clab-pp30-client curl --max-time 5 http://10.30.0.2:8080/`.
   Find SYN, SYN/ACK, ACK, request/response, and FIN/ACK. Explain both sequence
   spaces. Packet grouping can differ because of segmentation/offloads.
3. Connect to port 8081 instead. Expect a prompt connection-refused error and
   RST,ACK from the server, rather than a retransmission timeout.
4. On server add `iptables -I INPUT -i eth1 -p tcp --dport 8080 -j DROP`.
   Repeat the bounded curl. Expect timeout and retransmitted SYNs; ICMP ping
   should still work. Restore with the identical command using `-D INPUT`.
5. Inspect `ss -tan` on both endpoints. Explain why TIME-WAIT is not a failed
   connection. Repeat with simultaneous clients to distinguish flows by ports.

## Acceptance

HTTP returns `packet-path-labs`. Show captures for successful connection,
closed port and silently filtered port. Diagnose each without relying only on ping.

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
