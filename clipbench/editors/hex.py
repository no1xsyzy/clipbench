from weakref import ref

from PyQt5.QtWidgets import QTextEdit

from ._base import BaseBuffer
from ._helpers import from_hex_dump, to_hex_dump


class HexBuffer(BaseBuffer):
    widget: QTextEdit

    def __init__(self):
        super().__init__()
        self.widget = QTextEdit()
        self_ref = ref(self)

        @self.widget.textChanged.connect
        def scp():
            self_ref().changed.emit()

    def set_content(self, content):
        self.widget.setPlainText(to_hex_dump(content))

    def get_content(self):
        return from_hex_dump(self.widget.toPlainText())
