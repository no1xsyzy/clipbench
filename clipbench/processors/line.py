import re

from PyQt5.QtWidgets import QTextEdit

from ._base import *


def with_each_line(func, buffer_widget):
    text = buffer_widget.toPlainText()
    buffer_widget.setPlainText(''.join(func(s) + ss[len(s):]
                                       for s, ss in zip(text.splitlines(), text.splitlines(True))))


class AddPrefix(BasePlainTextProcessor):
    def process(self, args, buffer_widget: QTextEdit):
        check_args_range(len(args), 2, 2)
        prefix = args[1]
        with_each_line(lambda line: prefix + line, buffer_widget)

    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]:
        return []


class AddSuffix(BasePlainTextProcessor):
    def process(self, args, buffer_widget: QTextEdit):
        check_args_range(len(args), 2, 2)
        suffix = args[1]
        with_each_line(lambda line: line + suffix, buffer_widget)

    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]:
        return []


class Replace(BasePlainTextProcessor):
    def process(self, args, buffer_widget):
        check_args_range(len(args), 3, 3)
        _, from_, to = args
        with_each_line(lambda line: line.replace(from_, to), buffer_widget)

    def auto_complete(self, args, index):
        return []


class Sub(BasePlainTextProcessor):
    def process(self, args, buffer_widget):
        check_args_range(len(args), 3, 3)
        _, from_, to = args
        with_each_line(lambda line: re.sub(from_, to, line), buffer_widget)

    def auto_complete(self, args, index):
        return []
