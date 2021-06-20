import re

from ._base import *


class AddPrefix(BasePlainTextProcessor):
    """Usage: add_prefix <prefix>"""

    def iterates(self, lines, opts):
        prefix = opts['<prefix>']
        for line in lines:
            yield [prefix + line]


class AddSuffix(BasePlainTextProcessor):
    """Usage: add_suffix <suffix>"""

    def iterates(self, lines, opts):
        suffix = opts['<suffix>']
        for line in lines:
            yield [line + suffix]


class Replace(BasePlainTextProcessor):
    """ Usage: replace <from> <to>"""

    def iterates(self, lines, opts):
        from_ = opts['<from>']
        to = opts['<to>']
        for line in lines:
            yield [line.replace(from_, to)]


class Sub(BasePlainTextProcessor):
    """Usage: s <from> <to>"""

    def iterates(self, lines, opts):
        from_ = opts['<from>']
        to = opts['<to>']
        for line in lines:
            yield [re.sub(from_, to, line)]


class OnlyKeepLinesContainingRegex(BasePlainTextProcessor):
    """Usage: grep <pattern>"""

    def iterates(self, lines, opts):
        pattern = opts['<pattern>']
        for line in lines:
            if re.search(pattern, line):
                yield [line]


class RemovePrefix(BasePlainTextProcessor):
    """Removes Prefix.

    Usage: remove_prefix [-fr] <prefix>

    Options:
      -f, --force   Do NOT skip line if prefix is not <prefix>
      -r, --regex   Treat <prefix> as prefix
    """

    def iterates(self, lines, opts):
        prefix = opts['<prefix>']
        force = opts['--force']
        regex = opts['--regex']
        if prefix == "":
            for line in lines:
                yield [line]
            return
        if not regex:
            prefix = re.escape(prefix)
        prefix = "^" + prefix
        for i, line in enumerate(lines):
            edited, n = re.subn(prefix, "", line, 1)
            if force and n == 0:
                raise ValueError(f"line {i + 1} does not contain prefix matching pattern `{prefix}`")
            yield [edited]


class RemoveSuffix(BasePlainTextProcessor):
    """Usage: remove_suffix [-fr] <suffix>

    Options:
      -f, --force   Do NOT skip line if suffix is not <suffix>
      -r, --regex   Treat <suffix> as suffix
    """

    def iterates(self, lines, opts):
        suffix = opts['<suffix>']
        force = opts['--force']
        regex = opts['--regex']
        if suffix == "":
            for line in lines:
                yield [line]
            return
        if not regex:
            suffix = re.escape(suffix)
        suffix = suffix + "$"
        for i, line in enumerate(lines):
            edited, n = re.subn(suffix, "", line, 1)
            if force and n == 0:
                raise ValueError(f"line {i + 1} does not contain prefix matching pattern `{suffix}`")
            yield [edited]


class Strip(BasePlainTextProcessor):
    """Usage: strip <strip>"""

    def iterates(self, lines, opts):
        strip = opts['<strip>']
        for line in lines:
            yield [line.strip(strip)]


class LeftStrip(BasePlainTextProcessor):
    """Usage: lstrip <strip>"""

    def iterates(self, lines, opts):
        strip = opts['<strip>']
        for line in lines:
            yield [line.lstrip(strip)]


class RightStrip(BasePlainTextProcessor):
    """Usage: rstrip <strip>"""

    def iterates(self, lines, opts):
        strip = opts['<strip>']
        for line in lines:
            yield [line.rstrip(strip)]
