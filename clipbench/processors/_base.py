import typing
from abc import ABC, abstractmethod

__all__ = ['BaseProcessor', 'BasePlainTextProcessor', 'check_args_range']

from docopt import docopt


class BaseProcessor(ABC):
    @abstractmethod
    def available(self, mime_format: str) -> bool: ...

    @abstractmethod
    def process(self, args: list[str], clipbench: 'ClipboardWorkbench'): ...

    @abstractmethod
    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]: ...


class BasePlainTextProcessor(BaseProcessor, ABC):
    def available(self, mime_format):
        if mime_format == "text/plain":
            return True
        return False

    def auto_complete(self, args, index):
        return []

    def process(self, args, clipbench):
        opts = docopt(self.__doc__, argv=args[1:])
        buffer_widget = clipbench.buffer.widget
        text = buffer_widget.toPlainText()
        buffer_widget.setPlainText(''.join(line + ss[len(s):]
                                           for s, ss, lines in zip(text.splitlines(),
                                                                   text.splitlines(True),
                                                                   self.iterates(text.splitlines(), opts))
                                           for line in lines))

    @abstractmethod
    def iterates(self, lines: typing.Iterable[str], opts: dict[str, typing.Any]) -> typing.Iterator[list[str]]: ...


def check_args_range(nargs, lo, hi):
    if nargs > hi:
        raise ValueError("too much arguments")
    elif nargs < lo:
        raise ValueError("too less arguments")


if typing.TYPE_CHECKING:
    from clipbench import ClipboardWorkbench
