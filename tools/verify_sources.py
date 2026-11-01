"""Offline provenance and patch verification. Does not build, load auth or send audio."""
from pathlib import Path
import difflib
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
def git_hash(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
def verify():
    entries = json.loads((ROOT / 'UPSTREAM.json').read_text())
    declared = set()
    for f in entries:
        path = ROOT / f['path']; declared.add(path)
        assert git_hash(path.read_bytes()) == f['git_blob_sha1'], f['path']
    actual = {p for p in (ROOT/'vendor').rglob('*') if p.is_file()}
    assert actual == declared, 'Unexpected/missing vendor files'
    original = ROOT/'vendor/codex-voice-input'
    desktop = ROOT/'desktop'
    patches = []
    assert {p.relative_to(desktop) for p in desktop.rglob('*') if p.is_file()} == {p.relative_to(original) for p in original.rglob('*') if p.is_file()}
    changed = []
    for path in sorted(p for p in desktop.rglob('*') if p.is_file()):
        rel=path.relative_to(desktop); old=(original/rel).read_text(); new=path.read_text()
        if old != new:
            changed.append(str(rel))
            patches.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel)))
        if path.suffix in {'.csproj','.props','.xaml','.manifest'}:
            ET.parse(path)
    diff=''.join(patches)
    if '--write-patch' in sys.argv:
        (ROOT/'INTEGRATION.patch').write_text(diff)
    else:
        assert (ROOT/'INTEGRATION.patch').read_text() == diff, 'Stale integration patch'
    print(f'PASS: {len(entries)} upstream blobs; {len(changed)} patched desktop files; XML parsed; patch reproducible')
    return changed
if __name__=='__main__': verify()
