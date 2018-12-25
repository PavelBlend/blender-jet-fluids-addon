
from . import bake
from . import objects
from . import operators
from . import ui
from . import render


modules = [
    objects,
    operators,
    bake,
    ui,
    render
]

def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()
