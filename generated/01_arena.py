"""Codigo gerado automaticamente pelo compilador GameLang."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_origin = Path(globals().get('__file__', Path.cwd())).resolve().parent
for _candidate in (_origin, *_origin.parents):
    if (_candidate / 'gamelang').is_dir():
        sys.path.insert(0, str(_candidate))
        break

from gamelang.runtime import ExecutionResult, GameState


def run(touches=None):
    state = GameState()
    state.add_entity('player', {'health': 100, 'x': 0, 'y': 0})
    state.add_entity('enemy', {'health': 30, 'x': 0, 'y': 0})

    def _event_0(state):
        state.damage('player', 10)
        state.damage('enemy', 5)
        state.emit('colisao')
        state.emit(state.property('player.health'))
    state.add_event('player', 'enemy', _event_0)
    state.emit('arena pronta')
    for left, right in touches or []:
        state.touch(left, right)
    return ExecutionResult(state, list(state.output))


def main():
    parser = argparse.ArgumentParser(description='Programa gerado a partir de GameLang')
    parser.add_argument('--touch', action='append', default=[], metavar='A,B')
    parser.add_argument('--state-json', action='store_true')
    args = parser.parse_args()
    touches = [tuple(item.split(',', 1)) for item in args.touch]
    result = run(touches)
    for line in result.output:
        print(line)
    if args.state_json:
        print(json.dumps(result.snapshot(), ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
