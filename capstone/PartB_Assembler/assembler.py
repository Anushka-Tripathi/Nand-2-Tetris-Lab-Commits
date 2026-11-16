#!/usr/bin/env python3
"""
Hack Assembler  (Nand to Tetris - ETCCNT301 Capstone)
Roll No: 2501730077   K = 77   K mod 3 = 2
Extra feature (K mod 3 == 2): print a WARNING if the same label is defined twice.

Usage:  python assembler.py Prog.asm      ->  writes Prog.hack
"""
import sys
import os

# ---------- lookup tables ----------
COMP = {
    '0': '0101010', '1': '0111111', '-1': '0111010',
    'D': '0001100', 'A': '0110000', '!D': '0001101', '!A': '0110001',
    '-D': '0001111', '-A': '0110011', 'D+1': '0011111', 'A+1': '0110111',
    'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
    'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101',
    'M': '1110000', '!M': '1110001', '-M': '1110011', 'M+1': '1110111',
    'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111',
    'D&M': '1000000', 'D|M': '1010101',
}
DEST = {
    '': '000', 'M': '001', 'D': '010', 'MD': '011',
    'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111',
}
JUMP = {
    '': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
    'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111',
}
PREDEFINED = {
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
    'SCREEN': 16384, 'KBD': 24576,
}
for _i in range(16):
    PREDEFINED['R%d' % _i] = _i


def valid_symbol(s):
    """Symbols: letters, digits, _ . $ : and must not start with a digit."""
    if not s or s[0].isdigit():
        return False
    return all(c.isalnum() or c in '_.$:' for c in s)


def clean(line):
    """Remove comments and all whitespace."""
    if '//' in line:
        line = line[:line.index('//')]
    return ''.join(line.split())


def assemble(lines):
    """Return (list_of_binary_strings, errors, warnings)."""
    errors, warnings = [], []
    symbols = dict(PREDEFINED)
    label_line = {}          # label -> source line where first defined
    code = []                # (source_line_no, cleaned_text)

    # ---------- FIRST PASS: comments/blank lines out, record labels ----------
    rom_addr = 0
    for no, raw in enumerate(lines, 1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith('('):
            if not text.endswith(')') or text.count('(') != 1 or text.count(')') != 1:
                errors.append("Line %d: invalid label '%s'" % (no, text))
                continue
            name = text[1:-1]
            if not valid_symbol(name):
                errors.append("Line %d: invalid label name '%s'" % (no, name))
                continue
            if name in label_line:                       # ---- EXTRA FEATURE ----
                warnings.append(
                    "Line %d: WARNING: label '%s' already defined on line %d "
                    "(keeping the first definition)" % (no, name, label_line[name]))
                continue
            if name in PREDEFINED:
                errors.append("Line %d: label '%s' clashes with a predefined symbol" % (no, name))
                continue
            label_line[name] = no
            symbols[name] = rom_addr                     # address of NEXT instruction
        else:
            code.append((no, text))
            rom_addr += 1

    # ---------- SECOND PASS: translate to 16 bits ----------
    next_var = 16
    out = []
    for no, text in code:
        if text.startswith('@'):
            sym = text[1:]
            if sym == '':
                errors.append("Line %d: invalid instruction '@' (missing value)" % no)
                continue
            if sym.isdigit():
                val = int(sym)
                if val > 32767:
                    errors.append("Line %d: constant %d too large (max 32767)" % (no, val))
                    continue
            elif valid_symbol(sym):
                if sym not in symbols:
                    symbols[sym] = next_var
                    next_var += 1
                val = symbols[sym]
            else:
                errors.append("Line %d: invalid instruction '%s'" % (no, text))
                continue
            out.append('0' + format(val, '015b'))
        else:
            dest, comp, jump = '', text, ''
            if '=' in comp:
                dest, comp = comp.split('=', 1)
            if ';' in comp:
                comp, jump = comp.split(';', 1)
            if dest not in DEST or comp not in COMP or jump not in JUMP:
                errors.append("Line %d: invalid instruction '%s'" % (no, text))
                continue
            out.append('111' + COMP[comp] + DEST[dest] + JUMP[jump])
    return out, errors, warnings


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.asm'):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.read().splitlines()
    except OSError as e:
        print("Cannot open file:", e)
        sys.exit(1)

    out, errors, warnings = assemble(lines)
    for w in warnings:
        print(w)
    if errors:
        for e in errors:
            print(e)
        print("Assembly failed with %d error(s); no .hack file written." % len(errors))
        sys.exit(1)

    hack = os.path.splitext(path)[0] + '.hack'
    with open(hack, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print("OK: %s -> %s (%d instructions)" % (path, hack, len(out)))


if __name__ == '__main__':
    main()