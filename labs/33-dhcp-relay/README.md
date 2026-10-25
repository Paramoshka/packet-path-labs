# Lab 33 — DHCP across a router

Observe address leasing and a relay between two broadcast domains.
Prerequisites: labs 01–02 and 32.

## Topology

`client (DHCP) — relay 10.33.0.1 / 10.33.1.1 — server 10.33.1.2`

Only eth0 has an address on client initially. DHCP is scoped to lab interfaces;
never run these DHCP services on host interfaces or the management network.

## Experiments

1. Capture on relay eth1 and eth2 with `tcpdump -ni eth1 -vv 'udp port 67 or udp port 68'`
   (use a second terminal for eth2). Predict broadcast versus relayed traffic.
2. On client run `udhcpc -i eth1 -s /etc/lab/udhcpc.sh -f -n` and keep it running.
   The mounted hook is executable. Observe Discover, Offer, Request, ACK and
   the relay's giaddr. The hook deliberately supports this lab's fixed /24.
3. In another terminal inspect `ip -4 addr show eth1`, `ip route`,
   `/tmp/dhcp-options`, and `dig server.lab.test`. Expected lease: `.100`–`.150`,
   gateway `10.33.0.1`, DNS `10.33.1.2`. Ping the server.
4. Keep the foreground client alive through renewal (lease is two minutes).
   Compare initial broadcast exchange with renewal; inspect server lease file
   and `/var/log/dnsmasq.log`. Do not assume renewal uses the same broadcast path.
5. Stop the relay, terminate the DHCP client, flush its eth1 IPv4 address,
   and start udhcpc again. Explain why an unconfigured client cannot discover
   the remote server. Restore the relay
   using `dnsmasq --conf-file=/etc/dnsmasq.conf`.

## Acceptance

Explain why an ordinary IP router does not forward the initial broadcast,
which subnet the server selects from giaddr, and where gateway/DNS originate.
A client that exits after obtaining a lease cannot demonstrate renewal.

Reference: [dnsmasq manual](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html).

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
