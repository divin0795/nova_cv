import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.cm import plasma

# ----------------------------
# Génération du tesseract 4D
# ----------------------------
def generate_tesseract():
    return np.array([[x, y, z, w]
                     for x in [-1, 1]
                     for y in [-1, 1]
                     for z in [-1, 1]
                     for w in [-1, 1]])

# ----------------------------
# Génération des arêtes
# ----------------------------
def generate_edges(points):
    edges = []
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            if np.sum(np.abs(points[i] - points[j])) == 2:
                edges.append((i, j))
    return edges

# ----------------------------
# Rotation 4D dans un plan (dim1, dim2)
# ----------------------------
def rotate(points, angle, dim1, dim2):
    c, s = np.cos(angle), np.sin(angle)
    rot_matrix = np.identity(4)
    rot_matrix[dim1, dim1] = c
    rot_matrix[dim1, dim2] = -s
    rot_matrix[dim2, dim1] = s
    rot_matrix[dim2, dim2] = c
    return points @ rot_matrix.T

# ----------------------------
# Projection 4D → 3D (w encodé dans la couleur)
# ----------------------------
def project_to_3d(points4d, w_factor=3.0):
    w = points4d[:, 3]
    factor = w_factor / (w_factor - w)
    projected = points4d[:, :3] * factor[:, np.newaxis]
    return projected

# ----------------------------
# Encodage de la 4e dimension : couleur par w
# ----------------------------
def color_by_w(points4d):
    w = points4d[:, 3]
    norm_w = (w + 1) / 2  # w ∈ [-1, 1] → [0, 1]
    return plasma(norm_w)

# ----------------------------
# Affichage fixe du tesseract 4D
# ----------------------------
def plot_tesseract():
    tesseract = generate_tesseract()
    edges = generate_edges(tesseract)

    # Rotation pour incliner l'objet dans R⁴
    rotated = rotate(tesseract, np.pi/6, 0, 3)   # x-w
    rotated = rotate(rotated, np.pi/8, 1, 2)     # y-z
    projected = project_to_3d(rotated)
    colors = color_by_w(rotated)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Configuration de la vue
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_zlim(-4, 4)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_box_aspect([1, 1, 1])
    ax.set_facecolor("black")
    fig.patch.set_facecolor("black")
    ax.set_title("Tesseract 4D – Vue Fixe enrichie", color='white')

    # Dessin des arêtes
    for i, j in edges:
        seg = [projected[i], projected[j]]
        color = (colors[i][:3] + colors[j][:3]) / 2
        ax.plot(*zip(*seg), color=color, linewidth=2)

    # Sommets (affichés comme sphères colorées)
    ax.scatter(*projected.T, c=colors, s=60)

    plt.show()

# ----------------------------
# Lancer l'affichage
# ----------------------------
plot_tesseract()
