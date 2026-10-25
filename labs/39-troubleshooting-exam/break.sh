#!/bin/sh
# Run on the Docker host, only against a fresh pp39 lab. Instructor entry point.
set -eu
case "${1:-}" in
    A) docker exec clab-pp39-client ip route del 10.39.2.0/24 via 10.39.1.1 ;;
    B) docker exec clab-pp39-server ip route del 10.39.1.0/24 via 10.39.2.1 ;;
    C) docker exec clab-pp39-r1 iptables -I FORWARD -i eth1 -o eth2 -p tcp --dport 8080 -j DROP ;;
    D) docker exec clab-pp39-dns pkill -TERM dnsmasq ;;
    E) docker exec clab-pp39-server pkill -TERM -f 'python3 -m http.server' ;;
    *) echo 'usage: sh break.sh A|B|C|D|E (one fault per fresh deployment)' >&2; exit 2 ;;
esac
printf 'Scenario %s installed. Diagnose from the client.\n' "$1"
