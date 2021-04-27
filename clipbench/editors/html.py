from weakref import ref

from PyQt5.QtWidgets import QTextEdit

from ._base import BaseBuffer


class HtmlBuffer(BaseBuffer):
    widget: QTextEdit

    def __init__(self):
        super().__init__()
        self.widget = QTextEdit()
        self_ref = ref(self)

        @self.widget.textChanged.connect
        def scp():
            self_ref().changed.emit()

    def set_content(self, content):
        self.widget.setHtml(content.decode('utf-8'))

    def get_content(self):
        return self.widget.toHtml().encode('utf-8')
