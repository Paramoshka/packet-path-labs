#!/bin/sh
set -eu
umask 077
wg genkey > /tmp/wg-private
wg pubkey < /tmp/wg-private > /tmp/wg-public
ip link add wg0 type wireguard
wg set wg0 private-key /tmp/wg-private listen-port 51820
ip addr add 10.35.255.2/30 dev wg0
ip link set wg0 mtu 1420 up
