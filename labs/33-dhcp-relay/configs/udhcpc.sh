#!/bin/sh
set -eu
case "$1" in
    deconfig)
        ip -4 addr flush dev "$interface" scope global
        ;;
    bound|renew)
        ip -4 addr flush dev "$interface" scope global
        ip addr add "$ip/24" dev "$interface"
        # This lab offers exactly one gateway and a /24 mask.
        ip route replace default via "$router" dev "$interface"
        printf 'address=%s gateway=%s dns=%s lease=%s\n' "$ip" "$router" "$dns" "$lease" > /tmp/dhcp-options
        : > /etc/resolv.conf
        for server in $dns; do printf 'nameserver %s\n' "$server" >> /etc/resolv.conf; done
        ;;
esac
