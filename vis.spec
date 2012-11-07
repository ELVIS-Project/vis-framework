# -*- mode: python -*-
a = Analysis(['__main__.py'],
             pathex=['/Users/jamieklassen/Documents/Code/vis'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.darwin/vis', 'vis'),
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'vis'))
app = BUNDLE(coll,
             name=os.path.join('dist', 'vis.app'))
