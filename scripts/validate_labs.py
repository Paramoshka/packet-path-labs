#!/usr/bin/env python3
"""Offline structural checks; does not claim that protocols work at runtime."""
from pathlib import Path
import re
import subprocess

import yaml


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def validate(path):
    data = yaml.load(path.read_text(), Loader=UniqueLoader)
    topology = data['topology']
    nodes = topology['nodes']
    if not nodes:
        raise ValueError('empty topology')
    defaults = topology.get('defaults', {})
    used = set()
    for link in topology.get('links', []):
        endpoints = link['endpoints']
        if len(endpoints) != 2:
            raise ValueError('link must have two endpoints')
        for endpoint in endpoints:
            name, interface = endpoint.split(':', 1)
            if name not in nodes or not interface or interface == 'eth0':
                raise ValueError(f'invalid data endpoint: {endpoint}')
            if endpoint in used:
                raise ValueError(f'endpoint reused: {endpoint}')
            used.add(endpoint)
    for name, config in nodes.items():
        config = config or {}
        settings = {**defaults, **config}
        if not settings.get('kind') or (settings['kind'] != 'host' and not settings.get('image')):
            raise ValueError(f'{name}: missing kind/image')
        for command in settings.get('exec', []):
            if not isinstance(command, str):
                raise ValueError(f'{name}: exec command is not a string')
        for mount in defaults.get('binds', []) + config.get('binds', []):
            source = mount.split(':', 1)[0]
            if '$' in source:
                raise ValueError(f'{name}: cannot validate dynamic bind source: {source}')
            if not (path.parent / source).exists():
                raise ValueError(f'{name}: missing bind source: {source}')
    if not (path.parent / 'README.md').is_file():
        raise ValueError('missing README.md')
    return data['name']


def main():
    root = Path(__file__).resolve().parents[1]
    names = set()
    paths = sorted((root / 'labs').glob('*/lab.clab.yml'))
    for path in paths:
        try:
            name = validate(path)
            if name in names:
                raise ValueError(f'duplicate lab name: {name}')
            names.add(name)
        except (ValueError, KeyError, TypeError, yaml.YAMLError) as error:
            raise SystemExit(f'{path.relative_to(root)}: {error}') from error
        if f'(labs/{path.parent.name}/)' not in (root / 'README.md').read_text():
            raise SystemExit(f'{path.parent.name}: absent from lab index')
    for path in (root / 'labs').glob('*/**/*.sh'):
        if any(part.startswith('clab-') for part in path.parts):
            continue
        subprocess.run(['sh', '-n', str(path)], check=True)
    for path in (root / 'labs').glob('*/README.md'):
        for target in re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', path.read_text()):
            if '://' not in target and not (path.parent / target).exists():
                raise SystemExit(f'{path}: broken local link: {target}')
    print(f'Validated {len(paths)} topologies, index entries, bind sources, links and shell syntax.')


if __name__ == '__main__':
    main()
