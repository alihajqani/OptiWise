# File: windows.spec
# -*- mode: python ; coding: utf-8 -*-

import pulp

# Find the CBC executable path dynamically within the Python environment
cbc_path = pulp.apis.LpSolverDefault.executableExtension('cbc')
# The destination is '.', meaning the root directory next to the main .exe
cbc_binary = (cbc_path, '.')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[cbc_binary],
    datas=[],
    hiddenimports=['pulp', 'pulp.apis'],
    hookspath=[],
    runtime_hooks=[],
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
    name='OptiWise_v0.7.3-windows',
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