"""Failure-oriented tests for the offline topology checks."""
import tempfile
import unittest
from pathlib import Path

import yaml
from validate_labs import UniqueLoader, check_readme_media, validate


class ValidateLabsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'README.md').write_text('# Test lab\n')
        self.data = {'name': 'test', 'topology': {
            'defaults': {'kind': 'linux', 'image': 'alpine:3.22'},
            'nodes': {'a': {}, 'b': {}},
            'links': [{'endpoints': ['a:eth1', 'b:eth1']}]}}

    def check(self):
        path = self.root / 'lab.clab.yml'
        path.write_text(yaml.safe_dump(self.data))
        return validate(path)

    def test_valid_inherited_defaults(self):
        self.assertEqual(self.check(), 'test')

    def test_host_node_needs_no_image(self):
        del self.data['topology']['defaults']
        self.data['topology']['nodes'] = {'host': {'kind': 'host'}}
        self.data['topology']['links'] = []
        self.assertEqual(self.check(), 'test')

    def test_unknown_endpoint(self):
        self.data['topology']['links'][0]['endpoints'][1] = 'typo:eth1'
        with self.assertRaisesRegex(ValueError, 'invalid data endpoint'):
            self.check()

    def test_reused_interface(self):
        self.data['topology']['links'].append({'endpoints': ['a:eth1', 'b:eth2']})
        with self.assertRaisesRegex(ValueError, 'endpoint reused'):
            self.check()

    def test_management_link_rejected(self):
        self.data['topology']['links'][0]['endpoints'][0] = 'a:eth0'
        with self.assertRaisesRegex(ValueError, 'invalid data endpoint'):
            self.check()

    def test_missing_mount(self):
        self.data['topology']['nodes']['a']['binds'] = ['missing.conf:/etc/lab.conf:ro']
        with self.assertRaisesRegex(ValueError, 'missing bind source'):
            self.check()

    def test_yaml_command_must_be_string(self):
        self.data['topology']['nodes']['a']['exec'] = [{'echo': 'mistaken YAML mapping'}]
        with self.assertRaisesRegex(ValueError, 'exec command is not a string'):
            self.check()

    def test_duplicate_yaml_key(self):
        with self.assertRaisesRegex(ValueError, 'duplicate YAML key'):
            yaml.load('name: one\nname: two\n', Loader=UniqueLoader)

    def test_animation_scenario_is_validated(self):
        (self.root / 'animation.yml').write_text(yaml.safe_dump({
            'title': 'bad', 'steps': [{'text': 'x', 'packets': [
                {'from': 'a', 'to': 'ghost'}]}]}))
        with self.assertRaisesRegex(ValueError, 'unknown node'):
            self.check()

    def test_broken_img_src_rejected(self):
        path = self.root / 'README.md'
        path.write_text('<img src="missing.svg">\n')
        with self.assertRaisesRegex(SystemExit, 'broken local image'):
            check_readme_media(path)

    def test_broken_picture_srcset_rejected(self):
        path = self.root / 'README.md'
        path.write_text('<picture><source media="(prefers-color-scheme: dark)" '
                        'srcset="missing.dark.svg"><img src="ok.svg"></picture>\n')
        (self.root / 'ok.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>\n')
        with self.assertRaisesRegex(SystemExit, 'broken local image'):
            check_readme_media(path)

    def test_valid_picture_passes(self):
        path = self.root / 'README.md'
        for name in ('ok.light.svg', 'ok.dark.svg'):
            (self.root / name).write_text('<svg xmlns="http://www.w3.org/2000/svg"/>\n')
        path.write_text('<picture><source media="(prefers-color-scheme: dark)" '
                        'srcset="ok.dark.svg"><img src="ok.light.svg"></picture>\n')
        check_readme_media(path)


if __name__ == '__main__':
    unittest.main()
