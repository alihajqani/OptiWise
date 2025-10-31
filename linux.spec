# -*- mode: python ; coding: utf-8 -*-

import pulp
import os

# Step 1: Dynamically find the absolute path to the 'pulp' library directory.
pulp_absolute_path = os.path.dirname(pulp.__file__)

# Step 2: Convert the absolute path to a relative path from the current directory (project root).
# This creates the reliable './.venv/...' path format without hardcoding it.
pulp_relative_path = os.path.relpath(pulp_absolute_path)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    
    # Use the dynamically generated relative path. This is robust and portable.
    datas=[(pulp_relative_path, 'pulp')],
    
    hiddenimports=['pulp', 'pulp.apis'],
    hookspath=[],
    # The runtime hook is still essential for setting execute permissions.
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
    name='OptiWise_v0.12.0', 
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
    entitlements_file=None,
    icon='assets/app_icon.png'
)