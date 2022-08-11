import time


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


def time_stats(name):
    def decorator(fun):
        def wrapper(*args, **kw):
            import time
            start_time = time.time()
            result = fun(*args, **kw)
            end_time = time.time()
            total_time = end_time - start_time
            print('{0}: {1:.3f} sec'.format(name, total_time))
            return result
        return wrapper
    return decorator


def print_info(*print_params):
    print(*print_params)
