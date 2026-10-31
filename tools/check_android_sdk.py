#!/usr/bin/env python3
"""Read-only SDK preflight. Never installs SDK packages or accepts licenses."""
import os
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
location=os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME')
properties=root/'local.properties'
if not location and properties.is_file():
 for line in properties.read_text().splitlines():
  if line.startswith('sdk.dir='):
   location=line.split('=',1)[1].replace('\\:',':').replace('\\\\','\\')
   break
if not location:
 sys.exit('Android SDK not configured. Set ANDROID_HOME/ANDROID_SDK_ROOT or configure SDK in Android Studio. No packages or licenses were changed.')
sdk=Path(location).expanduser()
if not (sdk/'platforms/android-37/android.jar').is_file():
 sys.exit('API37 SDK platform missing. Install it in an authorized SDK environment; this check will not auto-install or accept licenses.')
if not list((sdk/'build-tools').glob('*/aapt2*')):
 sys.exit('Android Build Tools missing. Install the AGP-required version in Android Studio.')
print('PASS: API37 platform and Android Build Tools present. Version/permission compatibility still requires actual Gradle build.')
