from weakref import ref

from PyQt5.QtWidgets import QTextEdit

from ._base import BaseBuffer
from ._helpers import decode


class HtmlBuffer(BaseBuffer):
    widget: QTextEdit
    enc: str
    apparent_enc: str

    def __init__(self, enc=""):
        super().__init__()
        self.widget = QTextEdit()
        self.enc = enc
        self.apparent_enc = ""
        self_ref = ref(self)

        @self.widget.textChanged.connect
        def scp():
            self_ref().changed.emit()

    def set_content(self, content):
        self.apparent_enc, html = decode(content, self.enc)
        self.widget.setHtml(html)

    def get_content(self):
        if self.apparent_enc == "":
            raise ValueError("get_content before set_content, thus unknown encoding")
        return self.widget.toHtml().encode(self.apparent_enc)
