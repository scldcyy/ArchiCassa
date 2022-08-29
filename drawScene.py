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


def drawGrid(savePath, temp):
    """
    网格布局
    :param savePath:
    :param temp:
    :return:
    """
    # 读取archi
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
    # 确定网格位置、大小
    w = temp.width
    h = temp.height
    grid_x = eval(layout[0].get('grid-x'))
    grid_y = eval(layout[0].get('grid-y'))
    sep_x = w / grid_x
    sep_y = h / grid_y
    reverse = True if grid_x > grid_y else False
    if reverse:
        r_x, r_y = grid_y, grid_x
    else:
        r_x, r_y = grid_x, grid_y
    grid = np.ones((r_x, r_y))
    largest = int(r_x / 2)
    mat = np.zeros((largest, largest))
    mat[0, 0] = largest * largest
    # 选择左右
    chs = random.randint(0, 1)
    offset = random.randint(0, r_y - largest * 2)
    if chs == 0:
        grid[:largest, :largest] = grid[:largest, -largest:] = grid[-largest:, int(
            (r_y - largest) / 2) + offset:int((r_y + largest) / 2) + offset] = mat
    else:
        grid[-largest:, :largest] = grid[-largest:, -largest:] = grid[:largest, int(
            (r_y - largest) / 2) + offset:int((r_y + largest) / 2) + offset] = mat
    tmp = list(range(1, largest))
    rev = list(reversed(tmp))
    for i in range(r_x):
        for j in range(r_y):
            if grid[i, j] != 1:
                continue
            chs = random.choices(tmp, rev, k=1)[0]
            if i + chs < r_x and j + chs < r_y and (grid[i:i + chs, j:j + chs] == 1).all():
                mat = np.zeros((chs, chs))
                mat[0, 0] = chs * chs
                grid[i:i + chs, j:j + chs] = mat

    if reverse:
        grid = grid.T
    archiNum = np.count_nonzero(grid)
    # 绘制网格
    archis = random.sample(archis, archiNum)
    h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
    colors = random.choices(colorTemplate, k=len(archis))
    current_x = sep_x / 2
    current_y = sep_y / 2
    count = 0
    wait = np.argsort(-h_divide_w)
    tmp = np.cumsum([np.count_nonzero(i) for i in grid])
    sameRow = np.zeros_like(tmp)
    sameRow[1:] = tmp[:-1]
    for i in range(len(wait)):
        if wait[i] in sameRow:
            np.delete(wait, i)
    chs = wait[0]
    # chs = sat
    # chs = np.random.choice(np.setdiff1d(wait, sameRow), 1)[0]
    base_ls = []
    c1, c2 = colors[0][1], colors[0][1]
    for i in range(grid_x):
        for j in range(grid_y):
            cell = grid[i, j]
            if cell != 0:
                archi = archis[count]
                step = cell ** 0.5
                grid_w = sep_x * step / 2 - diff
                grid_h = sep_y * step / 2 - diff
                cx = current_x + sep_x / 2 * (step - 1)
                cy = current_y + sep_y / 2 * (step - 1)
                archi_h_div_w = h_divide_w[count]
                step = grid_w
                rect = BasicElement(TAG_NAME='rect', id=f'rect{count}', x=cx - grid_w,
                                    y=cy - grid_h,
                                    width=2 * grid_w, height=2 * grid_h,
                                    fill=colors[count][0])
                clip = drawSvg.ClipPath(id=f'clip{count}')
                clip.append(rect)
                if archi_h_div_w > grid_h / grid_w:
                    step = grid_h / archi_h_div_w

                if count == chs - 1:
                    archi = Archi()
                    c1, c2 = colors[count][1], colors[count][2]
                elif count == chs:
                    ratio = min((sep_y - diff) / archi.out_rect[1] * 3, (sep_x - diff) / archi.out_rect[0] * 0.8)
                    update_dict = {'x': str(current_x - archi.out_rect[0] * ratio / 2),
                                   'y': str(current_y + grid_h - archi.out_rect[1] * ratio),
                                   'width': str(archi.out_rect[0]),
                                   'height': str(archi.out_rect[1]),
                                   'viewBox': f'0 0 {archi.out_rect[0] / ratio} {archi.out_rect[1] / ratio}',
                                   'fill': colors[count][1],
                                   'stroke': colors[count][1]}
                    archi.args.update(update_dict)
                    for elem in archi.iter():
                        if 'light' in elem.args:
                            elem.args['fill'] = c2
                    base_ls[count - 1].children[1] = copy.deepcopy(archi)
                    base_ls[count - 1].children[1].args['fill'] = c1
                    base_ls[count - 1].children[1].args['stroke'] = c1
                else:
                    ratio = step / archi.out_rect[0] * 1.6
                    update_dict = {'x': str(cx - archi.out_rect[0] * ratio / 2),
                                   'y': str(cy + grid_h - archi.out_rect[1] * ratio),
                                   'width': str(archi.out_rect[0]),
                                   'height': str(archi.out_rect[1]),
                                   'viewBox': f'0 0 {archi.out_rect[0] / ratio} {archi.out_rect[1] / ratio}',
                                   'fill': colors[count][1],
                                   'stroke': colors[count][1]}
                    archi.args.update(update_dict)
                    for elem in archi.iter():
                        if 'light' in elem.args:
                            elem.args['fill'] = colors[count][2]
                base = Archi()
                base.append(rect)
                base.append(archi)
                base.args['clip-path'] = clip
                base_ls.append(base)
                # gridLoc.append([i, j])
                count += 1
            current_y += sep_y
        current_y = sep_y / 2
        current_x += sep_x
    temp.elements = base_ls
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
    light = layout.get('light')
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
    h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
    arg_sort = np.argsort(-h_divide_w)
    # 限制高度,宽度
    const_w = temp.width * eval(prospectShot.get('width-bound')[:-1])
    const_h = temp.height * eval(prospectShot.get('height-bound')[:-1])
    max_h_div_w = const_h / const_w
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
            'stroke-width': "3"}
        # archi.children = [archi.children[0]]
        archi.args.update(update_dict)
        # for elem in archi.iter():
        #     if 'light' in elem.args:
        #         elem.args['fill'] = elem.args['light']
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
    if temp.getTree().getroot().get('name') == 'grid-template':
        drawGrid(savePath='scenes/g4.svg', temp=temp)
    elif temp.getTree().getroot().get('name') == 'raster-template':
        drawRaster(savePath='scenes/r4.svg', temp=temp)
