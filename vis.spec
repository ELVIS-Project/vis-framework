# -*- mode: python -*-
a = Analysis(['../vis_hack_day/__main__.py'],
             pathex=['/Users/jamieklassen/Documents/Code/pyinstaller'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=['PyInstaller/loader/rthooks/pyi_rth_PIL_Image.py',
                            'PyInstaller/loader/rthooks/pyi_rth_encodings.py',
                            'PyInstaller/loader/rthooks/pyi_rth_mpldata.py',
                            'PyInstaller/loader/rthooks/pyi_rth_qt4plugins.py'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.darwin/vis', 'vis'),
          debug=False,
          strip=None,
          upx=True,
          console=True )

import sys
if sys.platform.startswith("darwin"):
    app = BUNDLE(exe,
                 a.binaries,
                 a.zipfiles,
                 a.datas,
                 name=os.path.join('dist', 'vis.app'),
                 version="1.0")
