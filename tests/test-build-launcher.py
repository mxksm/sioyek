#!/usr/bin/env python3
"""Run the real launcher against a local Git remote and a harmless build stub."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

launcher = Path(__file__).resolve().parents[1] / 'build-sioyek.sh'
real_git = shutil.which('git')
def git(*args):
    return subprocess.run([real_git, *args], check=True, capture_output=True, text=True).stdout.strip()

with tempfile.TemporaryDirectory(prefix='sioyek launcher ') as temp:
    root = Path(temp)
    remote = root / 'remote'
    git('init', str(remote))
    (remote / 'scripts').mkdir()
    (remote / 'scripts/build-macos-local.sh').write_text('echo built >> "$SIOYEK_BUILD_CACHE/build-ran"\n')
    (remote / 'tracked.txt').write_text('original\n')
    git('-C', str(remote), 'add', '.')
    git('-C', str(remote), '-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-m', 'fixture')
    revision = git('-C', str(remote), 'rev-parse', 'HEAD')
    config = root / 'config'
    config.mkdir()
    shutil.copy2(launcher, config / launcher.name)
    (config / 'sioyek-app-revision').write_text(revision+'\n')
    bin_dir = root / 'bin'
    bin_dir.mkdir()
    proxy = bin_dir / 'git'
    proxy.write_text('''#!/usr/bin/env python3
import os, sys
args=sys.argv[1:]
if 'clone' in args or 'fetch' in args:
    args=['-c', 'url.'+os.environ['TEST_REMOTE']+'.insteadOf=https://github.com/mxksm/sioyek-app.git']+args
os.execv(os.environ['TEST_REAL_GIT'], [os.environ['TEST_REAL_GIT']]+args)
''')
    proxy.chmod(0o755)
    env = dict(os.environ, PATH=str(bin_dir)+os.pathsep+os.environ['PATH'], TEST_REMOTE=str(remote), TEST_REAL_GIT=real_git)
    def run(cache, success=True):
        result=subprocess.run(['bash',str(config/launcher.name)],env=dict(env,SIOYEK_BUILD_CACHE=str(cache)),capture_output=True,text=True)
        assert (result.returncode==0)==success, result.stdout+result.stderr
        return result
    fresh = root / 'fresh'
    run(fresh)
    assert (fresh/'build-ran').read_text()=='built\n'
    run(fresh)
    assert (fresh/'build-ran').read_text()=='built\nbuilt\n'
    old = root / 'old'
    old.mkdir()
    git('clone','--no-checkout',str(remote),str(old/'source'))
    git('-C',str(old/'source'),'remote','set-url','origin','https://github.com/mxksm/sioyek-app.git')
    result=run(old)
    assert 'Initializing empty source checkout' in result.stdout
    assert (old/'build-ran').exists()
    tracked=old/'source/tracked.txt'
    tracked.write_text('user changes\n')
    result=run(old,False)
    assert 'Local source changes exist' in result.stderr
    assert tracked.read_text()=='user changes\n'
    assert (old/'build-ran').read_text()=='built\n'
    git('-C',str(old/'source'),'add','tracked.txt')
    run(old,False)
    assert tracked.read_text()=='user changes\n'
print('PASS: fresh clone, repeat build, empty checkout recovery, staged and unstaged edit protection')
