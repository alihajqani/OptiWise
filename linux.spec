# File: linux.spec
# -*- mode: python ; coding: utf-8 -*-

import pulp
import os

# Find the full path to the pulp library directory
pulp_path = os.path.dirname(pulp.__file__)
# The destination is 'pulp', to recreate the structure inside the bundle
pulp_data = (pulp_path, 'pulp')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[pulp_data],
    hiddenimports=['pulp', 'pulp.apis'],
    hookspath=[],
    runtime_hooks=['hook-pulp.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    a.binaries,
    a.zipfiles,
    a.datas,
    name='OptiWise_v0.7.3-linux',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None, 
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)