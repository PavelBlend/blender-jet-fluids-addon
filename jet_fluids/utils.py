import os, time

import bpy


def convert_time_to_string(start_time):
    total_time = time.time() - start_time
    HOUR_IN_SECONDS = 60 * 60
    MINUTE_IN_SCEONDS = 60
    time_string = ''
    if total_time > 10.0:
        total_time = int(total_time)
        if total_time > MINUTE_IN_SCEONDS and total_time <= HOUR_IN_SECONDS:
            minutes = total_time // MINUTE_IN_SCEONDS
            seconds = total_time - minutes * MINUTE_IN_SCEONDS
            time_string = '{0} min {1} sec'.format(minutes, seconds)
        elif total_time <= MINUTE_IN_SCEONDS:
            time_string = '{0} seconds'.format(total_time)
        elif total_time > HOUR_IN_SECONDS:
            hours = total_time // HOUR_IN_SECONDS
            minutes = total_time - (total_time // HOUR_IN_SECONDS) * HOUR_IN_SECONDS
            time_string = '{0} hours {1} min'.format(hours, minutes)
    else:
        seconds = round(total_time, 2)
        time_string = '{0} seconds'.format(seconds)
    return time_string


def get_log_path(domain, log_file_name):
    cache_folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
    log_file_path = os.path.join(cache_folder, log_file_name)
    return log_file_path


def print_info(*print_params):
    domain = bpy.context.object
    if domain.jet_fluid.print_debug_info:
        print(*print_params)
    if domain.jet_fluid.write_log:
        log_file_path = get_log_path(domain, '_jet_fluids_simulate.log')
        with open(log_file_path, 'a') as log_file:
            print(*print_params, file=log_file)
