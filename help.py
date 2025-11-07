import numpy as np



def unit_conv(unit:tuple, convert_to='rad', print_conversion=False):
    """converts all units to degrees for ease of calculation later

    Args:
        unit (tuple): tuple containing the unit descriptor and its values
        convert_to (str): target unit to convert to ('deg', 'rad', 'arc', 'hour')
    """
    result_deg = 0.0
    
    unit = ('deg', unit) if not isinstance(unit, tuple) else unit

    if convert_to == unit[0]:
        return unit[1]

    # Converts each unit seperately to degrees
    if unit[0] == 'deg':
        result_deg = unit[1]
    elif unit[0] == 'rad':
        result_deg = unit[1] * 180/np.pi
    elif unit[0] == 'arc':
        result_deg = arc_to_deg(unit[1:])
    elif unit[0] == 'hour':
        result_deg = hour_to_deg(unit[1:])
    else:
        raise ValueError("incorrect descriptor, must be one of 'deg', 'rad', 'arc', 'hour'")


    if convert_to == 'deg':
        return result_deg if not print_conversion else f"{result_deg:.4f}°"
    elif convert_to == 'rad':
        return deg_to_rad(result_deg) if not print_conversion else f"{deg_to_rad(result_deg):.6f} rad"
    elif convert_to == 'arc':
        return deg_to_arc(result_deg) if not print_conversion else f"{int(deg_to_arc(result_deg)[0])}° {int(deg_to_arc(result_deg)[1])}' {deg_to_arc(result_deg)[2]:.4f}''"
    elif convert_to == 'hour':
        return deg_to_hour(result_deg) if not print_conversion else f"{int(deg_to_hour(result_deg)[0])}h {int(deg_to_hour(result_deg)[1])}m {deg_to_hour(result_deg)[2]:.4f}s"
    else:
        raise ValueError("incorrect target unit, must be 'deg', 'rad', 'arc', or 'hour'")

def hour_to_deg(unit_hour:tuple): return (unit_hour[0] + unit_hour[1]/60 + unit_hour[2]/3600)*15
def arc_to_deg(unit_arc:tuple): return unit_arc[0] + unit_arc[1]/60 + unit_arc[2]/3600
def deg_to_rad(unit_deg:float): return unit_deg * (np.pi/180)

def deg_to_arc(unit_deg:float):
    deg = np.floor(unit_deg)
    arc_min = (unit_deg - deg)*60
    arc_sec = (arc_min - np.floor(arc_min))*60
    return (deg, np.floor(arc_min), arc_sec)

def deg_to_hour(unit_deg:float):
    hour = np.floor(unit_deg/15)
    hour_min = (unit_deg/15 - hour)*60
    hour_sec = (hour_min - np.floor(hour_min))*60
    return (hour, np.floor(hour_min), hour_sec)
