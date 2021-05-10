import typing
from abc import ABC, abstractmethod

__all__ = ['BaseProcessor', 'BasePlainTextProcessor', 'check_args_range']


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


def check_args_range(nargs, lo, hi):
    if nargs > hi:
        raise ValueError("too much arguments")
    elif nargs < lo:
        raise ValueError("too less arguments")


if typing.TYPE_CHECKING:
    from clipbench import ClipboardWorkbench
