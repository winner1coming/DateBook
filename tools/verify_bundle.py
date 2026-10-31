#!/usr/bin/env python3
"""Verify the trusted generated delivery, extraction fidelity and fail-closed extraction."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile

source=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/'archive/DateBook_AllInOne_2026-11-01.py'
spec=importlib.util.spec_from_file_location('datebook_trusted_delivery',source)
bundle=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
checks=0
def denied(action):
 global checks
 try:action()
 except (ValueError,OSError):checks+=1;return
 raise AssertionError('Unsafe action was accepted')

payloads=bundle._payloads()
with tempfile.TemporaryDirectory(prefix='datebook-delivery-test-') as scratch:
 target=Path(scratch)/'DateBook'
 bundle.extract(target)
 for name,data in payloads.items():
  assert (target/name).read_bytes()==data,name
  checks+=1
 marker=target/'README.md';original=marker.read_bytes()
 denied(lambda:bundle.extract(target))
 assert marker.read_bytes()==original;checks+=1
 for path in ('../escape','/absolute','a\\b','a//b','a/./b','a/../b','C:/path',''):
  denied(lambda p=path:bundle._safe_path(p))
 # A malicious path added to otherwise matching metadata must fail before mkdir.
 bundle.FILES['../escape']='no'
 bundle.SHA256['../escape']=hashlib.sha256(b'no').hexdigest()
 denied(lambda:bundle.extract(Path(scratch)/'Unsafe'))
 assert not (Path(scratch)/'Unsafe').exists();checks+=1
 del bundle.FILES['../escape'];del bundle.SHA256['../escape']
 key='README.md';text=bundle.FILES[key];bundle.FILES[key]=text+'tamper'
 denied(bundle._payloads);bundle.FILES[key]=text
 assert hashlib.sha256(payloads['gradle/wrapper/gradle-wrapper.jar']).hexdigest()=='55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c';checks+=1
 bundle._payloads();checks+=1
print(f'PASS: {checks} bundle extraction/integrity/overwrite/path checks; {len(payloads)} files compared byte-for-byte.')
