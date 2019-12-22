bl_info = {
    'name': 'Jet-Fluids',
    'author': 'Pavel_Blend',
    'version': ('demo', 0, 0, 5),
    'blender': (2, 81, 0),
    'category': 'Animation',
    'location': 'Properties > Physics > Jet Fluid',
    'warning': 'Demo version',
    'wiki_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon',
    'tracker_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon/issues'
}


try:
    from .addon import register, unregister
except BaseException as error:    # used in make_release.py
    print('\n' * 2)
    print(error)
    print('\n' * 2)
