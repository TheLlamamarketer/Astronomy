import numpy as np
import sys
import os
import math
import datetime
script_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from help import unit_conv

alpha_sat2025 = ('hour', 23, 45, 10.227)
delta_sat2025 = ('arc', -3, 57, 29.36)

alpha_arc2000 = ('hour', 14, 15, 39.6721)
delta_arc2000 = ('arc', 19, 10, 56.673)

p = 2*np.pi/25772.5  # radian per year
e = unit_conv(('deg', 23.43708)) # Ecliptic obliquity

b = unit_conv(('arc', 52, 27, 13.9)) # Nördliche Breite
l = unit_conv(('arc', 13, 17, 48.8)) # Östliche Länge


obs_date = datetime.date(2025, 11, 12)
obs_hour = 17.0 # Ortszeit which means time at location not in UT

# converting locational time to UT
obs_hour_UT = obs_hour - l/(np.pi) * 12.0

# decimal day of year (1..365)
day_of_year = obs_date.timetuple().tm_yday

# decimal observation year
obs_decimal_year = obs_date.year + (day_of_year - 1 + obs_hour_UT/24.0) / 365.2422
epoch_saturn = 2025.9
epoch_arcturus = 2000.0

# precession years to apply:
years_saturn = obs_decimal_year - epoch_saturn
years_arcturus = obs_decimal_year - epoch_arcturus

# Example: set Time list used in your code
Time = [years_saturn, years_arcturus]


#PRÄZESSION
def precession(alpha, delta, years):
    d_alpha = years * p * (np.cos(e) + np.sin(e) * np.sin(alpha) * np.tan(delta))
    d_delta = years * p * np.cos(alpha) * np.sin(e)

    return d_alpha, d_delta


#ORTSZEITEN


thetaG0 = unit_conv(('hour', 3, 25, 30.8376)) # Greenwich Sidereal Time at 12.11.2025 at 0h UT

thetaG = thetaG0 + obs_hour_UT * np.pi/12 * 366.2422/365.2422 # Calculate Θ_G(t) Greenwich Sidereal Time at observation time 17h local time
thetaFU = thetaG + l



#HÖHE UND AZIMUTH
def local_angles(delta, tau):

    h = np.arcsin(
        np.cos(b) * np.cos(delta) * np.cos(tau) + np.sin(b) * np.sin(delta)
    )

    A_z = np.arctan2(
        -np.cos(delta) * np.sin(tau),
        -np.sin(b) * np.cos(delta) * np.cos(tau) + np.cos(b) * np.sin(delta)
    )

    return h, np.mod(A_z, 2*np.pi) # Wrap azimuth to [0, 2π)

#KULMINATIONEN

def h_and_t(alpha, delta, tau):
    h_beob = local_angles(delta, tau)[0]
    t_beob = t_from_tau(tau, alpha)
    return h_beob, t_beob

def t_from_tau(tau_rad, alpha_rad):
    """Convert an hour angle `tau` (radians) and right ascension `alpha` (radians)
    into local solar time in hours and an integer day offset.

    Returns: (t_hours_wrapped, day_offset)
    - t_hours_wrapped is in [0, 24)
    - day_offset is integer number of days relative to reference 0h UT
    """
     
    tau_rad = tau_rad % (2 * np.pi)
    alpha_rad = alpha_rad % (2 * np.pi)
    
    # t_hours = (tau + alpha - thetaG0 - l) * (24/(2π)) * (1/sidereal_per_solar)
    t_hours = (tau_rad + alpha_rad - thetaG0 - l) * (24.0 / (2 * np.pi)) * (365.2422/ 366.2422)

    day_offset = np.floor(t_hours / 24.0)
    t_wrapped = t_hours - day_offset * 24.0
    return t_wrapped, int(day_offset)

#AUF- UND UNTERGANG h=0 

def up_and_down(delta, alpha):
    x = -np.tan(b) * np.tan(delta)
    # Handle circumpolar / never-rise cases
    if abs(x) > 1.0:
        # x > 1 -> arccos undefined -> never rises; x < -1 -> always above horizon
        return None, None

    tau_rise = -np.arccos(np.clip(x, -1.0, 1.0))
    tau_set  = +np.arccos(np.clip(x, -1.0, 1.0))


    t_up = t_from_tau(tau_rise, alpha)
    t_down = t_from_tau(tau_set, alpha)

    # Return rise, set in chronological order. Compare absolute hours.
    abs_up = t_up[0] + 24 * t_up[1]
    abs_down = t_down[0] + 24 * t_down[1]
    if abs_up <= abs_down:
        return t_up, t_down
    else:
        return t_up, t_down


def format_time(t_tuple:tuple):
    """Format time returned by t_from_tau (hours, day_offset) into HH:MM string
    with a day-offset annotation.
    """
    if t_tuple is None:
        return "N/A"
    hours, day = t_tuple
    hh = int(hours) % 24
    mm = int(round((hours - int(hours)) * 60))
    # handle rounding to next hour
    if mm == 60:
        hh = (hh + 1) % 24
        mm = 0
    s = f"{hh:02d}:{mm:02d}"
    if day == 0:
        return f"{s}h (same day)"
    sign = '+' if day > 0 else ''
    return f"{s}h (day {sign}{day})"

objects = ["Saturn", "Arcturus"]

tau_max_min = [('hour', 0, 0, 0), ('hour', 12, 0, 0)]



print(f"Beobachtung bei ({unit_conv(('rad', b), 'arc', True)} NB, {unit_conv(('rad', l), 'arc', True)} OL) am {obs_date} um {int(obs_hour_UT):02d}:{int((obs_hour_UT - int(obs_hour_UT))*60):02d} UT")

for i, (alpha, delta) in enumerate([[alpha_sat2025, delta_sat2025], [alpha_arc2000, delta_arc2000]]):
    print('-' * 40)
    print(f"Objekt: {objects[i]}")

    print(f"Rektaszension α: {unit_conv((alpha), 'hour', True)} Deklination δ: {unit_conv((delta), 'arc', True)}")

    alpha_prec = unit_conv(alpha) + precession(unit_conv(alpha), unit_conv(delta), Time[i])[0]
    delta_prec = unit_conv(delta) + precession(unit_conv(alpha), unit_conv(delta), Time[i])[1]

    tau = thetaFU - alpha_prec

    h_beob, A_beob = local_angles(delta_prec, tau)

    t_up, t_down = up_and_down(delta_prec, alpha_prec)
    h_max, t_max = h_and_t(alpha_prec, delta_prec, unit_conv(tau_max_min[0]))
    h_min, t_min = h_and_t(alpha_prec, delta_prec, unit_conv(tau_max_min[1]))
    
    def add_hour(t):
        if t is None:
            return None
        hrs, d = t
        total = hrs + 1.0
        d += int(np.floor(total / 24.0))
        return (total % 24.0, int(d))

    print(f"Präzessionskorrigierte Rektaszension α_präz: {unit_conv(('rad', alpha_prec), 'hour', True)} Deklination δ_präz: {unit_conv(('rad', delta_prec), 'arc', True)}")
    print('')
    print('Zeiten in Berlin (MEZ / UTC+1):')
    print(f"Beobachtung bei t = {format_time((obs_hour_UT + 1, 0))}: Höhe h: {unit_conv(('rad', h_beob), 'arc', True)}, Azimuth A: {unit_conv(('rad', A_beob), 'arc', True)} ")


    print(f"Höhe_max : {format_time(add_hour(t_max))} bei Höhe {unit_conv(('rad', h_max), 'arc', True)}")
    print(f"Untergang: {format_time(add_hour(t_down))}") if t_down is not None else print("Untergang N/A")
    print(f"Höhe_min : {format_time(add_hour(t_min))} bei Höhe {unit_conv(('rad', h_min), 'arc', True)}")
    print(f"Aufgang  : {format_time(add_hour(t_up))}") if t_up is not None else print("Aufgang N/A")

