import numpy as np
import sys
import os
script_dir = os.path.dirname(__file__)
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from help import unit_conv

alpha_sat2025 = ('hour', 23, 45, 10.227)
delta_sat2025 = ('arc', -3, 57, 29.36)

alpha_arc2000 = ('hour', 14, 15, 39.6721)
delta_arc2000 = ('arc', 19, 10, 56.673)

T_arc = 25.8671239 # Jahre seit J 2000.0

Time = [0, T_arc] # tuple für Zeitintervall in Jahren für Saturn und Arcturus

p = 360/25772.5  # Grad pro Jahr
e = unit_conv(('deg', 23.43708)) # Ekliptikschiefe in Grad


#PRÄZESSION
def precession(alpha, delta, Time):
    d_alpha = Time * p * (np.cos(e) + np.sin(e) * np.sin(alpha) * np.tan(delta))
    d_delta = Time * p * np.cos(alpha) * np.sin(e)

    return d_alpha, d_delta


#ORTSZEITEN
b = unit_conv(('arc', 52, 27, 13.9)) # Nördliche Breite
l = unit_conv(('arc', 13, 17, 48.8)) # Östliche Länge
time_og = 17

thetaG0 = unit_conv(('hour', 3, 25, 30.8376))

thetaG = thetaG0 + unit_conv(('hour', 17, 0, 0)) * 366.24/365.24
thetaFU = thetaG + l

#STUNDENWINKEL



#HÖHE UND AZIMUTH
def local_angles(delta, tau):

    h = np.arcsin(
        np.cos(b) * np.cos(delta) * np.cos(tau) + np.sin(b) * np.sin(delta)
    )

    A_1 = np.arcsin(
        -np.cos(delta) * np.sin(tau) / np.cos(h)
    )

    A_2 = np.arccos(
        (-np.sin(b) * np.cos(delta) * np.cos(tau) + np.cos(b) * np.sin(delta)) / np.cos(h)
    )

    return h, A_1, A_2

#KULMINATIONEN

def h_and_t(alpha, delta, tau):
    h_beob = local_angles(delta, tau)[0]
    t_beob = t_from_tau(tau, alpha)
    return h_beob, t_beob

def t_from_tau(tau, alpha): return 365.24 / 366.24 * (tau - thetaG0 - l + alpha)

#AUF- UND UNTERGANG

#h=0 

def up_and_down(delta, alpha):
    tau_1 = np.arccos(-np.tan(b)*np.tan(delta))
    tau_2 = 2 * np.pi - tau_1

    t_updown = t_from_tau(tau_1, alpha)
    t_downup = t_from_tau(tau_2, alpha)

    return t_updown, t_downup

objects = ["Saturn", "Arcturus"]

tau_max_min = [('hour', 0, 0, 0), ('hour', 12, 0, 0)]




for i, (alpha, delta) in enumerate([[alpha_sat2025, delta_sat2025], [alpha_arc2000, delta_arc2000]]):
    print('-' * 40)
    print(f"Objekt: {objects[i]}")

    print(f"Rektaszension α: {unit_conv((alpha), 'hour', True)} Deklination δ: {unit_conv((delta), 'arc', True)}")

    alpha = unit_conv(alpha) + precession(unit_conv(alpha), unit_conv(delta), Time[i])[0]
    delta = unit_conv(delta) + precession(unit_conv(alpha), unit_conv(delta), Time[i])[1]

    tau = thetaFU - alpha
    
    h_beob, t_beob = h_and_t(alpha, delta, tau)
    
    t_updown, t_downup = up_and_down(delta, alpha)
    h_max, t_max = h_and_t(alpha, delta, unit_conv(tau_max_min[0]) - alpha)
    h_min, t_min = h_and_t(alpha, delta, unit_conv(tau_max_min[1]) - alpha)

    print(f"Rektaszension α: {unit_conv(('rad', alpha), 'hour', True)} Deklination δ: {unit_conv(('rad', delta), 'arc', True)}")
    print(f"Höhe bei Beobachtung: {unit_conv(('rad', h_beob), 'arc', True)} at t = {unit_conv(('rad', t_beob), 'hour', True)}")
    print(f"Höhe bei Maximalerhöhung: {unit_conv(('rad', h_max), 'arc', True)} at t = {unit_conv(('rad', t_max), 'hour', True)}")
    print(f"Höhe bei Minimalerhöhung: {unit_conv(('rad', h_min), 'arc', True)} at t = {unit_conv(('rad', t_min), 'hour', True)}")
