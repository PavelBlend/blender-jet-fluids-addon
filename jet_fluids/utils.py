import os

import bpy


def get_log_path(domain):
    cache_folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
    log_file_path = os.path.join(cache_folder, '_jet_fluids.log')
    return log_file_path


def print_info(*print_params):
    domain = bpy.context.object
    if domain.jet_fluid.print_debug_info:
        print(*print_params)
    if domain.jet_fluid.write_log:
        log_file_path = get_log_path(domain)
        with open(log_file_path, 'a') as log_file:
            print(*print_params, file=log_file)
