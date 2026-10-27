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
    state.add_entity('bot', {'health': 40, 'x': 0, 'y': 0})
    state.damage('bot', 8)
    state.move('bot', (0, 0))
    state.move('bot', (5, 2))
    state.emit(state.property('bot.health'))
    state.emit(state.property('bot.x'))
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
