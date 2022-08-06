bl_info = {
    'name': 'Jet-Fluids',
    'author': 'Pavel_Blend',
    'version': (0, 1, 1),
    'blender': (3, 2, 1),
    'category': 'Animation',
    'location': 'Properties > Physics > Jet Fluid',
    'warning': 'Demo version',
    'wiki_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon',
    'tracker_url': 'https://github.com/PavelBlend/blender_jet_fluids_addon/issues'
}


def register():
    from . import addon
    addon.register()


def unregister():
    from . import addon
    addon.unregister()
