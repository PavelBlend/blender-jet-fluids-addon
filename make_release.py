from jet_fluids import bl_info
from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk


with ZipFile('jet_fluids_{}.zip'.format(('_'.join(map(str, bl_info['version'])))), 'w') as z:
    for root, _, files in walk('jet_fluids'):
        for file in files:
            if not file.endswith('.py') and not file.endswith('.pyd'):
                continue
            z.write(path.join(root, file), compress_type=ZIP_DEFLATED)

input('Make release finish!')
