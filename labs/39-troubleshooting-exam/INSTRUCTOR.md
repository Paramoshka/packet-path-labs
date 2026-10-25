# Instructor notes — spoilers

Deploy a fresh pp39 and check the working baseline before each scenario. The
fault script targets only fixed pp39 containers; it does not touch host networking.
Choose a scenario without naming its cause. Learner should inspect evidence
before changing state. Runtime changes are discarded by destroy/deploy.

| Scenario | Fault | Evidence | Minimal repair (inside indicated node) |
|---|---|---|---|
| A | Client's service-subnet route removed | `ip route get 10.39.2.10` uses management default; no SYN on lab link | client: `ip route add 10.39.2.0/24 via 10.39.1.1` |
| B | Server's return route removed | Request arrives; reply uses wrong interface | server: `ip route add 10.39.1.0/24 via 10.39.2.1` |
| C | Router drops TCP/8080 | Ping/DNS work; SYN on ingress but not egress, rule counter increases | r1: `iptables -D FORWARD -i eth1 -o eth2 -p tcp --dport 8080 -j DROP` |
| D | DNS service stopped | Direct HTTP works, DNS fails, no DNS listener | dns: `dnsmasq --conf-file=/etc/dnsmasq.conf` |
| E | HTTP service stopped | DNS works, TCP receives RST, no TCP/8080 listener | server: `nohup python3 -m http.server 8080 --directory /www > /tmp/http.log 2>&1 < /dev/null &` |

The management interface is deliberately retained for Docker operations. A
missing lab route may use that default route; this is a symptom, not evidence
that management is a valid data path. Do not accept "ping works" as final proof.
