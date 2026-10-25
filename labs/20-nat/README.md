# Lab 20 — NAT

Translate an RFC1918 source address at a Linux router and observe conntrack/stateful return traffic.

## Topology

```text
inside 10.0.0.10 -- NAT -- 198.51.100.2 outside
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Capture inside and outside interfaces and compare source addresses.
- Inspect NAT rules and conntrack entries.
- Replace MASQUERADE with explicit SNAT as an exercise.

## Useful checks

- `docker exec clab-pp20-inside ping -c 2 198.51.100.2`
- `docker exec clab-pp20-nat iptables -t nat -nvL`

## DNAT and a published service

Keep the existing SNAT baseline. Start a TCP listener on inside port 8080
(`nc -l -p 8080`, restart after each connection). On `nat`, add a PREROUTING
DNAT rule for traffic arriving on `eth2` at `198.51.100.1:8080`, targeting
`10.0.0.10:8080`. Connect from `outside` to the published address.
Capture both router interfaces: the destination changes on ingress, and the
reply source is translated back. Inspect `conntrack -L -p tcp` on `nat`.
Expected: the client connects to the public address without knowing the private one.

## Hairpin NAT

Create a second LAN client in its own namespace inside the `inside` container:

```sh
ip netns add client
ip link add veth-host type veth peer name veth-client
ip link add br-lan type bridge
ip link set br-lan up
ip addr del 10.0.0.10/24 dev eth1
ip link set eth1 master br-lan
ip link set veth-host master br-lan
ip link set veth-host up
ip addr add 10.0.0.10/24 dev br-lan
ip route replace 198.51.100.0/24 via 10.0.0.1
ip link set veth-client netns client
ip -n client link set lo up
ip -n client link set veth-client up
ip -n client addr add 10.0.0.20/24 dev veth-client
ip -n client route add default via 10.0.0.1
```

From that namespace connect to `198.51.100.1:8080`. Extend DNAT to LAN ingress
on `nat` and observe why DNAT alone is insufficient: the server can reply
straight to `10.0.0.20`, bypassing the NAT router. Add narrowly scoped
POSTROUTING SNAT for the translated LAN-to-server flow, using `10.0.0.1`.
Expected: both directions now traverse the NAT router and the client sees a
reply from the public endpoint. Compare original/reply tuples in conntrack.
Do not masquerade all LAN traffic just to hide the return-path problem.

Destroy/deploy restores the baseline, including removal of the nested namespace.
Reference: [Netfilter connection tracking](https://conntrack-tools.netfilter.org/manual.html).
