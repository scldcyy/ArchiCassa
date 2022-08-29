# 规范archisvg格式
import os
import queue

import cairosvg
import cv2
from sklearn.neighbors import KDTree
import drawScene
from Archi import *

def normalizeArchi(load_dir, save_dir):
    """svg转位图再转svg"""
    svg_ls = os.listdir(load_dir)
    for i, svg in enumerate(svg_ls):
        if svg[-4:] != '.file':
            continue
        save_path = save_dir + svg[:-4] + '.png'
        cairosvg.svg2png(url=load_dir + svg, write_to=save_path)
        image = cv2.imread(save_path, 0)
        _, thresh = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
        cv2.imwrite(save_path, thresh)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        ccc = contours[0]
        for c in range(1, len(contours)):
            np.concatenate((ccc, contours[c]), axis=0)
        x, y, w, h = cv2.boundingRect(ccc)
        temp = Temp(width=w, height=h)
        clip = ParentsElement(TAG_NAME='clipPath', id='clip' + svg[:-4])
        for cont in contours:
            path = BasicElement(TAG_NAME='path', d=pts2path(cont))
            clip.append(path)
        archi = drawScene.loadArchi(load_dir + svg)
        archi.args['clip-path'] = f"url(#clip{svg[:-4]})"
        outline = ParentsElement(TAG_NAME='file', x=-x, y=-y)
        outline.append(clip)
        outline.append(archi)
        temp.append(outline)
        temp.saveSvg(f'../archis/{svg[:-4]}.file')


if __name__ == '__main__':
    normalizeArchi(load_dir="C:/Users/85365/Desktop/新建文件夹/", save_dir='../png/')

# import copy
# import os
# import random
# import numpy as np
# from Archi import Archi, Temp, color_generator, pts2path, BasicElement, prefix_tag, ParentsElement
# from xml.etree import ElementTree as ET
#
# file = ET.parse('file/raster_scene.file')
#
#
# # file = ET.parse('file/grid_scene.file')
#
#
# def popArg(dic, arg):
#     """
#     删除字典元素
#     :param dic:
#     :param arg:
#     :return:
#     """
#     if arg in dic:
#         dic.pop(arg)
#
#
# def loadTemp(loadPath, x=0.1, y=0.1, w=160, h=100, num=None):
#     """
#     读取archi
#     :param loadPath:
#     :param x:
#     :param y:
#     :param w:
#     :param h:
#     :param num:
#     :return:
#     """
#     temp = Temp(width=w * (1 - 2 * x), height=h * (1 - 2 * y))
#     temp.viewBox = (-x * w, -y * h, w, h)
#     elemDict = dict()
#     if not num or num > len(loadPath):
#         num = len(loadPath)
#     for pi in range(num):
#         path = loadPath[pi]
#         if path[-4:] != '.file':
#             continue
#         per = ET.parse(path)
#         root = per.getroot()
#         group = root.findall(prefix_tag + 'g')
#         for outline in group:
#             archi = Archi()
#             archi.args.update(outline.attrib)
#             archi.out_rect = [eval(root.attrib['width']), eval(root.attrib['height'])]
#             temp.append(archi)
#             elemDict[outline] = archi
#             for elem in outline.iter():
#                 for child in elem:
#                     print(child.tag, child.attrib)
#                     if '{http://www.w3.org/1999/xlink}href' in child.attrib:
#                         child.attrib['xlink:href'] = child.attrib.pop('{http://www.w3.org/1999/xlink}href')
#                     parEle = ParentsElement(TAG_NAME=child.tag[len(prefix_tag):]) if len(child) > 0 else BasicElement(
#                         TAG_NAME=child.tag[len(prefix_tag):])
#                     parEle.args.update(child.attrib)
#                     for i in ['class', 'style', 'fill', 'stroke']:
#                         popArg(parEle.args, i)
#                     elemDict[child] = parEle
#                     elemDict[elem].append(parEle)
#             break
#     return temp
#
#
# def drawRandomGrid(savePath, temp):
#     """
#     网格布局
#     :param savePath:
#     :param temp:
#     :return:
#     """
#     colorTemplate = file.find('colors')[0].get('colors').split(' ')
#     colorTemplate = [[colorTemplate[3 * i], colorTemplate[3 * i + 1], colorTemplate[3 * i + 2]] for i in
#                      range(int(len(colorTemplate) / 3))]
#     layout = file.find('layout')
#     diff = eval(layout.get('archi-interval')[:-1]) * temp.width
#     archis = temp.elements
#     random.shuffle(archis)
#     w = temp.width
#     h = temp.height
#     grid_x = eval(layout[0].get('grid-x'))
#     grid_y = eval(layout[0].get('grid-y'))
#     sep_x = w / grid_x
#     sep_y = h / grid_y
#     short_x = sep_x / 2 - diff
#     long_x = sep_x - diff
#     short_y = sep_y / 2 - diff
#     long_y = sep_y - diff
#     grid = np.ones((grid_x, grid_y))
#     for i in range(grid_x):
#         for j in range(grid_y):
#             if i < grid_x - 1:
#                 if random.random() < .3 and grid[i, j] == 1:
#                     grid[i, j] = 2
#                     grid[i + 1, j] = 0
#             if j < grid_y - 1:
#                 if random.random() < .3 and grid[i, j] == 1 and grid[i, j + 1] != 0:
#                     grid[i, j] = 3
#                     grid[i, j + 1] = 0
#             if i < grid_x - 1 and j < grid_y - 1:
#                 if random.random() < .6 and grid[i, j] == 1 and grid[i, j + 1] == 1 and grid[i + 1, j] == 1 and grid[
#                     i + 1, j + 1] == 1:
#                     grid[i, j] = 4
#                     grid[i + 1, j] = 0
#                     grid[i, j + 1] = 0
#                     grid[i + 1, j + 1] = 0
#     current_x = sep_x / 2
#     current_y = sep_y / 2
#     rect_ls = []
#     for i in range(grid_x):
#         for j in range(grid_y):
#             print(current_x, short_x, long_x)
#             print(current_y, short_y, long_y)
#             cell = grid[i, j]
#             if cell == 1:
#                 rect_ls.append([current_x, current_y, short_x, short_y])
#                 # draw_rect(current_x, current_y, short_x, short_y, temp, f)
#             if cell == 2:
#                 rect_ls.append([current_x + sep_x / 2, current_y, long_x, short_y])
#             if cell == 3:
#                 rect_ls.append([current_x, current_y + sep_y / 2, short_x, long_y])
#             if cell == 4:
#                 rect_ls.append([current_x + sep_x / 2, current_y + sep_y / 2, long_x, long_y])
#             current_y += sep_y
#         current_y = sep_y / 2
#         current_x += sep_x
#     if len(archis) < len(rect_ls):
#         tmp = random.sample(archis, len(rect_ls) - len(archis))
#         for i in tmp:
#             archi = copy.deepcopy(i)
#             archis.append(archi)
#     else:
#         archis = archis[:len(rect_ls)]
#     h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
#     colors = random.choices(colorTemplate, k=len(archis))
#     for i, archi in enumerate(archis):
#         archi_h_div_w = h_divide_w[i]
#         const_w, const_h = rect_ls[i][2], rect_ls[i][3]
#         step = const_w
#         if archi_h_div_w > const_h / const_w:
#             step = const_h / archi_h_div_w
#         ratio = step / archi.out_rect[0] * 1.6
#         c = colors[i][1]
#         update_dict = {
#             'transform': f'translate({rect_ls[i][0] - archi.out_rect[0] * ratio / 2}'
#                          f',{rect_ls[i][1] - archi.out_rect[1] * ratio / 2}) scale({ratio})',
#             'fill': c,
#             'stroke': c}
#         archi.args.update(update_dict)
#     for i in range(len(archis)):
#         rect = BasicElement(TAG_NAME='rect', x=rect_ls[i][0] - rect_ls[i][2], y=rect_ls[i][1] - rect_ls[i][3],
#                             width=2 * rect_ls[i][2], height=2 * rect_ls[i][3],
#                             fill=colors[i][0])
#         temp.elements = [rect] + temp.elements
#     temp.saveSvg(savePath)
#
#
# def drawRaster(savePath, temp):
#     """
#     光栅布局
#     :param savePath:
#     :param temp:
#     :return:
#     """
#     colorTemplate = file.find('colors')[0].get('colors').split(' ')
#     layout = file.find('layout')
#     archiInterval = eval(layout.get('archi-interval')[:-1]) * temp.width
#     rasterNum = eval(layout.find('raster').get('num'))
#     backgroundShadow = layout.find('background-shadow')
#     prospectShot = layout.find('prospect-shot')
#     cloud = layout.find('cloud')
#     archis = temp.elements
#     # for elem in temp.iter():
#     #     print(elem)
#     #     if elem not in archis and isinstance(elem, ParentsElement) :
#     #         elem.args['fill']='grey'
#     #         elem.args['stroke'] = 'grey'
#     h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
#     arg_sort = np.argsort(-h_divide_w)
#     # 限制高度,宽度
#     const_w = temp.width * eval(prospectShot.get('width-bound')[:-1])
#     const_h = temp.height * eval(prospectShot.get('height-bound')[:-1])
#     max_h_div_w = const_h / const_w
#     # for i in range(num):
#     #     print(h_divide_w[i])
#     tmp = [archis[i] for i in arg_sort]
#     for i, archi in enumerate(tmp):
#         archi_h_div_w = h_divide_w[arg_sort[i]]
#         step = const_w
#         if archi_h_div_w > max_h_div_w:
#             step = const_h / archi_h_div_w
#         ratio = step / archi.out_rect[0]
#         update_dict = {
#             'transform': f'translate({((const_w + archiInterval) * i) % temp.width},{temp.height - archi.out_rect[1] * ratio}) scale({ratio})',
#             'fill': "white" if i > 3 else "grey",
#             'stroke': "black",
#             'stroke-width': "5"}
#         # archi.children = [archi.children[0]]
#         archi.args.update(update_dict)
#     temp.elements = tmp
#     base = Archi()
#     w = temp.width / rasterNum
#     for i in range(rasterNum):
#         base.append(BasicElement(TAG_NAME='rect', x=i * w, y=0, width=w, height=temp.height,
#                                  fill=colorTemplate[i]))
#     up = eval(backgroundShadow.get('up'))
#     for i in range(5):
#         height = random.uniform(temp.height * up * 0.7, temp.height * up)
#         base.append(
#             BasicElement(TAG_NAME='rect', x=i * temp.width / 5,
#                          y=temp.height - height, width=temp.width / 5,
#                          height=height,
#                          fill='black'))
#     temp.elements = [base] + temp.elements
#     cloudNum = eval(cloud.get('num'))
#     cloudUrl = cloud.get('url')
#     down = eval(cloud.get('down'))
#     opcaity = eval(cloud.get('fill-opcaity'))
#     cloudLs = [cloudUrl + i for i in os.listdir(cloudUrl)]
#     cloudTemp = loadTemp(cloudLs, num=cloudNum)
#     for c in cloudTemp.elements:
#         update_dict = {
#             'transform': f'translate({random.uniform(0, temp.width * 0.9)},{random.uniform(0, temp.height * (1 - down))})',
#             'fill-opcaity': opcaity,
#             'fill': "white",
#             'stroke': "white"}
#         c.args.update(update_dict)
#         temp.append(c)
#     temp.saveSvg(savePath)
#
#
# if __name__ == '__main__':
#     """光栅绘制"""
#     Dir = file.find('archis-url')[0].get('url')
#     loadPath = [Dir + i for i in os.listdir(Dir)]
#     posTemplate = file.find('position')[0]
#     scaleTemplate = file.find('scale')[0]
#     w, h = eval(scaleTemplate.get('width')), eval(scaleTemplate.get('height'))
#     x, y = eval(posTemplate.get('left')[:-1]), eval(posTemplate.get('up')[:-1])
#     temp = loadTemp(loadPath, x, y, w, h)
#     drawRaster(savePath='scenes/raster1.file', temp=temp)
