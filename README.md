# Packet Path Labs

A progressive set of **29 Containerlab networking exercises** using Linux and FRRouting (FRR). The repository starts with ARP and static routing, then moves through OSPF/BGP policy, VLAN/VRF, VXLAN/EVPN, IPv6, MPLS and leaf-spine fabrics.

The name is intentionally about the main question behind every lab: **what path does the packet take, and why?**

## Requirements

- Linux VM or host with Docker
- Containerlab
- `sudo` privileges
- Internet access for the initial image pulls (Labs 20–21 also install firewall packages with `apk` at deploy time)

Default images can be overridden with environment variables:

```bash
export FRR_IMAGE=quay.io/frrouting/frr:10.7.1
export LINUX_IMAGE=ghcr.io/srl-labs/network-multitool:latest
```

## Workflow

```bash
cd labs/04-ebgp-basics
sudo containerlab deploy -t lab.clab.yml
# explore the lab
sudo containerlab destroy -t lab.clab.yml
```

Or from the repository root:

```bash
make up LAB=04-ebgp-basics
make down LAB=04-ebgp-basics
make list
```

## Lab index

| Directory | Topic |
|---|---|
| [01-l2-arp-icmp](labs/01-l2-arp-icmp/) | L2, ARP and ICMP |
| [02-linux-router](labs/02-linux-router/) | Linux Router |
| [03-frr-ospf](labs/03-frr-ospf/) | FRR and OSPF |
| [04-ebgp-basics](labs/04-ebgp-basics/) | eBGP Basics |
| [05-bgp-filtering](labs/05-bgp-filtering/) | BGP Filtering |
| [06-bgp-localpref-med](labs/06-bgp-localpref-med/) | BGP Local Preference and MED |
| [07-bgp-communities](labs/07-bgp-communities/) | BGP Communities |
| [08-ecmp](labs/08-ecmp/) | ECMP |
| [09-ospf-convergence](labs/09-ospf-convergence/) | OSPF Failure and Convergence |
| [10-ospf-cost](labs/10-ospf-cost/) | OSPF Cost |
| [11-vlan-basics](labs/11-vlan-basics/) | VLAN Basics |
| [12-inter-vlan-routing](labs/12-inter-vlan-routing/) | Inter-VLAN Routing |
| [13-vrf](labs/13-vrf/) | VRF |
| [14-vxlan-basics](labs/14-vxlan-basics/) | VXLAN Basics |
| [15-vxlan-bridge](labs/15-vxlan-bridge/) | VXLAN Bridge and FDB |
| [16-evpn-vxlan](labs/16-evpn-vxlan/) | BGP EVPN + VXLAN |
| [17-route-reflector](labs/17-route-reflector/) | iBGP Route Reflector |
| [18-ibgp-ebgp](labs/18-ibgp-ebgp/) | iBGP + eBGP Together |
| [19-bfd](labs/19-bfd/) | BFD |
| [20-nat](labs/20-nat/) | NAT |
| [21-nftables-firewall](labs/21-nftables-firewall/) | nftables Firewall |
| [22-mtu-fragmentation](labs/22-mtu-fragmentation/) | MTU, Fragmentation and PMTUD |
| [23-traceroute-ttl](labs/23-traceroute-ttl/) | ICMP TTL and Traceroute |
| [24-ipv6-basics](labs/24-ipv6-basics/) | IPv6 Basics and NDP |
| [25-ospfv3](labs/25-ospfv3/) | OSPFv3 |
| [26-bgp-ipv6](labs/26-bgp-ipv6/) | BGP for IPv6 |
| [27-mpls-basics](labs/27-mpls-basics/) | MPLS Basics with LDP |
| [28-ebgp-leaf-spine](labs/28-ebgp-leaf-spine/) | eBGP Leaf-Spine Underlay |
| [29-evpn-leaf-spine](labs/29-evpn-leaf-spine/) | EVPN over a Leaf-Spine Underlay |

## Philosophy

Each lab is deliberately small. The topology and a working baseline are provided, but the real exercise is to **break, capture, inspect, modify and explain** the behavior with tools such as `tcpdump`, `ip`, `bridge`, `nft`, `vtysh` and Containerlab.

Advanced labs are starter designs rather than production reference architectures. In particular, EVPN/MPLS behavior can depend on the host kernel and FRR version; treat those labs as a foundation for experiments and Codex-assisted iteration.

## Validation note

All 29 topology files were YAML-parsed during generation. The advanced EVPN/MPLS labs are intentionally experimental starter labs and were not runtime-deployed in the generation environment; MPLS additionally requires MPLS support in the host kernel.
