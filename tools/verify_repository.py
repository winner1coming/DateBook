#!/usr/bin/env python3
"""Repository/docs checks; --check-baseline additionally proves migration changed no app code."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--check-baseline',action='store_true',help='One-time migration acceptance: compare production sources with archived delivery')
args=parser.parse_args()
count=0
def check(ok,message):
 global count
 if not ok:raise AssertionError(message)
 count+=1

required=['README.md','CONTRIBUTING.md','docs/README.md','docs/product/PRD.md','docs/product/REQUIREMENTS.md','docs/technical/TD.md','docs/technical/ARCHITECTURE.md','docs/development/BUILD_GUIDE.md','docs/development/DEVELOPMENT_PLAN.md','docs/development/IMPLEMENTATION_STATUS.md','docs/testing/TEST_PLAN.md','docs/testing/TEST_REPORT.md','docs/testing/RELEASE_CHECKLIST.md','.github/workflows/verify.yml','tools/check_android_sdk.py']
for path in required:check((ROOT/path).is_file(),'Missing '+path)
check(not (ROOT/'DateBook_AllInOne.py').exists(),'Legacy bundle should not be the root entry point')
archive=ROOT/'archive/DateBook_AllInOne_2026-11-01.py'
check(archive.is_file(),'History snapshot retained')
check(hashlib.sha256((ROOT/'gradle/wrapper/gradle-wrapper.jar').read_bytes()).hexdigest()=='55243ef57851f12b070ad14f7f5bb8302daceeebc5bce5ece5fa6edb23e1145c','Wrapper integrity')

for path in [ROOT/'README.md',ROOT/'CONTRIBUTING.md',*sorted((ROOT/'docs').rglob('*.md'))]:
 content=path.read_text(encoding='utf-8')
 check('/Users/jinling.qin/' not in content,'Local path leaked in '+str(path.relative_to(ROOT)))
 without_fences=re.sub(r'```[\s\S]*?```','',content)
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',without_fences):
  target=target.split(' "',1)[0].strip('<>')
  if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
  value=unquote(target.split('#',1)[0])
  check((path.parent/value).resolve().exists(),f'Broken link in {path.relative_to(ROOT)}: {target}')

source_meta=[
 ('PRD_v1.1.docx','product/PRD.md',9,0,'b08683c5a0bbe9c330f1e79b2105b5d5ff6565117d82b0b799174b36e34e5b97'),
 ('REQUIREMENTS_v1.1.docx','product/REQUIREMENTS.md',7,0,'2eb0c74e205b80bfe8d97f4886fc0c7c7d070f55bb6a80472bf407b470a5ce4a'),
 ('TD_v1.1.docx','technical/TD.md',38,10,'406465eb713a08ba679e940a43b08ca18eae3ea7827c5cdf68e65215cd341d25')]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for name,reading,tables,images,digest in source_meta:
 path=ROOT/'docs/source'/name
 check(hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Original DOCX changed: '+name)
 with zipfile.ZipFile(path) as package:body=ET.fromstring(package.read('word/document.xml'))
 check(len(body.findall('.//w:tbl',ns))==tables,'Source table count: '+name)
 check(len(body.findall('.//a:blip',ns))==images,'Source image count: '+name)
 markdown=(ROOT/'docs'/reading).read_text()
 check(len(re.findall(r'^\|(?:\s*---\s*\|)+\s*$',markdown,re.M))==tables,'Reading copy table count: '+reading)
 check(markdown.count('![原文插图 ')==images,'Reading copy image count: '+reading)

workflow=(ROOT/'.github/workflows/verify.yml').read_text()
check('contents: read' in workflow,'CI must not request repository write permission')
check('persist-credentials: false' in workflow,'CI must not retain checkout credentials')
check('pull_request_target' not in workflow,'No privileged pull_request_target')
check('sdkmanager --licenses' not in workflow,'No auto-accept SDK licenses')
check(':app:assembleDebug' in workflow and ':app:lintDebug' in workflow,'CI includes actual Android build/lint targets')
check('continue-on-error' not in workflow,'Do not turn failed verification into success')
for uses in re.findall(r'uses:\s*([^\s#]+)',workflow):check(bool(re.fullmatch(r'actions/[a-z-]+@[a-f0-9]{40}',uses)),'Unpinned or third-party Action: '+uses)

if args.check_baseline:
 spec=importlib.util.spec_from_file_location('datebook_migration_baseline',archive)
 legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
 for name,data in legacy._payloads().items():
  if name.endswith('.kt') or name.startswith(('app/src/main/res/','app/schemas/','gradle/','licenses/')) or name in ('app/src/main/AndroidManifest.xml','app/build.gradle.kts','core/build.gradle.kts','build.gradle.kts','settings.gradle.kts','gradle.properties','gradlew','gradlew.bat'):
   check((ROOT/name).read_bytes()==data,'Business/build file changed during migration: '+name)

print(f'PASS: {count} repository/docs/CI checks; migration baseline={args.check_baseline}. No Android build/device execution implied.')
