import copy
import random
import cv2
import drawSvg
import numpy as np
from sklearn.neighbors import KDTree
from Archi import *

a = Temp()
b = Archi()
c = BasicElement('rect')
a.append(b)
b.append(c)
d = copy.deepcopy(a)
print(a, d)
#
# w, h = 200, 250
#
# # colors = [(127, 199, 175, 110), (218, 216, 167, 110), (167, 219, 216, 110), (237, 118, 112, 110)]
# colors = [(92, 97, 130), (79, 164, 165), (202, 166, 122), (212, 117, 100)]
# # colors = [(139,169,135, 150), (244,107,99, 150), (100,161,165, 150)]
# grid_x = 4
# grid_y = 5
# # Seperation between the bricks
# diff = 1
# # Distance between the birds
# sep_x = w / grid_x
# sep_y = h / grid_y
#
#
# # Number of quads
#
#
# def get_random_element(l):
#     return l[int(random.randint(0, len(l) - 1))]
#
#
# def draw_rect(x, y, x_s, y_s, bk):
#     rect = BasicElement(TAG_NAME='rect', x=x - x_s, y=y - y_s, width=2 * x_s, height=2 * y_s, fill=color_generator())
#     bk.append(rect)
#
#
# def setup():
#     background = Temp(width=w, height=h)
#     reverse = True if grid_x > grid_y else False
#     if reverse:
#         r_x, r_y = grid_y, grid_x
#     else:
#         r_x, r_y = grid_x, grid_y
#     grid = np.ones((r_x, r_y))
#     largest = int(r_x / 2)
#     mat = np.zeros((largest, largest))
#     mat[0, 0] = largest * largest
#     # 选择左右
#     chs = random.randint(0, 1)
#     offset = random.randint(0, r_y - largest * 2)
#     if chs == 0:
#         grid[:largest, :largest] = grid[:largest, -largest:] = grid[-largest:, int(
#             (r_y - largest) / 2) + offset:int((r_y + largest) / 2) + offset] = mat
#     else:
#         grid[-largest:, :largest] = grid[-largest:, -largest:] = grid[:largest, int(
#             (r_y - largest) / 2) + offset:int((r_y + largest) / 2) + offset] = mat
#     tmp = list(range(1, largest))
#     rev = list(reversed(tmp))
#     for i in range(r_x):
#         for j in range(r_y):
#             if grid[i, j] != 1:
#                 continue
#             grid.all()
#             chs = random.choices(tmp, rev, k=1)[0]
#             if i + chs < r_x and j + chs < r_y and (grid[i:i + chs, j:j + chs] == 1).all():
#                 mat = np.zeros((chs, chs))
#                 mat[0, 0] = chs * chs
#                 grid[i:i + chs, j:j + chs] = mat
#
#     if reverse:
#         grid = grid.T
#     current_x = sep_x / 2
#     current_y = sep_y / 2
#
#     for i in range(grid_x):
#         for j in range(grid_y):
#             cell = grid[i][j]
#             if cell != 0:
#                 step = cell ** 0.5
#                 grid_w = sep_x * step / 2 - diff
#                 grid_h = sep_y * step / 2 - diff
#                 draw_rect(current_x + sep_x / 2 * (step - 1), current_y + sep_y / 2 * (step - 1), grid_w, grid_h,
#                           background)
#             current_y += sep_y
#         current_y = sep_y / 2
#         current_x += sep_x
#     background.saveSvg('test.svg')
#
#
# setup()
