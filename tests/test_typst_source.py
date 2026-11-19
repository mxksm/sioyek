#!/usr/bin/env python3
"""Real Tinymist -> PDF position -> headless Neovim integration test."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('typst_source', root / 'commands/typst_source.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

with tempfile.TemporaryDirectory(prefix='typst inverse ') as temporary:
    folder = Path(temporary).resolve()
    bridge.CACHE = folder / 'cache'
    source = folder / 'main.typ'
    child = folder / "chapter α's.typ"
    source.write_text('#set page(width: 300pt, height: 400pt, margin: 30pt)\n#include "chapter α\'s.typ"\n')
    child.write_text('Hello inverse search.\n\nSecond source paragraph.\n')
    module = root.parent / 'nvim/lua'
    startup = folder / 'init.lua'
    startup.write_text('package.path = ' + json.dumps(str(module / '?.lua') + ';') + ' .. package.path\n')
    server = str(folder / 'nvim.sock')
    editor = subprocess.Popen([bridge.executable('nvim'), '--headless', '-u', str(startup), '--listen', server],
                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    def remote(expression):
        return subprocess.check_output([bridge.executable('nvim'), '--server', server, '--remote-expr', expression],text=True).strip()
    try:
        deadline = time.monotonic()+5
        while not Path(server).exists() and time.monotonic()<deadline:
            time.sleep(.02)
        bridge.compile_pdf(argparse.Namespace(source=str(source), server=server, input=['now=test']))
        pdf = source.with_suffix('.pdf')
        meta = json.loads(bridge.registration(pdf).read_text())
        assert meta['args'][-1] == 'now=test'
        bridge.jump(argparse.Namespace(pdf=str(pdf),page=1,x=45,y=36))
        assert Path(remote("expand('%:p')")).resolve() == child
        assert remote("line('.')") == '1'
        # A different paragraph resolves to a different source line.
        bridge.jump(argparse.Namespace(pdf=str(pdf),page=1,x=45,y=53))
        assert remote("line('.')") == '3'
        # Reject changed includes rather than querying a layout newer than the PDF.
        original = child.read_text()
        child.write_text(original+'Changed.\n')
        try:
            bridge.jump(argparse.Namespace(pdf=str(pdf),page=1,x=45,y=36))
            raise AssertionError('Stale source was accepted')
        except RuntimeError as error:
            assert 'changed' in str(error)
        child.write_text(original)
        original_pdf = pdf.read_bytes()
        pdf.write_bytes(original_pdf + b'\n% changed')
        try:
            bridge.jump(argparse.Namespace(pdf=str(pdf),page=1,x=45,y=36))
            raise AssertionError('Stale PDF was accepted')
        except RuntimeError as error:
            assert 'changed' in str(error)
        pdf.write_bytes(original_pdf)
        editor.terminate()
        editor.wait(timeout=3)
        try:
            bridge.jump(argparse.Namespace(pdf=str(pdf),page=1,x=45,y=36))
            raise AssertionError('Closed editor was accepted')
        except RuntimeError as error:
            assert 'no longer available' in str(error)
        print('PASS: actual PDF coordinates, included Unicode/spaced path, two paragraphs, '
              'Neovim jump, stale source/PDF rejection, closed editor feedback')
    finally:
        editor.terminate()
        try:
            editor.wait(timeout=3)
        except subprocess.TimeoutExpired:
            editor.kill();editor.wait()
        editor.stderr.close()
