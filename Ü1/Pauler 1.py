import numpy as np


def dez_to_degree(dez):
    degree=dez//1
    degmin=((dez%1)*60)//1
    degsec=round((((dez%1)*60)%1)*60,5)
    return degree, degmin, degsec

def degree_to_dez(degree):
    dez=degree[0]+degree[1]/60+degree[2]/3600
    return round(dez,5)

def dez_to_hour(dez):
    h=(dez/15)//1
    hmin=((((dez/15)%1)*60))
    hsec=round((hmin%1)*60,5)
    return h, hmin//1, hsec

def hour_to_dez(hour):
    dez=15*(hour[0] + hour[1]/60 +hour[2]/3600)
    return round(dez,5)

def dez_to_rad(dez):
    rad=dez*2*np.pi/360
    return round(rad,5)

def rad_to_dez(rad):
    dez=rad*360/(2*np.pi)
    return round(dez,5)


def rad_to_hour(rad):
    dez=rad_to_dez(rad)
    hour=dez_to_hour(dez)
    return hour

def hour_to_rad(hour):
    dez=hour_to_dez(hour)
    rad=dez_to_rad(dez)
    return rad


def rad_to_degree(rad):
    dez=rad_to_dez(rad)
    degree=dez_to_degree(dez)
    return degree

def degree_to_rad(degree):
    dez=degree_to_dez(degree)
    rad=dez_to_rad(dez)
    return rad

def hour_to_degree(hour):
    dez=hour_to_dez(hour)
    degree=dez_to_degree(dez)
    return degree

def degree_to_hour(degree):
    dez=degree_to_dez(degree)
    hour=dez_to_hour(dez)
    return hour

dez=180
hour=7,8,0
degree=349,33,54.9
rad=1.302029

print(dez, "° sind", int(dez_to_degree(dez)[0]), "°", int(dez_to_degree(dez)[1]), "'", int(dez_to_degree(dez)[2]), "''")
print(dez, "° sind", int(dez_to_hour(dez)[0]), "h", int(dez_to_hour(dez)[1]), "min", dez_to_hour(dez)[2], "s")
print(dez, "° sind", dez_to_rad(dez), "im Bogenmaß")

print(int(hour[0]), "h", int(hour[1]), "min", hour[2], "s sind", hour_to_dez(hour), "°")
print(int(hour[0]), "h", int(hour[1]), "min", hour[2], "s sind", hour_to_rad(hour), "im Bogenmaß")
print(int(hour[0]), "h", int(hour[1]), "min", hour[2], "s sind",  int(hour_to_degree(hour)[0]), "°", int(hour_to_degree(hour)[1]), "'", int(hour_to_degree(hour)[2]), "''")

print(rad, "im Bogenmaß sind", rad_to_dez(rad), "°")
print(rad, "im Bogenmaß sind", int(rad_to_hour(rad)[0]), "h", int(rad_to_hour(rad)[1]), "min", rad_to_hour(rad)[2], "s")
print(rad, "im Bogenmaß sind", int(rad_to_degree(rad)[0]), "°", int(rad_to_degree(rad)[1]), "'", int(rad_to_degree(rad)[2]), "''")

print(int(degree[0]), "°", int(degree[1]), "'", int(degree[2]), "'' sind", degree_to_dez(degree), "°")
print(int(degree[0]), "°", int(degree[1]), "'", int(degree[2]), "'' sind", degree_to_rad(degree), "im Bogenmaß")
print(int(degree[0]), "°", int(degree[1]), "'", int(degree[2]), "'' sind", int(degree_to_hour(degree)[0]), "h", int(degree_to_hour(degree)[1]), "min", degree_to_hour(degree)[2], "s")

