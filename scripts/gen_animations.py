#!/usr/bin/env python3
"""Generate looping packet-path SVG animations for labs.

Each lab may carry an ``animation.yml`` scenario next to ``lab.clab.yml``.
This script turns the scenario plus the topology into deterministic
``packet-path.light.svg`` / ``packet-path.dark.svg`` files that the lab
README embeds with a ``<picture>`` element (GitHub renders both themes).

The SVGs use only basic shapes, text and SMIL animation elements — no
scripts, styles, defs or external references — so they survive GitHub's
SVG sanitization and animate inline when the README is viewed.

Usage:
    python3 scripts/gen_animations.py            # regenerate every lab
    python3 scripts/gen_animations.py --lab 01-l2-arp-icmp
    python3 scripts/gen_animations.py --check    # fail if files are stale
"""
import argparse
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

WIDTH = 800
NODE_W = 128
NODE_H = 56
ROW_GAP = 150
TOP_Y = 84
PAD_X = 84
FADE = 0.25
TAIL = 0.9

SANS = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', "
        'Helvetica, Arial, sans-serif')
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# kind -> (light accent, dark accent)
KINDS = {
    'arp': ('#bc4c00', '#f0883e'),
    'icmp': ('#1a7f37', '#3fb950'),
    'tcp': ('#0969da', '#58a6ff'),
    'udp': ('#8250df', '#bc8cff'),
    'vxlan': ('#0e7490', '#39c5cf'),
    'bgp': ('#cf222e', '#f85149'),
    'ospf': ('#9a6700', '#d29922'),
    'vrrp': ('#bf3989', '#ff7b72'),
    'rst': ('#cf222e', '#f85149'),
    'data': ('#57606a', '#8b949e'),
}

THEMES = {
    'light': {
        'page': '#ffffff', 'node_fill': '#ffffff', 'node_stroke': '#d0d7de',
        'text': '#1f2328', 'muted': '#57606a', 'link': '#d0d7de',
        'progress': '#0969da',
    },
    'dark': {
        'page': '#0d1117', 'node_fill': '#161b22', 'node_stroke': '#30363d',
        'text': '#e6edf3', 'muted': '#8b949e', 'link': '#30363d',
        'progress': '#58a6ff',
    },
}


def fmt(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.')


def accent(kind, theme):
    pair = KINDS.get(kind)
    if pair is None:
        raise ValueError(f'unknown packet kind: {kind}')
    return pair[0 if theme == 'light' else 1]


def load_scenario(lab_dir):
    """Load and structurally validate animation.yml against the topology."""
    topo = yaml.safe_load((lab_dir / 'lab.clab.yml').read_text())
    scenario = yaml.safe_load((lab_dir / 'animation.yml').read_text())
    nodes = topo['topology']['nodes']
    links = set()
    ifaces = {}
    for link in topo['topology'].get('links', []):
        (a, ia), (b, ib) = (endpoint.split(':', 1) for endpoint in link['endpoints'])
        links.add(frozenset((a, b)))
        ifaces[frozenset((a, b))] = {a: ia, b: ib}

    def need_node(name, where):
        if name not in nodes:
            raise ValueError(f'{where}: unknown node {name!r}')

    def need_link(a, b, where):
        need_node(a, where)
        need_node(b, where)
        if frozenset((a, b)) not in links:
            raise ValueError(f'{where}: no topology link between {a} and {b}')

    steps = scenario.get('steps')
    if not isinstance(steps, list) or not steps:
        raise ValueError('scenario needs a non-empty steps list')
    for i, step in enumerate(steps):
        if not isinstance(step.get('text'), str) or not step['text']:
            raise ValueError(f'step {i}: missing caption text')
        for packet in step.get('packets', []):
            legs = packet.get('legs')
            if legs is None:
                targets = packet.get('to')
                targets = targets if isinstance(targets, list) else [targets]
                legs = [{'from': packet.get('from'), 'to': t} for t in targets]
            for leg in legs:
                need_link(leg.get('from'), leg.get('to'), f'step {i}')
                if leg.get('kind', 'data') not in KINDS:
                    raise ValueError(f'step {i}: unknown kind {leg.get("kind")!r}')
                if float(leg.get('dur', 1.6)) <= 0:
                    raise ValueError(f'step {i}: leg dur must be positive')

    n = len(steps)

    def window_steps(entry, where):
        bounds = entry.get('steps')
        if (not isinstance(bounds, list) or len(bounds) != 2
                or not all(isinstance(b, int) and 0 <= b <= n for b in bounds)
                or bounds[0] >= bounds[1]):
            raise ValueError(f'{where}: steps must be [start, end] within 0..{n}')

    for badge in scenario.get('badges', []):
        need_node(badge.get('node'), 'badge')
        window_steps(badge, 'badge')
    for dim in scenario.get('dim', []):
        need_node(dim.get('node'), 'dim')
        window_steps(dim, 'dim')
    for down in scenario.get('link_down', []):
        pair = down.get('link', [])
        if len(pair) != 2:
            raise ValueError('link_down: link must be [nodeA, nodeB]')
        need_link(pair[0], pair[1], 'link_down')
        window_steps(down, 'link_down')

    rows = scenario.get('layout', {}).get('rows')
    if rows is not None:
        flat = [name for row in rows for name in row]
        if sorted(flat) != sorted(nodes):
            raise ValueError('layout rows must list every topology node exactly once')
    return topo, scenario, links, ifaces


def layout_positions(topo, scenario, links):
    nodes = list(topo['topology']['nodes'])
    rows = scenario.get('layout', {}).get('rows')
    if rows is None:
        rows = auto_rows(nodes, links)
    positions = {}
    overrides = scenario.get('layout', {}).get('x', {})
    for r, row in enumerate(rows):
        count = len(row)
        for i, name in enumerate(row):
            x = WIDTH / 2 if count == 1 else PAD_X + i * (WIDTH - 2 * PAD_X) / (count - 1)
            if name in overrides:
                x = float(overrides[name])
            positions[name] = (round(x, 1), TOP_Y + r * ROW_GAP)
    return positions


def auto_rows(nodes, links):
    """Chain topologies become one row; anything else needs explicit rows."""
    adj = {name: set() for name in nodes}
    for pair in links:
        a, b = tuple(pair)
        adj[a].add(b)
        adj[b].add(a)
    if nodes and all(len(adj[name]) <= 2 for name in nodes):
        ends = sorted(name for name in nodes if len(adj[name]) <= 1)
        start = ends[0] if ends else sorted(nodes)[0]
        order, prev, cur = [start], None, start
        while True:
            nxt = [name for name in sorted(adj[cur]) if name != prev]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            order.append(cur)
        if len(order) == len(nodes):
            return [order]
    raise ValueError('cannot auto-layout this topology; set layout.rows in animation.yml')


def step_times(scenario):
    """Absolute start time of every step and the total loop duration."""
    starts, t = [], 0.0
    for step in scenario['steps']:
        starts.append(round(t, 3))
        pause = float(step.get('pause', 0.5))
        hold = float(step.get('hold', 1.1))
        t += pause
        span = float(step.get('dur', 0))
        for packet in step.get('packets', []):
            delay = float(packet.get('delay', 0))
            legs = packet_legs(packet)
            span = max(span, delay + sum(float(leg.get('dur', 1.6)) for leg in legs))
        t += span + hold
    return starts, round(t + TAIL, 3)


def packet_legs(packet):
    if 'legs' in packet:
        inherited = {k: packet[k] for k in ('label', 'kind') if k in packet}
        legs = [{**inherited, **leg} for leg in packet['legs']]
        # a label set on an early hop names the whole journey unless overridden
        carried = None
        for leg in legs:
            if 'label' in leg:
                carried = leg['label']
            elif carried is not None:
                leg['label'] = carried
        return legs
    targets = packet.get('to')
    targets = targets if isinstance(targets, list) else [targets]
    return [{'from': packet['from'], 'to': t, **{k: v for k, v in packet.items()
                                                  if k not in ('from', 'to', 'legs')}}
            for t in targets]


def value_track(points, total, default):
    """SMIL values/keyTimes for a piecewise value over one loop.

    points is a list of (absolute_time, value) changes; the track holds
    ``default`` until the first point and the last value until the loop end.
    """
    keys, vals = [0.0], [default]
    for t, v in sorted(points, key=lambda p: p[0]):
        t = min(max(float(t), 0.0), total)
        if t <= keys[-1]:
            vals[-1] = v
        else:
            keys.append(t)
            vals.append(v)
    if keys[-1] < total:
        keys.append(total)
        vals.append(vals[-1])
    key_times = ';'.join(fmt(t / total) for t in keys)
    values = ';'.join(fmt(v) for v in vals)
    return values, key_times


def window_points(windows, fade=FADE, low=0.0, high=1.0):
    points = []
    for start, end in windows:
        if end <= start:
            continue
        points += [(start, low), (min(start + fade, end), high),
                   (max(end - fade, start), high), (end, low)]
    return points


def animate(attribute, points, total, default, extra=''):
    values, key_times = value_track(points, total, default)
    return (f'<animate attributeName="{attribute}" values="{values}" '
            f'keyTimes="{key_times}" dur="{fmt(total)}s" '
            f'repeatCount="indefinite"{extra}/>')


def edge_point(center, toward, node_h=NODE_H, gap=3):
    cx, cy = center
    tx, ty = toward
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return center
    sx = (NODE_W / 2 + gap) / abs(dx) if dx else float('inf')
    sy = (node_h / 2 + gap) / abs(dy) if dy else float('inf')
    s = min(sx, sy)
    return (round(cx + dx * s, 1), round(cy + dy * s, 1))


def pill_width(text, char_w=6.4, pad=16):
    return round(char_w * len(text) + pad, 1)


class Scene:
    def __init__(self, lab_dir, topo, scenario, links, ifaces):
        self.lab_dir = lab_dir
        self.topo = topo
        self.scenario = scenario
        self.links = links
        self.ifaces = ifaces
        self.positions = layout_positions(topo, scenario, links)
        self.starts, self.total = step_times(scenario)
        self.node_h = NODE_H
        if any(isinstance(v.get('sub'), list) and len(v['sub']) > 1
               for v in scenario.get('nodes', {}).values()):
            self.node_h = NODE_H + 14

    def step_window(self, bounds):
        a, b = bounds
        end = self.starts[b] if b < len(self.starts) else self.total
        return (self.starts[a], end)

    def height(self):
        bottom = max(y for _, y in self.positions.values()) + self.node_h / 2
        badge_slots = max((b.get('slot', 0) for b in self.scenario.get('badges', [])),
                          default=-1)
        bottom += 20 + 22 * (badge_slots + 1) if badge_slots >= 0 else 14
        return int(bottom + 74)

    def link_geometry(self, a, b):
        pa, pb = self.positions[a], self.positions[b]
        return (edge_point(pa, pb, self.node_h), edge_point(pb, pa, self.node_h))

    def render(self, theme):
        t = THEMES[theme]
        height = self.height()
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
               f'height="{height}" viewBox="0 0 {WIDTH} {height}" '
               f'font-family="{SANS}" role="img">',
               f'<title>{escape(self.scenario["title"])}</title>']
        out += self.render_links(theme, t)
        out += self.render_link_states(theme, t)
        out += self.render_packets(theme, t)
        out += self.render_nodes(theme, t)
        out += self.render_pulses(theme, t)
        out += self.render_badges(theme, t)
        # packet labels ride above the nodes so they are never clipped
        out += self.packet_labels
        out += self.render_captions(theme, t, height)
        out.append('</svg>')
        return '\n'.join(out) + '\n'

    def render_links(self, theme, t):
        out = []
        show_ifaces = self.scenario.get('iface_labels', len(self.links) <= 4)
        decorations = {frozenset(d['between']): d
                       for d in self.scenario.get('links', [])}
        for pair in sorted(self.links, key=sorted):
            a, b = sorted(pair)
            (x1, y1), (x2, y2) = self.link_geometry(a, b)
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                       f'stroke="{t["link"]}" stroke-width="2"/>')
            if show_ifaces:
                names = self.ifaces[pair]
                for node, (px, py), (qx, qy) in ((a, (x1, y1), (x2, y2)),
                                                 (b, (x2, y2), (x1, y1))):
                    lx = round(px + (qx - px) * 0.16, 1)
                    ly = round(py + (qy - py) * 0.16, 1)
                    dx, dy = qx - px, qy - py
                    length = max((dx * dx + dy * dy) ** 0.5, 0.001)
                    ox, oy = -dy / length * 11, dx / length * 11
                    if oy < 0:
                        ox, oy = -ox, -oy
                    out.append(f'<text x="{fmt(lx + ox)}" y="{fmt(ly + oy + 3)}" '
                               f'font-size="9.5" fill="{t["muted"]}" '
                               f'text-anchor="middle">{escape(names[node])}</text>')
            deco = decorations.get(pair)
            if deco and deco.get('label'):
                mx, my = round((x1 + x2) / 2, 1), round((y1 + y2) / 2, 1)
                label = deco['label']
                w = pill_width(label, 5.6, 14)
                gap = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                if w > gap - 8:
                    # narrow link: float the label above the node boxes
                    out.append(f'<text x="{mx}" y="{fmt(min(y1, y2) - self.node_h / 2 - 8)}" '
                               f'font-size="9.5" fill="{t["muted"]}" '
                               f'text-anchor="middle">{escape(label)}</text>')
                else:
                    out.append(f'<rect x="{fmt(mx - w / 2)}" y="{fmt(my - 9)}" '
                               f'width="{w}" height="18" rx="9" fill="{t["page"]}" '
                               f'stroke="{t["link"]}"/>')
                    out.append(f'<text x="{mx}" y="{fmt(my + 3.5)}" font-size="10" '
                               f'fill="{t["muted"]}" text-anchor="middle">{escape(label)}</text>')
        return out

    def render_link_states(self, theme, t):
        out = []
        # colored highlight while a packet traverses a link
        for start, end, kind, a, b in self.iter_legs():
            color = accent(kind, theme)
            (x1, y1), (x2, y2) = self.link_geometry(a, b)
            points = window_points([(start, end)], fade=0.12, high=0.55)
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                       f'stroke="{color}" stroke-width="3.5" stroke-linecap="round" '
                       f'opacity="0">{animate("opacity", points, self.total, 0)}</line>')
        # failed links: red dashed overlay plus a cross marker
        red = accent('rst', theme)
        for down in self.scenario.get('link_down', []):
            a, b = down['link']
            window = self.step_window(down['steps'])
            (x1, y1), (x2, y2) = self.link_geometry(a, b)
            mx, my = round((x1 + x2) / 2, 1), round((y1 + y2) / 2, 1)
            points = window_points([window])
            out.append(f'<g opacity="0">{animate("opacity", points, self.total, 0)}'
                       f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{red}" '
                       f'stroke-width="2.5" stroke-dasharray="6 5"/>'
                       f'<rect x="{fmt(mx - 10)}" y="{fmt(my - 10)}" width="20" height="20" '
                       f'rx="5" fill="{t["page"]}" stroke="{red}"/>'
                       f'<text x="{mx}" y="{fmt(my + 5)}" font-size="13" font-weight="700" '
                       f'fill="{red}" text-anchor="middle">&#215;</text></g>')
        return out

    def iter_legs(self):
        """Yield (start, end, kind, from, to) for every packet leg."""
        for i, step in enumerate(self.scenario['steps']):
            base = self.starts[i] + float(step.get('pause', 0.5))
            for packet in step.get('packets', []):
                t = base + float(packet.get('delay', 0))
                for leg in packet_legs(packet):
                    dur = float(leg.get('dur', 1.6))
                    yield (round(t, 3), round(t + dur, 3), leg.get('kind', 'data'),
                           leg['from'], leg['to'])
                    t += dur

    def render_nodes(self, theme, t):
        out = []
        dim_windows = {}
        for dim in self.scenario.get('dim', []):
            dim_windows.setdefault(dim['node'], []).append(self.step_window(dim['steps']))
        overrides = self.scenario.get('nodes', {})
        for name, (x, y) in self.positions.items():
            info = overrides.get(name, {})
            sub = info.get('sub', [])
            sub = [sub] if isinstance(sub, str) else sub
            h = self.node_h
            group = [f'<rect x="{fmt(x - NODE_W / 2)}" y="{fmt(y - h / 2)}" '
                     f'width="{NODE_W}" height="{h}" rx="10" fill="{t["node_fill"]}" '
                     f'stroke="{t["node_stroke"]}" stroke-width="1.5"/>',
                     f'<text x="{x}" y="{fmt(y - 6 if sub else y + 5)}" font-size="14.5" '
                     f'font-weight="600" fill="{t["text"]}" text-anchor="middle">'
                     f'{escape(name)}</text>']
            for j, line in enumerate(sub[:2]):
                group.append(f'<text x="{x}" y="{fmt(y + 12 + j * 14)}" font-size="10.5" '
                             f'fill="{t["muted"]}" text-anchor="middle">{escape(line)}</text>')
            windows = dim_windows.get(name)
            if windows:
                points = window_points(windows, low=1.0, high=0.4)
                out.append(f'<g opacity="1">{animate("opacity", points, self.total, 1)}'
                           + ''.join(group) + '</g>')
            else:
                out.append('<g>' + ''.join(group) + '</g>')
        return out

    def render_badges(self, theme, t):
        out = []
        for badge in self.scenario.get('badges', []):
            x, y = self.positions[badge['node']]
            slot = badge.get('slot', 0)
            by = y + self.node_h / 2 + 18 + slot * 23
            color = accent(badge.get('kind', 'data'), theme)
            text = badge['text']
            w = pill_width(text, 6.0, 18)
            window = self.step_window(badge['steps'])
            points = window_points([window])
            out.append(f'<g opacity="0">{animate("opacity", points, self.total, 0)}'
                       f'<rect x="{fmt(x - w / 2)}" y="{fmt(by - 10)}" width="{w}" '
                       f'height="20" rx="10" fill="{color}" fill-opacity="0.12" '
                       f'stroke="{color}" stroke-opacity="0.55"/>'
                       f'<text x="{x}" y="{fmt(by + 4)}" font-size="10.5" font-weight="600" '
                       f'fill="{color}" text-anchor="middle">{escape(text)}</text></g>')
        return out

    def render_packets(self, theme, t):
        out = []
        self.packet_labels = []
        for i, step in enumerate(self.scenario['steps']):
            base = self.starts[i] + float(step.get('pause', 0.5))
            for packet in step.get('packets', []):
                t0 = base + float(packet.get('delay', 0))
                for leg in packet_legs(packet):
                    dur = float(leg.get('dur', 1.6))
                    start, end = round(t0, 3), round(t0 + dur, 3)
                    glyph, label = self.render_leg(leg, start, end, theme, t)
                    out.append(glyph)
                    if label:
                        self.packet_labels.append(label)
                    t0 = end
        return out

    def render_pulses(self, theme, t):
        out = []
        for i, step in enumerate(self.scenario['steps']):
            base = self.starts[i] + float(step.get('pause', 0.5))
            for packet in step.get('packets', []):
                t0 = base + float(packet.get('delay', 0))
                for leg in packet_legs(packet):
                    if leg.get('pulse'):
                        out.append(self.render_pulse(leg['from'], t0, theme, t))
                    t0 += float(leg.get('dur', 1.6))
        return out

    def render_pulse(self, node, at, theme, t):
        x, y = self.positions[node]
        color = t['progress']
        end = min(at + 0.7, self.total)
        keys = ';'.join(fmt(v / self.total) for v in (0, at, end, self.total))
        return (f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="{color}" '
                f'stroke-width="2" opacity="0">'
                f'<animate attributeName="opacity" values="0;0.6;0;0" '
                f'keyTimes="{keys}" dur="{fmt(self.total)}s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="10;10;34;34" '
                f'keyTimes="{keys}" dur="{fmt(self.total)}s" repeatCount="indefinite"/>'
                f'</circle>')

    def render_leg(self, leg, start, end, theme, t):
        a, b = leg['from'], leg['to']
        x1, y1 = self.positions[a]
        x2, y2 = self.positions[b]
        kind = leg.get('kind', 'data')
        color = accent(kind, theme)
        label = leg.get('label', '')
        if leg.get('encap'):
            inner = accent(leg.get('inner', 'icmp'), theme)
            glyph = (f'<rect x="-15" y="-9" width="30" height="18" rx="4" '
                     f'fill="{t["page"]}" stroke="{color}" stroke-width="1.5"/>'
                     f'<rect x="-8" y="-4.5" width="16" height="9" rx="2" fill="{inner}"/>')
        else:
            glyph = f'<circle r="6.5" fill="{color}"/>'
        visibility = window_points([(start, end)], fade=0.12)
        motion = (f'<animateMotion path="M {x1} {y1} L {x2} {y2}" '
                  f'keyPoints="0;0;1;1" keyTimes="{self.motion_keys(start, end)}" '
                  f'calcMode="linear" dur="{fmt(self.total)}s" repeatCount="indefinite"/>')
        fade_in = animate('opacity', visibility, self.total, 0)
        glyph_group = f'<g opacity="0">{fade_in}{glyph}{motion}</g>'
        label_group = ''
        if label:
            w = pill_width(label, 6.3, 14)
            label_group = (f'<g opacity="0">{fade_in}'
                           f'<rect x="{fmt(-w / 2)}" y="-31" width="{w}" height="17" '
                           f'rx="8.5" fill="{t["page"]}" fill-opacity="0.92" '
                           f'stroke="{color}" stroke-opacity="0.35"/>'
                           f'<text y="-18.5" font-size="10.5" font-family="{MONO}" '
                           f'font-weight="600" fill="{color}" text-anchor="middle">'
                           f'{escape(label)}</text>{motion}</g>')
        return glyph_group, label_group

    def motion_keys(self, start, end):
        return ';'.join(fmt(v / self.total) for v in (0, start, end, self.total))

    def render_captions(self, theme, t, height):
        out = []
        steps = self.scenario['steps']
        title = f'{self.lab_dir.name.split("-", 1)[0]} · {self.scenario["title"]}'
        out.append(f'<text x="24" y="30" font-size="12.5" font-weight="600" '
                   f'fill="{t["muted"]}">{escape(title)}</text>')
        out.append(f'<text x="{WIDTH - 24}" y="30" font-size="11" fill="{t["muted"]}" '
                   f'text-anchor="end">&#8635; {fmt(self.total)}s loop</text>')
        caption_y = height - 40
        for i, step in enumerate(steps):
            start = self.starts[i]
            end = self.starts[i + 1] if i + 1 < len(steps) else self.total
            points = window_points([(start, end)])
            lines = textwrap.wrap(step['text'], width=104)[:3]
            block = []
            for j, line in enumerate(lines):
                block.append(f'<text x="{WIDTH / 2}" y="{caption_y + j * 17}" '
                             f'font-size="13" fill="{t["text"]}" text-anchor="middle">'
                             f'{escape(line)}</text>')
            out.append(f'<g opacity="0">{animate("opacity", points, self.total, 0)}'
                       + ''.join(block) + '</g>')
            chip = f'step {i + 1}/{len(steps)}'
            out.append(f'<g opacity="0">{animate("opacity", points, self.total, 0)}'
                       f'<text x="24" y="{height - 12}" font-size="10" '
                       f'fill="{t["muted"]}">{escape(chip)}</text></g>')
        out.append(f'<rect x="0" y="{height - 4}" width="0" height="3" rx="1.5" '
                   f'fill="{t["progress"]}" opacity="0.4">'
                   f'<animate attributeName="width" values="0;{WIDTH}" keyTimes="0;1" '
                   f'dur="{fmt(self.total)}s" repeatCount="indefinite"/></rect>')
        return out


def generate(lab_dir):
    topo, scenario, links, ifaces = load_scenario(lab_dir)
    scene = Scene(lab_dir, topo, scenario, links, ifaces)
    return {f'packet-path.{theme}.svg': scene.render(theme) for theme in THEMES}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab', help='only this lab directory name')
    parser.add_argument('--check', action='store_true',
                        help='verify committed SVGs match the scenarios')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    labs = sorted((root / 'labs').glob('*/animation.yml'))
    if args.lab:
        labs = [p for p in labs if p.parent.name == args.lab]
        if not labs:
            raise SystemExit(f'no animation.yml for {args.lab}')
    stale = []
    for path in labs:
        lab_dir = path.parent
        try:
            outputs = generate(lab_dir)
        except (ValueError, KeyError, TypeError, yaml.YAMLError) as error:
            raise SystemExit(f'{lab_dir.name}: {error}') from error
        for name, content in outputs.items():
            target = lab_dir / name
            if args.check:
                if not target.is_file() or target.read_text() != content:
                    stale.append(str(target.relative_to(root)))
            else:
                target.write_text(content)
    if args.check:
        if stale:
            raise SystemExit('stale animations: ' + ', '.join(stale))
        print(f'Animations up to date for {len(labs)} labs.')
    else:
        print(f'Generated animations for {len(labs)} labs.')


if __name__ == '__main__':
    main()
