from math import e
import re
from matplotlib.pylab import add
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        proj = self.axes.get_proj() if hasattr(self, 'axes') and self.axes is not None else None
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, proj)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

    def do_3d_projection(self):
        """Project 3D coordinates to 2D for this 2D artist and
        return a depth for z-order sorting used by mplot3d.
        """
        xs3d, ys3d, zs3d = self._verts3d
        proj = self.axes.get_proj() if hasattr(self, 'axes') and self.axes is not None else None
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, proj)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        # return minimum z because mplot3d sorts artists by this value
        try:
            return np.min(zs)
        except Exception:
            return 0

def add_arrow(ax, start, end, color='k', lw=1.5, label=None):
    arrow = Arrow3D(
        [start[0], end[0]], [start[1], end[1]], [start[2], end[2]],
        mutation_scale=15, lw=lw, arrowstyle="-|>", color=color, alpha=0.9
    )
    ax.add_artist(arrow)
    if label:
        # add a dummy point to include it in the legend
        ax.plot([], [], [], color=color, label=label)
        # add a small 3D text label near the arrow tip
        try: 
            pos = end + (end - start) * 0.08 
            ax.text(pos[0], pos[1], pos[2], str(label), color=color,
                    fontsize=10, horizontalalignment='center', verticalalignment='center')
        except Exception:
            pass




# --- Rotation matrices

conv = np.pi/180.0

def Rx(theta):
    c, s = np.cos(theta*conv), np.sin(theta*conv)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s,  c]])

def Ry(theta):
    c, s = np.cos(theta*conv), np.sin(theta*conv)
    return np.array([[ c, 0, s],
                     [ 0, 1, 0],
                     [-s, 0, c]])

def Rz(theta):
    c, s = np.cos(theta*conv), np.sin(theta*conv)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]])


# --- Draw a wireframe sphere
def plot_sphere(ax, radius=1.0, alpha=0.2):
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 25)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color='gray', linewidth=0.5, alpha=alpha)


radius    = 5.0                         # radius of the Earth in the plot

lat  = 32.7015174
lon  = 250.1104
delta = 32                              # dec
alpha = (22 + 49/60 + 16.23/3600) * 15  # RA


ST = (19 + 34/60 + 25.1208/3600) * 15.0 

theta = ST + lon

e_x = np.array([1.0, 0.0, 0.0])
e_y = np.array([0.0, 1.0, 0.0])
e_z = np.array([0.0, 0.0, 1.0])

v_pos = radius * np.array([np.cos(lat*conv)*np.cos(theta*conv), np.cos(lat*conv)*np.sin(theta*conv), np.sin(lat*conv)])
v_star = np.array([np.cos(delta*conv)*np.cos(alpha*conv), np.cos(delta*conv)*np.sin(alpha*conv), np.sin(delta*conv)])

matrix_eq_loc     = Rz(theta) @ Ry(-lat)
matrix_loc_eq = Ry(lat) @ Rz(-theta)

U_eq = matrix_eq_loc @ e_x
E_eq = matrix_eq_loc @ e_y
N_eq = matrix_eq_loc @ e_z

star_loc = matrix_eq_loc @ v_star
star_eq = matrix_loc_eq @ star_loc

tau = theta - alpha

q_star = np.array([np.cos(lat*conv)*np.cos(delta*conv)*np.cos(tau*conv) + np.sin(lat*conv)*np.sin(delta*conv),
                   -np.cos(delta*conv)*np.sin(tau*conv),
                   -np.sin(lat*conv)*np.cos(delta*conv)*np.cos(tau*conv) + np.cos(lat*conv)*np.sin(delta*conv)])


# --- Plot
fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection='3d')
plot_sphere(ax, radius=radius, alpha=0.7)



add_arrow(ax, np.zeros(3), v_pos, lw=2.5, label='observer position')
add_arrow(ax, np.zeros(3), e_x*radius, color='red', lw=2, label='X')
add_arrow(ax, np.zeros(3), e_y*radius, color='green', lw=2, label='Y')
add_arrow(ax, np.zeros(3), e_z*radius, color='blue', lw=2, label='Z')

add_arrow(ax, v_pos, E_eq*radius + v_pos, color='green', lw=2, label='East')
add_arrow(ax, v_pos, N_eq*radius + v_pos, color='blue',   lw=2, label='North')
add_arrow(ax, v_pos, U_eq*radius + v_pos, color='red',  lw=2, label='Zenith')

assert np.allclose(star_eq, v_star), "star_eq and v_star do not match!"

add_arrow(ax, np.zeros(3), 10*v_star, color='purple', lw=2, label='star position')
add_arrow(ax, v_pos, 10*star_eq + v_pos, color='purple', lw=2)


ax.set_xlim(-1.5*radius, 1.5*radius)
ax.set_ylim(-1.5*radius, 1.5*radius)
ax.set_zlim(-1.5*radius, 1.5*radius)
ax.set_box_aspect((1, 1, 1))
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D plot of observer and star positions in equatorial frame")
fig.tight_layout()
plt.show()

fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection='3d')

add_arrow(ax, np.zeros(3), matrix_loc_eq@U_eq, lw=2.5, label='Zenith', color='red')
add_arrow(ax, np.zeros(3), matrix_loc_eq@E_eq, lw=2.5, label='East', color='green')
add_arrow(ax, np.zeros(3), matrix_loc_eq@N_eq, lw=2.5, label='North', color='blue')
add_arrow(ax, np.zeros(3), 2*star_loc, color='purple', lw=2, label='star position')

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(-1.5, 1.5)
ax.set_box_aspect((1, 1, 1))
ax.view_init(-40, 30, -40)
ax.set_xlabel("U")
ax.set_ylabel("E")
ax.set_zlabel("N")
ax.set_title("3D plot from local horizontal frame")
fig.tight_layout()

plt.show()

