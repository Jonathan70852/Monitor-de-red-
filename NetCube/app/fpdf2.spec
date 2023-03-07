# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['fpdf2', 'app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['python-nmap', 'scapy', 'scapy-http', 'scapy-python3', 'mysql-connector-python', 'mysqlclient', 'PyMySQL', 'Flask-MySQLdb', 'pysnmp', 'netaddr', 'Flask', 'Flask-WTF', 'WTForms'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='fpdf2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='fpdf2',
)
