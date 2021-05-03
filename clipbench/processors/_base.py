from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QWidget


class BaseProcessor(ABC):
    @abstractmethod
    def available(self, mime_format: str) -> bool: ...

    @abstractmethod
    def process(self, args: list[str], buffer_widget: QWidget): ...

    @abstractmethod
    def auto_complete(self, args: list[str], index: (int, int)) -> list[str]: ...


def check_args_range(nargs, lo, hi):
    if nargs > hi:
        raise ValueError("too much arguments")
    elif nargs < lo:
        raise ValueError("too less arguments")
