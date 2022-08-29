import random
import cv2
import drawSvg
import numpy as np
from sklearn.neighbors import KDTree
from Archi import *

#
# w, h = 200, 250
#
# # colors = [(127, 199, 175, 110), (218, 216, 167, 110), (167, 219, 216, 110), (237, 118, 112, 110)]
# colors = [(92, 97, 130), (79, 164, 165), (202, 166, 122), (212, 117, 100)]
# # colors = [(139,169,135, 150), (244,107,99, 150), (100,161,165, 150)]
#
#
# # Number of quads
# grid_x = 4
# grid_y = 5
#
# # Seperation between the bricks
# diff = 1
#
#
# # Distance between the birds
# sep_x = w / grid_x
# sep_y = h / grid_y
# short_x = sep_x / 2 - diff
# long_x = sep_x - diff
# short_y = sep_y / 2 - diff
# long_y = sep_y - diff
#
#
# def get_random_element(l):
#     return l[int(random.randint(0, len(l) - 1))]
#
#
# def draw_rect(x, y, x_s, y_s, bk, f):
#     rect = BasicElement(TAG_NAME='rect', x=x - x_s, y=y - y_s, width=2 * x_s, height=2 * y_s, fill=color_generator())
#     bk.append(rect)
#
#
# def setup():
#     aNum = int(grid_x * grid_y / 2)
#     background = Temp(width=w, height=h)
#     grid = np.ones((grid_x, grid_y))
#     # chs = random.choices((1, 2, 3, 4), weights=(2, 3, 3, 2), k=aNum)
#     # count = 0
#     # for i in range(grid_x):
#     #     for j in range(grid_y):
#     #         if grid[i, j] == -1:
#     #             continue
#     #         count += 1
#
#     for i in range(grid_x):
#         for j in range(grid_y):
#             if i < grid_x - 1:
#                 if random.random() < .3 and grid[i][j] == 1:
#                     grid[i][j] = 2
#                     grid[i + 1][j] = 0
#             if j < grid_y - 1:
#                 if random.random() < .3 and grid[i][j] == 1 and grid[i][j + 1] != 0:
#                     grid[i][j] = 3
#                     grid[i][j + 1] = 0
#             if i < grid_x - 1 and j < grid_y - 1:
#                 if random.random() < .2 and grid[i][j] == 1 and grid[i][j + 1] == 1 and grid[i + 1][j] == 1 and grid[
#                     i + 1][j + 1] == 1:
#                     grid[i][j] = 4
#                     grid[i + 1][j] = 0
#                     grid[i][j + 1] = 0
#                     grid[i + 1][j + 1] = 0
#
#     current_x = sep_x / 2
#     current_y = sep_y / 2
#     for i in range(grid_x):
#         for j in range(grid_y):
#             print(current_x, short_x, long_x)
#             print(current_y, short_y, long_y)
#             cell = grid[i][j]
#             if cell == 1:
#                 f = get_random_element(colors)
#                 draw_rect(current_x, current_y, short_x, short_y, background, f)
#
#             if cell == 2:
#                 f = get_random_element(colors)
#                 draw_rect(current_x + sep_x / 2, current_y, long_x, short_y, background, f)
#
#             if cell == 3:
#                 f = get_random_element(colors)
#                 draw_rect(current_x, current_y + sep_y / 2, short_x, long_y, background, f)
#
#             if cell == 4:
#                 f = get_random_element(colors)
#                 draw_rect(current_x + sep_x / 2, current_y + sep_y / 2, long_x, long_y, background, f)
#
#             current_y += sep_y
#         current_y = sep_y / 2
#         current_x += sep_x
#     background.saveSvg('test.file')
#
#
# setup()
# import cv2
#
# imgpath = 'png/05.png'
# # image = cv2.imread(imgpath, cv2.IMREAD_UNCHANGED)
# image = cv2.imread(imgpath)
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
# cv2.imwrite('sss.jpg', thresh)
import drawSvg as draw

d = draw.Drawing(1.4, 1.4, origin='center')

# Define clip path

# Draw a cropped circle
c = drawSvg.Path(d='M 0 0 L200 200 L200 0 z')
d.append(c)

# Make a transparent copy, cropped again
g = draw.Group(opacity=0.5)
u = draw.Use(c, 0.3, 0.3)
print(u.getSvgDefs())
g.append(u)
d.append(g)

# Display
d.setRenderSize(400)
d.rasterize()
d.saveSvg('test1.svg')
