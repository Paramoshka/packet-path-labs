# Lab 24 — IPv6 Basics and NDP

Repeat the first L2 lab with IPv6: link-local addresses, Neighbor Discovery and ICMPv6 replace IPv4 ARP behavior.

## Topology

```text
h1 2001:db8:1::1/64 ---- 2001:db8:1::2/64 h2
```

## Run

```bash
sudo containerlab deploy -t lab.clab.yml
sudo containerlab destroy -t lab.clab.yml
```

## Explore

- Inspect automatically created `fe80::/64` link-local addresses.
- Flush IPv6 neighbors and capture ICMPv6 Neighbor Solicitation/Advertisement.
- Compare NDP with ARP from Lab 01.

## Useful checks

- `docker exec clab-pp24-h1 ip -6 neigh`
- `docker exec clab-pp24-h1 ping -6 -c 2 2001:db8:1::2`

## Router advertisements and SLAAC

Keep the static-address baseline for NDP, then turn h1 into an advertising router.
Inside h1 install `dnsmasq`, enable IPv6 forwarding with
`sysctl -w net.ipv6.conf.all.forwarding=1`, and start the supplied RA configuration:

```sh
apk add --no-cache dnsmasq
ip -6 addr add 2001:db8:24::1/64 dev eth1
dnsmasq --conf-file=/etc/dnsmasq.conf
```

On h2 enable `net.ipv6.conf.eth1.accept_ra=2` and
`net.ipv6.conf.eth1.autoconf=1` using `sysctl -w`. Value 2 accepts RAs even if
forwarding is enabled in the container. Capture ICMPv6 on eth1 and wait for an
RA. Inspect `ip -6 addr show dev eth1` and `ip -6 route show dev eth1`.

Expected: h2 gets an additional address in `2001:db8:24::/64` and an RA-learned
default route via h1's link-local address. The existing static address remains.
Compare prefix valid/preferred lifetimes with router lifetime; a prefix and a
default router are different pieces of information. Stop dnsmasq, capture the
result and follow the route lifetime rather than assuming an immediate withdrawal.
No DHCPv6 server is involved: SLAAC creates the address and RA supplies the router.
Destroy/deploy restores the static NDP baseline.
