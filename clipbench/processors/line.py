import re

from ._base import *


def map_line(func, buffer_widget):
    text = buffer_widget.toPlainText()
    buffer_widget.setPlainText(''.join(func(s) + ss[len(s):]
                                       for s, ss in zip(text.splitlines(), text.splitlines(True))))


def filter_line(func, buffer_widget):
    text = buffer_widget.toPlainText()
    text = ''.join(ss for s, ss in zip(text.splitlines(), text.splitlines(True)) if func(s))
    buffer_widget.setPlainText(text)


class AddPrefix(BasePlainTextProcessor):
    def process(self, args, clipbench):
        check_args_range(len(args), 2, 2)
        prefix = args[1]
        map_line(lambda line: prefix + line, clipbench.buffer.widget)

    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]:
        return []


class AddSuffix(BasePlainTextProcessor):
    def process(self, args, clipbench):
        check_args_range(len(args), 2, 2)
        suffix = args[1]
        map_line(lambda line: line + suffix, clipbench.buffer.widget)

    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]:
        return []


class Replace(BasePlainTextProcessor):
    def process(self, args, clipbench):
        check_args_range(len(args), 3, 3)
        _, from_, to = args
        map_line(lambda line: line.replace(from_, to), clipbench.buffer.widget)

    def auto_complete(self, args, index):
        return []


class Sub(BasePlainTextProcessor):
    def process(self, args, clipbench):
        check_args_range(len(args), 3, 3)
        _, from_, to = args
        map_line(lambda line: re.sub(from_, to, line), clipbench.buffer.widget)

    def auto_complete(self, args, index):
        return []


class OnlyKeepLinesContainingRegex(BasePlainTextProcessor):
    def process(self, args, clipbench):
        check_args_range(len(args), 2, 2)
        _, pattern = args
        filter_line(lambda line: re.search(pattern, line), clipbench.buffer.widget)

    def auto_complete(self, args, index):
        return []
