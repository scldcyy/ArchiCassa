import copy
import os
import random

import drawSvg
import numpy as np
from Archi import Archi, Temp, color_generator, pts2path, BasicElement, prefix_tag, ParentsElement
from xml.etree import ElementTree as ET


def popArg(dic, arg):
    """
    删除字典元素
    :param dic:
    :param arg:
    :return:
    """
    if arg in dic:
        if arg != 'style' or 'fill' in dic[arg]:
            dic.pop(arg)


def loadTemp(acFile):
    """
    读取temp
    :param acFile:
    :return:
    """
    ac = ET.parse(acFile)
    posTemplate = ac.find('position')[0]
    scaleTemplate = ac.find('scale')[0]
    w, h = eval(scaleTemplate.get('width')), eval(scaleTemplate.get('height'))
    x, y = eval(posTemplate.get('left')[:-1]), eval(posTemplate.get('up')[:-1])
    temp = Temp(width=w * (1 - 2 * x), height=h * (1 - 2 * y))
    temp.file = acFile
    temp.viewBox = (-x * w, -y * h, w, h)
    return temp


def loadArchi(svgFile):
    """
    导入archi
    :param svgFile:
    :return:
    """
    elemDict = dict()
    if svgFile[-4:] != '.svg':
        return
    print(svgFile)
    per = ET.parse(svgFile)
    root = per.getroot()
    outline = root.find(prefix_tag + 'svg')
    archi = Archi(TAG_NAME='svg', file=svgFile)
    archi.args.update(outline.attrib)
    if 'width' in root.attrib:
        archi.out_rect = [eval(root.attrib['width']), eval(root.attrib['height'])]
    else:
        viewBox = list(map(eval, root.attrib['viewBox'].split(' ')))
        archi.out_rect = viewBox[2:]
    elemDict[outline] = archi
    for elem in outline.iter():
        for child in elem:
            if '{http://www.w3.org/1999/xlink}href' in child.attrib:
                child.attrib['xlink:href'] = child.attrib.pop('{http://www.w3.org/1999/xlink}href')
            parEle = ParentsElement(TAG_NAME=child.tag[len(prefix_tag):]) if len(child) > 0 else BasicElement(
                TAG_NAME=child.tag[len(prefix_tag):])
            parEle.args.update(child.attrib)
            # for i in ['class', 'style', 'fill', 'stroke']:
            #     popArg(parEle.args, i)
            # parEle.args['fill']='grey'
            # parEle.args['stroke'] = 'black'
            elemDict[child] = parEle
            elemDict[elem].append(parEle)
    return archi


def drawGrid(savePath, temp, archiNum=None):
    """
    网格布局
    :param savePath:
    :param temp:
    :return:
    """
    ac = temp.getTree()
    colorTemplate = ac.find('colors')[0].get('colors').split(' ')
    colorTemplate = [[colorTemplate[3 * i], colorTemplate[3 * i + 1], colorTemplate[3 * i + 2]] for i in
                     range(int(len(colorTemplate) / 3))]
    layout = ac.find('layout')
    diff = eval(layout.get('archi-interval')[:-1]) * temp.width
    Dir = ac.find('archis-url')[0].get('url')
    archis = []
    for i in os.listdir(Dir):
        archi = loadArchi(Dir + i)
        if archi:
            archi.args['id'] = archi.file[:-4]
            archis.append(archi)
    if not archiNum or archiNum > len(archis):
        archiNum = len(archis)
    archis = random.sample(archis, archiNum)
    random.shuffle(archis)
    w = temp.width
    h = temp.height
    grid_x = eval(layout[0].get('grid-x'))
    grid_y = eval(layout[0].get('grid-y'))
    sep_x = w / grid_x
    sep_y = h / grid_y
    short_x = sep_x / 2 - diff
    long_x = sep_x - diff
    short_y = sep_y / 2 - diff
    long_y = sep_y - diff
    grid = np.ones((grid_x, grid_y))
    for i in range(grid_x):
        for j in range(grid_y):
            if i < grid_x - 1:
                if random.random() < .3 and grid[i, j] == 1:
                    grid[i, j] = 2
                    grid[i + 1, j] = 0
            if j < grid_y - 1:
                if random.random() < .3 and grid[i, j] == 1 and grid[i, j + 1] != 0:
                    grid[i, j] = 3
                    grid[i, j + 1] = 0
            if i < grid_x - 1 and j < grid_y - 1:
                if random.random() < .6 and grid[i, j] == 1 and grid[i, j + 1] == 1 and grid[i + 1, j] == 1 and grid[i + 1, j + 1] == 1:
                    grid[i, j] = 4
                    grid[i + 1, j] = 0
                    grid[i, j + 1] = 0
                    grid[i + 1, j + 1] = 0
    current_x = sep_x / 2
    current_y = sep_y / 2
    rect_ls = []
    for i in range(grid_x):
        for j in range(grid_y):
            cell = grid[i, j]
            if cell == 1:
                rect_ls.append([current_x, current_y, short_x, short_y])
                # draw_rect(current_x, current_y, short_x, short_y, temp, f)
            if cell == 2:
                rect_ls.append([current_x + sep_x / 2, current_y, long_x, short_y])
            if cell == 3:
                rect_ls.append([current_x, current_y + sep_y / 2, short_x, long_y])
            if cell == 4:
                rect_ls.append([current_x + sep_x / 2, current_y + sep_y / 2, long_x, long_y])
            current_y += sep_y
        current_y = sep_y / 2
        current_x += sep_x
    use_ls = [drawSvg.Use(archi, 0, 0) for archi in archis]
    if len(archis) < len(rect_ls):
        tmp = random.sample(archis, len(rect_ls) - len(archis))
        for archi in tmp:
            use_ls.append(drawSvg.Use(archi, 0, 0))
    else:
        use_ls = use_ls[:len(rect_ls)]
    h_divide_w = np.array([use.getSvgDefs()[0].out_rect[1] / use.getSvgDefs()[0].out_rect[0] for use in use_ls])
    colors = random.choices(colorTemplate, k=len(use_ls))
    for i, use in enumerate(use_ls):
        archi_h_div_w = h_divide_w[i]
        const_w, const_h = rect_ls[i][2], rect_ls[i][3]
        step = const_w
        if archi_h_div_w > const_h / const_w:
            step = const_h / archi_h_div_w
        ratio = step / use.getSvgDefs()[0].out_rect[0] * 1.6
        c = colors[i][1]
        update_dict = {'width': str(use.getSvgDefs()[0].out_rect[0]),
                       'height': str(use.getSvgDefs()[0].out_rect[1]),
                       'viewBox': f'0 0 {use.getSvgDefs()[0].out_rect[0] / ratio} {use.getSvgDefs()[0].out_rect[1] / ratio}'}
        popArg(use.getSvgDefs()[0].args, 'fill')
        popArg(use.getSvgDefs()[0].args, 'stroke')
        use.getSvgDefs()[0].args.update(update_dict)
        update_dict = {
            'x': str(rect_ls[i][0] - use.getSvgDefs()[0].out_rect[0] * ratio / 2),
            'y': str(rect_ls[i][1] - use.getSvgDefs()[0].out_rect[1] * ratio / 2),
            'fill': c,
            'stroke': c}
        use.args.update(update_dict)
        temp.append(use)
    grid = Archi()
    for i in range(len(use_ls)):
        rect = BasicElement(TAG_NAME='rect', id=f'rect{i}', x=rect_ls[i][0] - rect_ls[i][2],
                            y=rect_ls[i][1] - rect_ls[i][3],
                            width=2 * rect_ls[i][2], height=2 * rect_ls[i][3],
                            fill=colors[i][0])
        grid.append(rect)
    temp.elements = [drawSvg.Use(grid, 0, 0)] + temp.elements
    temp.saveSvg(savePath)


def drawRaster(savePath, temp, archiNum=None):
    """
    光栅布局
    :param savePath:
    :param temp:
    :return:
    """
    ac = temp.getTree()
    colorTemplate = ac.find('colors')[0].get('colors').split(' ')
    layout = ac.find('layout')
    archiInterval = eval(layout.get('archi-interval')[:-1]) * temp.width
    rasterNum = eval(layout.find('raster').get('num'))
    backgroundShadow = layout.find('background-shadow')
    prospectShot = layout.find('prospect-shot')
    cloud = layout.find('cloud')
    Dir = ac.find('archis-url')[0].get('url')
    archis = []
    for i in os.listdir(Dir):
        archi = loadArchi(Dir + i)
        if archi:
            archis.append(archi)
    if not archiNum or archiNum > len(archis):
        archiNum = len(archis)
    archis = random.sample(archis, archiNum)
    # for elem in temp.iter():
    #     print(elem)
    #     if elem not in archis and isinstance(elem, ParentsElement) :
    #         elem.args['fill']='grey'
    #         elem.args['stroke'] = 'grey'
    h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
    arg_sort = np.argsort(-h_divide_w)
    # 限制高度,宽度
    const_w = temp.width * eval(prospectShot.get('width-bound')[:-1])
    const_h = temp.height * eval(prospectShot.get('height-bound')[:-1])
    max_h_div_w = const_h / const_w
    # for i in range(num):
    #     print(h_divide_w[i])
    tmp = [archis[i] for i in arg_sort]
    for i, archi in enumerate(tmp):
        archi.args['id'] = archi.file[:-4]
        archi_h_div_w = h_divide_w[arg_sort[i]]
        step = const_w
        if archi_h_div_w > max_h_div_w:
            step = const_h / archi_h_div_w
        ratio = step / archi.out_rect[0]
        update_dict = {
            'x': str(((const_w + archiInterval) * i) % temp.width),
            'y': str(temp.height - archi.out_rect[1] * ratio),
            'width': str(archi.out_rect[0]),
            'height': str(archi.out_rect[1]),
            'viewBox': f'0 0 {archi.out_rect[0] / ratio} {archi.out_rect[1] / ratio}',
            'fill': "white" if i > 3 else "grey",
            'stroke': "black",
            'stroke-width': "5"}
        # archi.children = [archi.children[0]]
        archi.args.update(update_dict)
        use = drawSvg.Use(archi, 0, 0)
        temp.append(use)
    base = Archi(TAG_NAME='svg', id='raster')
    w = temp.width / rasterNum
    for i in range(rasterNum):
        base.append(BasicElement(TAG_NAME='rect', x=i * w, y=0, width=w, height=temp.height,
                                 fill=colorTemplate[i]))
    up = eval(backgroundShadow.get('up'))
    for i in range(5):
        height = random.uniform(temp.height * up * 0.7, temp.height * up)
        base.append(
            BasicElement(TAG_NAME='rect', x=i * temp.width / 5,
                         y=temp.height - height, width=temp.width / 5,
                         height=height,
                         fill='black'))
    temp.elements = [drawSvg.Use(base, 0, 0)] + temp.elements
    cloudNum = eval(cloud.get('num'))
    cloudUrl = cloud.get('url')
    down = eval(cloud.get('down'))
    opacity = eval(cloud.get('fill-opacity'))
    print('op:', opacity)
    cloudLs = [loadArchi(cloudUrl + i) for i in os.listdir(cloudUrl)][:cloudNum]
    for i, c in enumerate(cloudLs):
        update_dict = {
            'id': f'cloud{i}',
            'x': str(random.uniform(0, temp.width * 0.9)),
            'y': str(random.uniform(0, temp.height * (1 - down))),
            'fill-opacity': opacity,
            'fill': "white",
            'stroke': "white"}
        c.args.update(update_dict)
        temp.append(drawSvg.Use(c, 0, 0))
    temp.saveSvg(savePath)


if __name__ == '__main__':
    """光栅绘制"""
    temp = loadTemp('ac/grid_scene.ac')
    drawGrid(savePath='scenes/grid3.svg', temp=temp, archiNum=10)
