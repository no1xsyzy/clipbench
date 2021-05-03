from math import ceil

import chardet


def to_hex_dump(b: bytes):
    ss = []
    lenn = ceil(len(b).bit_length() / 4 - 1)
    n = 0
    while b:
        ss.append(
            hex(n)[2:].rjust(lenn, "0") +
            " | " +
            " ".join(("0" + hex(c)[2:])[-2:] for c in b[:16]).ljust(48) +
            "| " +
            ''.join(byte_to_char(c) for c in b[:16])
        )
        b = b[16:]
        n += 1
    return "\n".join(ss)


def byte_to_char(c: int):
    try:
        c = bytes([c]).decode('ascii')
        if c.isprintable():
            return c
        else:
            return '.'
    except UnicodeDecodeError:
        return '.'


def from_hex_dump(ss: str):
    return bytes([int(c, 16) for s in ss.split("\n") for c in s.split("|")[1].strip().split(" ")])


def decode(b: bytes, given_enc: str = ""):
    if given_enc != "":
        enc = given_enc
    else:
        enc = chardet.detect(b)['encoding']
    s = b.decode(enc)
    return enc, s
