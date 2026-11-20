"""Tests for the offline packet-path animation generator."""
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml
from gen_animations import generate, load_scenario, step_times, value_track


class GenAnimationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name)
        (self.lab / 'lab.clab.yml').write_text(yaml.safe_dump({
            'name': 'test', 'topology': {
                'defaults': {'kind': 'linux', 'image': 'alpine:3.22'},
                'nodes': {'a': {}, 'b': {}},
                'links': [{'endpoints': ['a:eth1', 'b:eth1']}]}}))
        self.scenario = {
            'title': 'test path',
            'steps': [{'text': 'a sends to b', 'packets': [
                {'from': 'a', 'to': 'b', 'kind': 'icmp', 'label': 'echo', 'dur': 1.5}]}],
            'badges': [{'node': 'a', 'text': 'sender', 'kind': 'icmp', 'steps': [0, 1]}],
        }
        self.write_scenario()

    def write_scenario(self):
        (self.lab / 'animation.yml').write_text(yaml.safe_dump(self.scenario))

    def test_deterministic_wellformed_svg(self):
        first = generate(self.lab)
        self.assertEqual(first, generate(self.lab))
        self.assertEqual(sorted(first), ['packet-path.dark.svg', 'packet-path.light.svg'])
        for name, content in first.items():
            root = ET.fromstring(content)
            self.assertTrue(root.tag.endswith('svg'))
            self.assertNotIn('<script', content)
            self.assertNotIn('foreignObject', content)
            self.assertIn('<animateMotion', content)
            self.assertIn('<animate ', content)
            self.assertIn('repeatCount="indefinite"', content)

    def test_themes_use_their_palette(self):
        outputs = generate(self.lab)
        self.assertIn('#0d1117', outputs['packet-path.dark.svg'])
        self.assertIn('#ffffff', outputs['packet-path.light.svg'])

    def test_unknown_node_rejected(self):
        self.scenario['steps'][0]['packets'][0]['to'] = 'ghost'
        self.write_scenario()
        with self.assertRaisesRegex(ValueError, 'unknown node'):
            load_scenario(self.lab)

    def test_non_adjacent_leg_rejected(self):
        self.scenario['steps'][0]['packets'] = [{'legs': [
            {'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'a'},
            {'from': 'a', 'to': 'b'}]}]
        self.write_scenario()
        load_scenario(self.lab)  # adjacent hops are fine
        topo = yaml.safe_load((self.lab / 'lab.clab.yml').read_text())
        topo['topology']['nodes']['c'] = {}
        (self.lab / 'lab.clab.yml').write_text(yaml.safe_dump(topo))
        self.scenario['steps'][0]['packets'][0]['legs'][1]['to'] = 'c'
        self.write_scenario()
        with self.assertRaisesRegex(ValueError, 'no topology link'):
            load_scenario(self.lab)

    def test_badge_window_out_of_range(self):
        self.scenario['badges'][0]['steps'] = [0, 5]
        self.write_scenario()
        with self.assertRaisesRegex(ValueError, 'steps must be'):
            load_scenario(self.lab)

    def test_layout_rows_must_cover_nodes(self):
        self.scenario['layout'] = {'rows': [['a']]}
        self.write_scenario()
        with self.assertRaisesRegex(ValueError, 'every topology node'):
            load_scenario(self.lab)

    def test_empty_steps_rejected(self):
        self.scenario['steps'] = []
        self.write_scenario()
        with self.assertRaisesRegex(ValueError, 'non-empty steps'):
            load_scenario(self.lab)

    def test_leg_pad_slows_every_hop(self):
        _, scenario, _, _ = load_scenario(self.lab)
        _, total = step_times(scenario)
        # pause .5 + authored 1.5 + pad .5 + hold 1.1 + tail .9
        self.assertAlmostEqual(total, 4.5)

    def test_value_track_monotonic_and_bounded(self):
        values, key_times = value_track([(2, 0), (2.2, 1), (5, 1), (5.2, 0)], 10, 0)
        keys = [float(k) for k in key_times.split(';')]
        vals = [float(v) for v in values.split(';')]
        self.assertEqual(len(keys), len(vals))
        self.assertEqual(keys[0], 0.0)
        self.assertEqual(keys[-1], 1.0)
        self.assertEqual(keys, sorted(keys))
        self.assertTrue(all(0 <= k <= 1 for k in keys))


if __name__ == '__main__':
    unittest.main()
