VERBOSE = False


def set_verbose(enabled):
    global VERBOSE
    VERBOSE = enabled


def log(message):
    if VERBOSE:
        print(message)
