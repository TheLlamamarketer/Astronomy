import numpy as np

def unit_conv(unit:tuple | list, convert_to='rad', print_conversion=False):
    """converts all units to degrees for ease of calculation later

    Args:
        unit (tuple): tuple containing the unit descriptor and its values as follows:
            ('deg', deg)
            ('rad', rad)
            ('arc', (deg, arcmin, arcsec)) or ('arc', deg, arcmin, arcsec)
            ('hour', (hour, min, sec)) or ('hour', hour, min, sec)
        convert_to (str): target unit to convert to ('deg', 'rad', 'arc', 'hour')
        print_conversion (bool): if True, returns a formatted string for printing
    Returns:
        float | str: converted value in desired unit or formatted string
    """
    result_deg = 0.0

    unit = ('deg', unit) if not isinstance(unit, (tuple, list)) else unit

    # Converts each unit seperately to degrees
    if unit[0] == 'deg':
        result_deg = unit[1]
    elif unit[0] == 'rad':
        result_deg = unit[1] * 180/np.pi
    elif unit[0] == 'arc':
        # handle ('arc', (deg, arcmin, arcsec)) or ('arc', deg, arcmin, arcsec)
        values = unit[1] if isinstance(unit[1], (tuple, list)) else unit[1:]
        result_deg = arc_to_deg(values)
    elif unit[0] == 'hour':
        # handle ('hour', (hour, min, sec)) or ('hour', hour, min, sec)
        values = unit[1] if isinstance(unit[1], (tuple, list)) else unit[1:]
        result_deg = hour_to_deg(values)
    else:
        raise ValueError("incorrect descriptor, must be one of 'deg', 'rad', 'arc', 'hour'")

    # Converts degrees back to a desired target unit or gives print ready string
    if convert_to == 'deg':
        return result_deg if not print_conversion else f"{result_deg:.4f}°"
    elif convert_to == 'rad':
        rad = deg_to_rad(result_deg)
        return rad if not print_conversion else f"{rad:.6f} rad"
    elif convert_to == 'arc':
        arc = deg_to_arc(result_deg)
        return arc if not print_conversion else f"{'+' if arc[0] >= 0 else ''}{int(arc[0])}° {int(arc[1])}' {arc[2]:.4f}\""
    elif convert_to == 'hour':
        hour = deg_to_hour(result_deg)
        return hour if not print_conversion else f"{int(hour[0])}h {int(hour[1])}m {hour[2]:.4f}s"
    else:
        raise ValueError("incorrect target unit, must be 'deg', 'rad', 'arc', or 'hour'")

def hour_to_deg(unit_hour:tuple): return (unit_hour[0] + unit_hour[1]/60 + unit_hour[2]/3600)*15
def arc_to_deg(unit_arc:tuple): return np.sign(unit_arc[0]) * (abs(unit_arc[0]) + unit_arc[1]/60 + unit_arc[2]/3600)
def deg_to_rad(unit_deg:float): return unit_deg * (np.pi/180)

def deg_to_arc(unit_deg:float):
    deg = np.floor(abs(unit_deg))
    arc_min = (abs(unit_deg) - deg)*60
    arc_sec = (arc_min - np.floor(arc_min))*60
    return (np.sign(unit_deg)*deg, np.floor(arc_min), arc_sec)

def deg_to_hour(unit_deg:float):
    hour = np.floor(abs(unit_deg)/15)
    hour_min = (abs(unit_deg)/15 - hour)*60
    hour_sec = (hour_min - np.floor(hour_min))*60
    return (np.sign(unit_deg)*hour, np.floor(hour_min), hour_sec)
