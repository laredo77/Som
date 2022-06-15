from math import sin, cos, pi
import pygame
from hexalattice.hexalattice import *
from matplotlib.colors import LinearSegmentedColormap


class Graphic:
    def __init__(self, clustering_dict):
        self.bg_color = (255, 255, 255)
        self.clustering_dict = clustering_dict
        self.w, self.h = 640, 480
        self.vertex_count = 6
        self.norm = plt.Normalize(0, 10)
        self.colors_schema = LinearSegmentedColormap.from_list('rg', ["r", "orange", "g"], N=10)

        pygame.init()
        self.root = pygame.display.set_mode((self.w, self.h))
        self.hex_centers, _ = create_hex_grid(n=100, crop_circ=4)
        self.main_loop()

    def draw_regular_polygon(self, surface, color, vertex_count,
                             radius, position, width=0):
        n, r = vertex_count, radius
        x, y = position
        pygame.draw.polygon(surface, color, [
            (x + r * sin(2 * pi * i / n),
             y + r * cos(2 * pi * i / n))
            for i in range(n)
        ], width)

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.root.fill(self.bg_color)

            w, h = 230, 50
            i = 5
            for k in range(5):
                for m in range(i):
                    if (k, m) in self.clustering_dict:
                        val = self.clustering_dict.get((k, m))
                        color = np.round(np.array(self.colors_schema(self.norm(val))) * 255).astype(int)
                    else:
                        color = (0, 0, 0)
                    self.draw_regular_polygon(self.root, color, self.vertex_count,
                                              20, (w, h),
                                              0)
                    w += 40
                w -= (i * 40 + 20)
                h += 35
                i += 1

            i = 8
            w, h = 170, 225
            for k in range(4):
                for m in range(i):
                    if (k + 5, m) in self.clustering_dict:
                        val = self.clustering_dict.get((k + 5, m))
                        color = np.round(np.array(self.colors_schema(self.norm(val))) * 255).astype(int)
                    else:
                        color = (0, 0, 0)
                    self.draw_regular_polygon(self.root, color, self.vertex_count,
                                              20, (w, h),
                                              0)
                    w += 40
                w -= (i * 40 - 20)
                h += 35
                i -= 1

            pygame.display.flip()
