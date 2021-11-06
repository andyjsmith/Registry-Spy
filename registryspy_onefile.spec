# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

data = [
    ('registryspy/img/*.png', 'img'),
    ('registryspy/img/*.ico', 'img'),
    ('registryspy/third_party_licenses.txt', '.')
]

a = Analysis(['run.py'],
             pathex=['.'],
             binaries=[],
             datas=data,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

splash = Splash('registryspy/img/splash.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(18, 136),
                text_size=9,
                text_color='white')

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          splash,
          splash.binaries,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='registryspy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='registryspy/img/icon.ico')
