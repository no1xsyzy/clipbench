from ._base import BaseBuffer
from .plain_text import PlainTextBuffer
from .html import HtmlBuffer
from .hex import HexBuffer

_registry = {
    'text/plain': {
        '': PlainTextBuffer,
        'HexDump': HexBuffer,
    },
    'text/html': {
        '': HtmlBuffer,
        'PlainText': PlainTextBuffer,
        'HexDump': HexBuffer,
    },
}


def possible_editors(mime_formats):
    result = []
    for mime_format in mime_formats:
        if mime_format in _registry:
            for exp, buffer in _registry[mime_format].items():
                result.append((mime_format, exp, buffer))
        else:
            result.append((mime_format, 'HexDump', HexBuffer))
    return result