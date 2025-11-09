# -*- mode: python ; coding: utf-8 -*-

CBC_EXECUTABLE_PATH = 'C:\\Users\\Seyyed Javad Razavi\\.conda\\envs\\OptiWisee\\Lib\\site-packages\\pulp\\solverdir\\cbc\\win\\64\\cbc.exe'

a = Analysis(
    ['main.py'],
    pathex=[],
    
    binaries=[(CBC_EXECUTABLE_PATH, '.')],
    
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
    name='OptiWise_v0.12.2',
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
    icon='assets/app_icon.ico'
)