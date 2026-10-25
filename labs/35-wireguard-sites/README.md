# Lab 35 — WireGuard site-to-site VPN

Connect two private LANs through an encrypted routed tunnel.
Prerequisites: labs 02, 20 and 22. Host kernel must support WireGuard; if interface
creation reports unsupported, load/install support on the lab host first.

## Topology and baseline

`h1 10.35.1.10 — gw1 — 198.51.100.0/30 — gw2 — h2 10.35.2.10`

Each gateway has wg0 with a fresh runtime key and tunnel address
`10.35.255.1/30` or `.2/30`. Peers are deliberately not configured yet:
WAN ping should work, cross-site ping should fail. Private keys stay in the
container; never commit them. Destroy/deploy generates new keys.

## Experiments

1. Read only `/tmp/wg-public` on each gateway and exchange the public keys.
2. On gw1 configure the peer:
   `wg set wg0 peer <GW2_PUBLIC_KEY> endpoint 198.51.100.2:51820 allowed-ips 10.35.255.2/32,10.35.2.0/24`.
   On gw2 use gw1's key, endpoint `198.51.100.1:51820`, and allowed prefixes
   `10.35.255.1/32,10.35.1.0/24`.
3. On gw1 add `ip route add 10.35.2.0/24 dev wg0`; on gw2 add the reverse
   `10.35.1.0/24` route through wg0. `wg set` itself does not install routes.
4. Ping `10.35.2.10` from h1. Check `wg show` for handshake and byte counters.
   Capture gw1 eth2 and wg0: outer UDP/51820 versus inner private IP packets.
5. Remove the remote LAN from one peer's AllowedIPs while keeping the route.
   Predict and verify failure. Restore it. Explain peer selection and validation
   of decrypted source addresses, not just the routing table.
6. Try DF pings of different sizes across sites; relate tunnel MTU to overhead.

## Acceptance

Both LANs communicate without NAT. A capture on WAN shows encrypted transport;
a capture on wg0 shows inner packets. Explain why a handshake alone does not
prove correct routes or AllowedIPs.

Reference: [WireGuard routing](https://www.wireguard.com/netns/).

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
