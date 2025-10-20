# -*- mode: python ; coding: utf-8 -*-
import os
import pulp

# --- PROFESSIONAL & PORTABLE WAY TO FIND THE PULP PATH ---
# This finds the path to the pulp package dynamically, wherever it is installed.
PULP_PATH = os.path.dirname(pulp.__file__)

a = Analysis(
    ['main.py'],
    datas=[(PULP_PATH, 'pulp')],
    hiddenimports=['pulp', 'pulp.apis'],
    runtime_hooks=['hook-pulp.py'],
    # ... (rest of the file is the same)
    pathex=[], binaries=[], hookspath=[], excludes=[],
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=None, noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz, a.scripts, [], a.binaries, a.zipfiles, a.datas,
    name='OptiWise_v0.7.1', debug=False, bootloader_ignore_signals=False,
    strip=False, upx=False, runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False, argv_emulation=False,
    target_arch=None, codesign_identity=None, entitlements_file=None
)