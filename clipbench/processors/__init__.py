import importlib
import typing
from typing import Optional

import inflection

from . import line
from ._base import BaseProcessor

__all__ = ['command_alias', 'all_commands', 'solve_alias', 'solve_command_object', 'run', 'auto_complete']

command_alias = {
    'r.prefix': 'line.add_prefix',
    'r.suffix': 'line.add_suffix',
    'r.replace': 'line.replace',
    'r.s': 'line.sub',
    's': 'r.s',
    'r.grep': 'line.only_keep_lines_containing_regex',
    'grep': 'r.grep',
}

all_commands = []

_set_cmd = set(all_commands)

for k, v in command_alias.items():
    for cmd in [k, v]:
        if cmd not in _set_cmd:
            all_commands.append(cmd)
            _set_cmd.add(cmd)

del k, v, cmd, _set_cmd


def solve_alias(command: str) -> str:
    while command in command_alias:
        command = command_alias[command]
    return command


def solve_command_object(command: str) -> Optional[BaseProcessor]:
    if "." not in command:
        return None
    module, processor = command.rsplit(".", 1)
    mod = importlib.import_module("." + module, __name__)
    pc = getattr(mod, inflection.camelize(processor))
    if pc is None:
        return None
    return pc()


def run(args: list[str], clipbench: 'ClipboardWorkbench'):
    if not args:
        raise ValueError("empty line")
    alias = args[0]
    command = solve_alias(alias)
    p = solve_command_object(command)
    if p is None or not p.available(clipbench.current_format):
        raise ValueError(f"no such command: `{alias}`")
    p.process(args, clipbench)


def auto_complete(args: list[str], index: (int, int)) -> list[str]:
    if index[0] == 0:
        if len(args) == 0:
            return all_commands
        else:
            return [command for command in all_commands
                    if command.startswith(args[0][:index[1]]) and command.endswith(args[0][index[1]:])]
    command = solve_alias(args[0])
    p = solve_command_object(command)
    p.auto_complete(args, index)


if typing.TYPE_CHECKING:
    from clipbench import ClipboardWorkbench
