# File: linux.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

pulp_datas = collect_data_files('pulp', include_py_files=True)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=pulp_datas,
    hiddenimports=['pulp', 'pulp.apis'],
    hookspath=[],
    runtime_hooks=['hook-pulp.py'],
    excludes=[],
    cipher=None,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pyz, a.scripts, [], a.binaries, a.zipfiles, a.datas,
          name='OptiWise-linux', # Simplified name
          console=False, upx=False)