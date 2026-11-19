#!/usr/bin/env python3
"""Install the tested official Tinymist release to ~/.local/bin on macOS."""
import hashlib
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import urllib.request

version = '0.15.12'
if platform.system() != 'Darwin' or platform.machine() not in ('arm64', 'x86_64'):
    raise SystemExit('Install Tinymist from https://github.com/Myriad-Dreamin/tinymist/releases for your platform.')
arch = 'aarch64' if platform.machine() == 'arm64' else 'x86_64'
name = f'tinymist-{arch}-apple-darwin'
url = f'https://github.com/Myriad-Dreamin/tinymist/releases/download/v{version}/{name}.tar.gz'
with tempfile.TemporaryDirectory() as tmp:
    archive = Path(tmp)/'tinymist.tar.gz'
    urllib.request.urlretrieve(url, archive)
    with urllib.request.urlopen(url+'.sha256', timeout=30) as response:
        expected = response.read().decode().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise SystemExit('Tinymist checksum mismatch; nothing was installed.')
    destination = Path.home()/'.local/bin/tinymist'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as bundle:
        member = bundle.getmember(name+'/tinymist')
        if not member.isfile():
            raise SystemExit('Invalid Tinymist archive')
        with bundle.extractfile(member) as source, open(destination.with_suffix('.new'), 'wb') as target:
            shutil.copyfileobj(source, target)
    destination.with_suffix('.new').chmod(0o755)
    destination.with_suffix('.new').replace(destination)
print(f'Installed Tinymist {version} at {destination}')
