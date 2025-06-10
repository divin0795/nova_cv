import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

# Générer les sommets du penteract (5D hypercube) : 2^5 = 32 sommets
def generate_penteract():
    return np.array([[x, y, z, w, v]
                     for x in [-1, 1]
                     for y in [-1, 1]
                     for z in [-1, 1]
                     for w in [-1, 1]
                     for v in [-1, 1]])

# Rotation dans le plan (dim1, dim2) en 5D
def rotate(points, angle, dim1, dim2):
    c, s = np.cos(angle), np.sin(angle)
    R = np.identity(5)
    R[dim1, dim1] = c
    R[dim1, dim2] = -s
    R[dim2, dim1] = s
    R[dim2, dim2] = c
    return points @ R.T

# Projection 5D -> 3D via projection perspective successive
def project_5d_to_3d(points5d, d1=4.0, d2=3.0):
    # Projection 5D -> 4D (projeter sur x,y,z,w)
    v = points5d[:, 4]
    factor1 = d1 / (d1 - v)
    points4d = points5d[:, :4] * factor1[:, np.newaxis]
    
    # Projection 4D -> 3D (projeter sur x,y,z)
    w = points4d[:, 3]
    factor2 = d2 / (d2 - w)
    points3d = points4d[:, :3] * factor2[:, np.newaxis]
    return points3d

# Génération des arêtes du penteract (32 sommets)
def generate_edges(points):
    edges = []
    n = len(points)
    for i in range(n):
        for j in range(i+1, n):
            # Deux sommets sont connectés si leur coordonnées diffèrent en une seule dimension (valeur 2)
            if np.sum(np.abs(points[i] - points[j])) == 2:
                edges.append((i, j))
    return edges

# Initialisation
penteract = generate_penteract()
edges = generate_edges(penteract)

# Création figure
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.25)
ax.set_facecolor('black')
fig.patch.set_facecolor('black')

def update_plot(angle):
    ax.cla()
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-15, 15)
    ax.axis('off')
    ax.set_title("Penteract (5D) projeté en 3D", color='white')

    # Appliquer plusieurs rotations sur différents plans 5D
    rotated = rotate(penteract, angle, 0, 4)   # x-v
    rotated = rotate(rotated, angle / 2, 1, 3) # y-w
    rotated = rotate(rotated, angle / 3, 2, 4) # z-v
    rotated = rotate(rotated, angle / 4, 0, 3) # x-w

    projected = project_5d_to_3d(rotated)

    # Tracer les arêtes
    for i, j in edges:
        xs, ys, zs = zip(projected[i], projected[j])
        ax.plot(xs, ys, zs, color='cyan', linewidth=1.5)

def animate(frame):
    angle = frame * np.pi / 180
    update_plot(angle)
    return []

anim = animation.FuncAnimation(fig, animate, frames=360, interval=30, blit=False)

plt.show()
