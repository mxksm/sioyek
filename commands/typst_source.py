#!/usr/bin/env python3
"""Compile/register Typst PDFs and resolve PDF coordinates through Tinymist.

Only loopback preview services are used; no browser or persistent service is opened.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time

CACHE = Path.home() / '.cache/sioyek/typst'
COMPILER_ENV = ('TYPST_FONT_PATHS', 'TYPST_PACKAGE_PATH', 'TYPST_PACKAGE_CACHE_PATH',
                'SOURCE_DATE_EPOCH')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def registration(pdf):
    return CACHE / (hashlib.sha256(str(Path(pdf).resolve()).encode()).hexdigest() + '.json')


def executable(name):
    candidates = [shutil.which(name), str(Path.home() / '.local/bin' / name),
                  '/opt/homebrew/bin/' + name, '/usr/local/bin/' + name]
    for path in candidates:
        if path and os.access(path, os.X_OK):
            return path
    raise RuntimeError(f'{name} is not installed. Install it, then compile the Typst document again.')


def source_hashes(root):
    return {str(p.resolve()): digest(p) for p in Path(root).rglob('*.typ') if p.is_file()}


class WebSocket:
    """Small RFC6455 client for the Tinymist loopback protocol (no extra packages)."""
    def __init__(self, port):
        self.sock = socket.create_connection(('127.0.0.1', port), timeout=10)
        self.reader = self.sock.makefile('rb')
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f'GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n'
                           f'Origin: http://127.0.0.1:{port}\r\nUpgrade: websocket\r\n'
                           f'Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n'
                           'Sec-WebSocket-Version: 13\r\n\r\n').encode())
        status = self.reader.readline()
        headers = {}
        while True:
            line = self.reader.readline()
            if line == b'\r\n':
                break
            if not line or len(line) > 8192:
                raise RuntimeError('Invalid Tinymist handshake')
            k, v = line.decode().split(':', 1)
            headers[k.lower()] = v.strip()
        expected = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
        if b' 101 ' not in status or headers.get('sec-websocket-accept') != expected:
            raise RuntimeError('Tinymist refused the preview connection')

    def send(self, text, opcode=1):
        payload = text.encode() if isinstance(text, str) else text
        mask = os.urandom(4)
        size = len(payload)
        header = bytes([0x80 | opcode, 0x80 | (size if size < 126 else 126)])
        if size >= 126:
            header += struct.pack('!H', size)
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def exact(self, size):
        data = self.reader.read(size)
        if len(data) != size:
            raise RuntimeError('Tinymist closed the preview connection')
        return data

    def receive(self):
        parts = []
        while True:
            first, second = self.exact(2)
            size = second & 127
            if size == 126:
                size = struct.unpack('!H', self.exact(2))[0]
            elif size == 127:
                size = struct.unpack('!Q', self.exact(8))[0]
            if size > 64 * 1024 * 1024:
                raise RuntimeError('Oversized Tinymist response')
            mask = self.exact(4) if second & 128 else None
            data = self.exact(size)
            if mask:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            opcode = first & 15
            if opcode == 8:
                raise RuntimeError('Tinymist closed the preview connection')
            if opcode == 9:
                self.send(data, 10)
                continue
            if opcode == 10:
                continue
            parts.append(data)
            if first & 128:
                return b''.join(parts)

    def close(self):
        self.reader.close()
        self.sock.close()


def resolve(meta, page, x, y):
    args = [meta['tinymist'], 'preview', meta['source'], *meta['args'], '--no-open', '--verbose',
            '--host', '127.0.0.1:0', '--data-plane-host', '127.0.0.1:0',
            '--control-plane-host', '127.0.0.1:0']
    messages = queue.Queue()
    environment = os.environ.copy()
    for key in COMPILER_ENV:
        environment.pop(key, None)
    environment.update(meta.get('environment', {}))
    process = subprocess.Popen(args, cwd=meta['cwd'], env=environment,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    def collect():
        for line in process.stdout:
            messages.put(line)
        messages.put(None)
    collector = threading.Thread(target=collect, daemon=True)
    collector.start()
    control = data = None
    try:
        ports = {}
        deadline = time.monotonic() + 25
        compiled = False
        logs = []
        while len(ports) != 2 or not compiled:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError('Typst preview timed out. Check that the document compiles.')
            line = messages.get(timeout=remaining)
            if line is None:
                raise RuntimeError('Tinymist preview failed:\n' + ''.join(logs[-8:]))
            logs.append(line)
            match = re.search(r'(Control panel|Data plane) server listening on: 127\.0\.0\.1:(\d+)', line)
            if match:
                ports[match[1]] = int(match[2])
            if 'compilation succeeded' in line:
                compiled = True
            if 'compilation failed' in line:
                raise RuntimeError('Typst compilation failed. Save and compile in Neovim first.')
        control = WebSocket(ports['Control panel'])
        data = WebSocket(ports['Data plane'])
        control.sock.settimeout(3)
        control.send(json.dumps({'event': 'syncMemoryFiles', 'files': {}}))
        data.send('src-point ' + json.dumps({'page_no': page, 'x': x, 'y': y}, separators=(',', ':')))
        while time.monotonic() < deadline:
            reply = json.loads(control.receive())
            if reply.get('event') == 'editorScrollTo':
                return reply
        raise RuntimeError('No Typst source found at this position')
    except TimeoutError as error:
        raise RuntimeError('No Typst source found at this position. Select a line of text.') from error
    finally:
        for ws in (control, data):
            if ws:
                ws.close()
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        collector.join(timeout=1)
        process.stdout.close()


def compile_pdf(args):
    source = Path(args.source).resolve()
    pdf = source.with_suffix('.pdf')
    tool = executable('tinymist')
    options = ['--root', str(source.parent)]
    for value in args.input:
        options += ['--input', value]
    compiler_hash = digest(tool)
    before = source_hashes(source.parent)
    subprocess.run([tool, 'compile', str(source), str(pdf), *options], check=True)
    if before != source_hashes(source.parent):
        raise RuntimeError('Typst sources changed while compiling; save again to refresh inverse search.')
    CACHE.mkdir(parents=True, exist_ok=True)
    meta = dict(source=str(source), pdf=str(pdf), pdf_hash=digest(pdf), sources=before,
                cwd=str(source.parent), args=options, tinymist=tool, compiler_hash=compiler_hash,
                environment={key: os.environ[key] for key in COMPILER_ENV if key in os.environ},
                nvim=executable('nvim'), server=args.server)
    with tempfile.NamedTemporaryFile(mode='w', dir=CACHE, delete=False) as stream:
        json.dump(meta, stream)
        temporary = stream.name
    os.replace(temporary, registration(pdf))


def jump(args):
    pdf = Path(args.pdf).resolve()
    meta = json.loads(registration(pdf).read_text())
    if digest(pdf) != meta['pdf_hash'] or source_hashes(meta['cwd']) != meta['sources']:
        raise RuntimeError('PDF or Typst sources changed. Save the Typst file in Neovim to refresh inverse search.')
    if digest(meta['tinymist']) != meta['compiler_hash']:
        raise RuntimeError('Tinymist changed. Save the Typst file in Neovim to refresh inverse search.')
    # Verify the owning editor is still alive before starting a compiler.
    try:
        subprocess.run([meta['nvim'], '--server', meta['server'], '--remote-expr', '1'],
                       check=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError('The Neovim instance that compiled this PDF is no longer available. '
                           'Open the Typst source in Neovim and save it again.') from error
    result = resolve(meta, args.page, args.x, args.y)
    location = result.get('start')
    if not location or not result.get('filepath'):
        raise RuntimeError('No editable Typst source at this position')
    payload = json.dumps(dict(path=result['filepath'], line=location[0]+1, column=location[1]))
    expression = "luaeval(\"require('configs.typst_sioyek').jump(_A)\", json_decode('" + payload.replace("'", "''") + "'))"
    reply = subprocess.run([meta['nvim'], '--server', meta['server'], '--remote-expr', expression],
                           check=True, capture_output=True, text=True, timeout=5)
    if reply.stdout.strip() != 'ok':
        raise RuntimeError(reply.stdout.strip() or 'Neovim could not open the Typst source')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    compile_args = sub.add_parser('compile')
    compile_args.add_argument('source')
    compile_args.add_argument('--server', required=True)
    compile_args.add_argument('--input', action='append', default=[])
    jump_args = sub.add_parser('jump')
    jump_args.add_argument('pdf')
    jump_args.add_argument('page', type=int)
    jump_args.add_argument('x', type=float)
    jump_args.add_argument('y', type=float)
    args = parser.parse_args()
    def interrupted(_signum, _frame):
        raise RuntimeError('Inverse search cancelled')
    signal.signal(signal.SIGTERM, interrupted)
    try:
        compile_pdf(args) if args.action == 'compile' else jump(args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, queue.Empty) as error:
        print('Typst inverse search: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
