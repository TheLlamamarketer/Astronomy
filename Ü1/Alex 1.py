import numpy as np

def unit_to_deg(unit:tuple):
    """converts all units to degrees for ease of calculation later

    Args:
        unit (tuple): tuple containing the unit descriptor and its values
    """
    
    result_deg = 0.0
    
    # Converts each unit seperately to degrees
    if unit[0] == 'deg':
        result_deg = unit[1]
    elif unit[0] == 'rad':
        result_deg = rad_to_deg(unit[1])
    elif unit[0] == 'arc':
        result_deg = arc_to_deg(unit[1:])
    elif unit[0] == 'hour':
        result_deg = hour_to_deg(unit[1:])
    else:
        raise ValueError("incorrect descriptor, must be one of 'deg', 'rad', 'arc', 'hour'")
    
    return result_deg

def rad_to_deg(unit_rad:float): return unit_rad * 180/np.pi
def deg_to_rad(unit_deg:float): return unit_deg * np.pi/180
def hour_to_deg(unit_hour:tuple): return (unit_hour[0] + unit_hour[1]/60 + unit_hour[2]/3600)*15
def arc_to_deg(unit_arc:tuple): return unit_arc[0] + unit_arc[1]/60 + unit_arc[2]/3600

def deg_to_arc(unit_deg:float):
    deg = np.trunc(unit_deg)
    arc_min = (unit_deg - deg)*60
    arc_sec = (arc_min - np.trunc(arc_min))*60
    return (deg, arc_min, arc_sec)

def deg_to_hour(unit_deg:float):
    hour = np.trunc(unit_deg/15)
    hour_min = (unit_deg/15 - hour)*60
    hour_sec = (hour_min - np.trunc(hour_min))*60
    return (hour, hour_min, hour_sec)


def print_all_units(unit_deg:float):
    """Prints all converted units from a given degree value

    Args:
        unit_deg (float): unit value in degrees
    """

    unit_rad = deg_to_rad(unit_deg)
    unit_arc = deg_to_arc(unit_deg)
    unit_hour = deg_to_hour(unit_deg)

    print(f"| {unit_rad:>10.6f} | {unit_deg:>10.4f}° | {int(unit_arc[0]):>3}° {int(unit_arc[1]):>2}' {unit_arc[2]:>5.2f}'' | {int(unit_hour[0]):>2}h {int(unit_hour[1]):>2}m {unit_hour[2]:>6.2f}s |")
    # the formatting, aka :>10.6f means: right aligned, 10 characters wide, 6 digits after decimal point, for better alignment in the table


print("| Bogenmaß   | Dezimalgrad | Gradmaß          | Zeitmaß         |")
print("|------------|-------------|------------------|-----------------|")


units = [('rad', 1.302029), ('deg', 180), ('arc', 349, 33, 54.9), ('hour', 7, 8, 0.0)]
for unit in units:
    deg_unit = unit_to_deg(unit)
    print_all_units(deg_unit)