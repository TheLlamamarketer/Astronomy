import numpy as np
import sys
import os
import datetime

script_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from help import unit_conv, format_time


# unit_conv converts all different unints to radians for easier calculations in sin and cos functions

# Input of all the coordinates and observation timepoints
alpha_sat2025 = ('hour', 23, 46, 55.89)
delta_sat2025 = ('arc', -4, 3, 56.62)

alpha_arc2000 = ('hour', 14, 15, 39.6721)
delta_arc2000 = ('arc', 19, 10, 56.673)

p = 2*np.pi/25772.5                 # radian per year
e = unit_conv(('deg', 23.43708))    # Ecliptic obliquity

b = unit_conv(('arc', 52, 27, 13.9))    # Nördliche Breite
l = unit_conv(('arc', 13, 17, 48.8))    # Östliche Länge


obs_date = datetime.date(2025, 11, 12)  # Date of observation stored as a datetime.date object
obs_hour = 17.0                         # Ortszeit depending on interpetation of time can mean either ZT or LMT

# Extra Code if Ortszeit is Zone time (ZT so here its MEZ) or Local Mean Time (LMT) 
TIME_INTERPRETATION = "LMT"
if TIME_INTERPRETATION == "ZT":
    # Zone time (legal time): UT = ZT - TZ
    obs_hour_UT = obs_hour - 1
elif TIME_INTERPRETATION == "LMT":
    # Local Mean time: UT = LMT - longitude_hours (east positive)
    obs_hour_UT = obs_hour - (l/np.pi)*12.0


day_of_year = obs_date.timetuple().tm_yday          # gets the exact day of the year (out of 365) on the observation day

obs_decimal_year = obs_date.year + (day_of_year - 1 + obs_hour_UT/24.0) / 365.2422 # calculates the year in decimal of the current observation time. The -1 because 1 Jan is supposed to be day 0.
epoch_arcturus = 2000.0
years_arcturus = obs_decimal_year - epoch_arcturus                                 # finds years in decimal since 2000 Jan 1st.


# Precession definition
def precession(alpha, delta, years):
    d_alpha = years * p * (np.cos(e) + np.sin(e) * np.sin(alpha) * np.tan(delta))
    d_delta = years * p * np.cos(alpha) * np.sin(e)

    return d_alpha, d_delta



# Local mean time definitions
thetaG0 = unit_conv(('hour', 3, 25, 30.8376)) # Greenwich Sidereal Time at 12.11.2025 at 0h UT

thetaG = thetaG0 + obs_hour_UT * np.pi/12 * 366.2422/365.2422 # Calculate Θ_G(t) Greenwich Sidereal Time at observation time 17h
thetaFU = thetaG + l   

print(unit_conv(('rad', thetaFU), 'hour', True))


# calculation of local angles from equatorial coordinates
def local_angles(delta, tau):

    h = np.arcsin(
        np.cos(b) * np.cos(delta) * np.cos(tau) + np.sin(b) * np.sin(delta)
    )

    A_z = np.arctan2(
        -np.cos(delta) * np.sin(tau),
        -np.sin(b) * np.cos(delta) * np.cos(tau) + np.cos(b) * np.sin(delta)
    ) # calculates azimuth A starting at North towards East, so that 0 is North, π/2 is East, π is South, 3π/2 is West

    return h, np.mod(A_z, 2*np.pi) # Wraps azimuth to [0, 2π) from the previous range of (-π, π)



def h_and_t(alpha, delta, tau):
    # calculates time and height with a given hour angle tau
    h_beob = local_angles(delta, tau)[0]
    t_beob = t_from_tau(tau, alpha)
    return h_beob, t_beob

def t_from_tau(tau_rad, alpha_rad):  
    tau_rad = tau_rad % (2 * np.pi)
    alpha_rad = alpha_rad % (2 * np.pi)
    
    t_hours = (tau_rad + alpha_rad - thetaG0 - l) * (12.0 / ( np.pi)) * (365.2422/ 366.2422)

    day_offset = np.floor(t_hours / 24.0)
    t_wrapped = t_hours - day_offset * 24.0
    return t_wrapped, int(day_offset)



def up_and_down(delta, alpha):
    # rise and set times (where h=0)
    
    x = -np.tan(b) * np.tan(delta)
    # Handle circumpolar / never-rise cases
    if abs(x) > 1.0:
        # x > 1 -> arccos undefined -> never rises; x < -1 -> always above horizon
        return None, None

    tau_rise = -np.arccos(x)
    tau_set  = +np.arccos(x)

    return t_from_tau(tau_rise, alpha),  t_from_tau(tau_set, alpha)


objects = ["Saturn", "Arcturus"]
tau_max_min = [('hour', 0, 0, 0), ('hour', 12, 0, 0)]


print(f"Beobachtung bei ({unit_conv(('rad', b), 'arc', True)} NB, {unit_conv(('rad', l), 'arc', True)} OL) am {obs_date}")
print(f"   Ortszeit : {format_time((obs_hour, 0))} {TIME_INTERPRETATION}")
print(f"   UT : {format_time((obs_hour_UT, 0))}")
print(f"  MEZ : {format_time((obs_hour_UT + 1, 0))}")


for i, (alpha, delta) in enumerate([[alpha_sat2025, delta_sat2025], [alpha_arc2000, delta_arc2000]]):
    print('-' * 40)
    print(f"Objekt: {objects[i]}")

    print(f"Rektaszension α: {unit_conv((alpha), 'hour', True)} Deklination δ: {unit_conv((delta), 'arc', True)}")
    
    alpha = unit_conv(alpha)
    delta = unit_conv(delta)
    
    if objects[i] == "Saturn":
        alpha_prec, delta_prec = alpha, delta
    else:
        dα, dδ = precession(alpha, delta, years_arcturus)
        alpha_prec, delta_prec = alpha + dα, delta + dδ

        print(f"Präzessionskorrigierte Rektaszension α_präz: {unit_conv(('rad', alpha_prec), 'hour', True)} Deklination δ_präz: {unit_conv(('rad', delta_prec), 'arc', True)}")
 
    tau = thetaFU - alpha_prec

    h_beob, A_beob = local_angles(delta_prec, tau)

    t_up, t_down = up_and_down(delta_prec, alpha_prec)
    h_max, t_max = h_and_t(alpha_prec, delta_prec, unit_conv(tau_max_min[0]))
    h_min, t_min = h_and_t(alpha_prec, delta_prec, unit_conv(tau_max_min[1]))
    
    # convert times to MEZ by adding one hour
    def add_hour(t):
        if t is None:
            return None
        hrs, d = t
        total = hrs + 1.0
        d += int(np.floor(total / 24.0))
        return (total % 24.0, int(d))

    print('')
    print('Zeiten in Berlin (MEZ / UTC+1):')
    print(f"Beobachtung bei t = {format_time((obs_hour_UT + 1, 0))}: Höhe h: {unit_conv(('rad', h_beob), 'arc', True)}, Azimuth A: {unit_conv(('rad', A_beob), 'arc', True)}, Stundenwinkel τ: {unit_conv(('rad', tau), 'hour', True)}")
    print('')

    # Order all events chronologically (first event prints first)
    def abs_hours_mez(t):
        if t is None:
            return None
        h, d = add_hour(t) 
        return h + 24 * d
    
    # order the dates of the events to print them in chronological order
    # is an optional addition
    events = []
    if t_up is not None:
        events.append((abs_hours_mez(t_up), f"  Aufgang: {format_time(add_hour(t_up))}"))
    else:
        events.append((None, "Aufgang N/A"))

    events.append((abs_hours_mez(t_max), f" Höhe_max: {format_time(add_hour(t_max))} bei Höhe {unit_conv(('rad', h_max), 'arc', True)}"))

    if t_down is not None:
        events.append((abs_hours_mez(t_down), f"Untergang: {format_time(add_hour(t_down))}"))
    else:
        events.append((None, "Untergang N/A"))

    events.append((abs_hours_mez(t_min), f" Höhe_min: {format_time(add_hour(t_min))} bei Höhe {unit_conv(('rad', h_min), 'arc', True)}"))

    # Print in chronological order; keep N/A at the end
    for _, line in sorted([e for e in events if e[0] is not None], key=lambda x: x[0]):
        print(line)
    for _, line in [e for e in events if e[0] is None]:
        print(line)


