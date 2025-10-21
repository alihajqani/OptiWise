# File: windows.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# This is a more robust way that should work on GitHub Actions
pulp_datas = collect_data_files('pulp')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=pulp_datas,
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
exe = EXE(pyz, a.scripts, [], a.binaries, a.zipfiles, a.datas,
          name='OptiWise-windows', # Simplified name
          console=False, upx=False)