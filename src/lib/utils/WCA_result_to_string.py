def format_result(result, event='3x3x3'):
    if event == '3x3x3 Fewest Moves':
        return format_result_FMC(result)

    elif event == '3x3x3 Multi-Blindfolded':
        return format_result_multi(result)

    elif result > 10 * 60 * 100: # mins * secs * millisecs
        return format_result_OVER_10MIN(result)

    elif result < 60 * 100: # mins * millisecs
        return format_result_UNDER_1MIN(result)

    else:
        minutes = int(result / 6000)
        return shrink_or_enlarge_string(str(minutes)) + ":" + format_result_UNDER_1MIN(result % 6000)

def format_result_FMC(result):
    # Single
    if result < 100:
        return str(result)
    # Mean of 3
    else:
        moves, millimoves = int(result / 100), result % 100
        return str(moves) + "." + str(millimoves)

def format_result_multi(result):
    missed = result % 100
    time_in_sec = int((result % 1000000) / 100)
    minutes, seconds = int(time_in_sec / 60), time_in_sec % 60
    difference = 99 - int(result / 10000000)
    solved = difference + missed
    attempted = solved + missed

    return str(solved) + "/" + str(attempted) + " in " + str(minutes) + ":" + str(seconds)

def format_result_OVER_10MIN(result):
    minutes, seconds = int(result / 6000), result % 6000
    return shrink_or_enlarge_string(str(minutes)) + ":" + shrink_or_enlarge_string(str(seconds)) + "." + str(result % 100)

def format_result_UNDER_1MIN(result):
    seconds, millis = int(result / 100), result % 100
    return str(seconds) + "." + shrink_or_enlarge_string(str(millis))

def shrink_or_enlarge_string(input_string, string_length = 2):
    while len(input_string) > string_length:
        input_string = input_string[1:]
    while len(input_string) < string_length:
        input_string = '0' + input_string
    return input_string