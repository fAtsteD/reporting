from ..config_app import config


def remap(val, oMin, oMax, nMin, nMax):
    """
    Remap value
    """

    if oMin == oMax:
        return None

    if nMin == nMax:
        return None

    # check reversed input range
    reverseInput = False
    oldMin = min(oMin, oMax)
    oldMax = max(oMin, oMax)
    if not oldMin == oMin:
        reverseInput = True

    # check reversed output range
    reverseOutput = False
    newMin = min(nMin, nMax)
    newMax = max(nMin, nMax)
    if not newMin == nMin:
        reverseOutput = True

    portion = (val - oldMin) * (newMax - newMin) / (oldMax - oldMin)
    if reverseInput:
        portion = (oldMax - val) * (newMax - newMin) / (oldMax - oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result


def scale_time(hours: int, minutes: int) -> list:
    """
    Transform minutes 0 to 60 gap to 0 to 100 gap
    with rounding minutes to setted in config (for example 25)
    """
    minutes = remap(minutes, 0, 60, 0, 100)

    # Fractional part rounded to setted in config
    frac = minutes % config.minute_round_to
    if frac >= int(config.minute_round_to / 2) + 1:
        minutes = (minutes // config.minute_round_to + 1) * \
            config.minute_round_to
        if minutes == 100:
            hours += 1
            minutes = 0
    else:
        minutes = minutes // config.minute_round_to * config.minute_round_to

    return [int(hours), int(minutes)]
