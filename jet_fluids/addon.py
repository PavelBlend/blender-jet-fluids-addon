
from . import bake
from . import objects
from . import operators
from . import ui
from . import render
from . import create


modules = [
    objects,
    operators,
    bake,
    ui,
    render,
    create
]

def register():
    for module in modules:
        module.register()


def unregister():
    for module in reversed(modules):
        module.unregister()
