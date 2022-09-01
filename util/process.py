# 规范archisvg格式
import os
import queue

import cairosvg
import cv2
from sklearn.neighbors import KDTree

from Archi import *


def connect_edge(edge):
    """
    连接断开边缘
    :param edge:
    :return:
    """
    edge = np.pad(edge, ((1, 1), (1, 1)), 'constant', constant_values=(0, 0))
    p = []
    locs = np.argwhere(edge == 255)
    # for i in range(1, h - 1):  # 遍历每一行
    #     for j in range(1, w - 1):  # 遍历每一列
    for loc in locs:
        i, j = loc
        r = []
        for y in range(i - 1, i + 2):
            for x in range(j - 1, j + 2):
                if y == i and x == j:
                    continue
                if edge[y, x] == 255:
                    r.append([y, x])
        rLen = len(r)
        if rLen > 0:
            # only one point, it is peak
            if rLen == 1:
                p.append([j, i])
            # there are two points and the distance is 1, it is also peak
            elif rLen == 2:
                dy = r[0][0] - r[1][0]
                dx = r[0][1] - r[1][1]
                t = dx * dx + dy * dy
                if t == 1:
                    p.append([j, i])
    if p:
        p = np.array(p)
        tree = KDTree(p, leaf_size=2)
        dist, node = tree.query(p, k=2)
        for i in range(len(node)):
            if dist[i][1] <= 10:
                cv2.line(edge, tuple(p[i]), tuple(p[node[i][1]]), 255)
    return edge[1:-1, 1:-1]


def Level_traversal(img):
    """
    层次遍历得到主要的archi及其子archi
    这里使用边缘提取，之后考虑实例分割
    :param img: 图片
    :return: 主要的archi及其子archi的列表
    """
    # img = cv2.GaussianBlur(img, (3, 3), 0)
    result = cv2.Canny(img, 50, 150, apertureSize=3, L2gradient=True)
    w, h = result.shape[:2]
    # result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel=(3, 3), iterations=3)
    result = connect_edge(result)
    # ret, result = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bk = np.array((w, h, 3))
    contours, hierarchy = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    q = queue.Queue()
    out_cont = []
    for i in range(len(hierarchy[0])):
        if hierarchy[0][i][3] == -1:
            out_cont.append(contours[i])
            q.put(i)
    ccc = out_cont[0]
    for i in range(1, len(out_cont)):
        ccc = np.concatenate((ccc, out_cont[i]), axis=0)
    ox, oy, width, height = cv2.boundingRect(ccc)
    temp = Temp(width=width, height=height)
    aid = 0
    archiList = [Archi(TAG_NAME='svg', id=aid, fill='grey', stroke='black')]
    conts = []
    while not q.empty():
        pid = q.get()
        cont = contours[pid]
        cont -= np.array([ox, oy])
        conts.append(cont)
        elem = BasicElement(TAG_NAME='path', d=pts2path(cont))
        archiList[aid].append(elem)
        if hierarchy[0][pid][0] < 0 and hierarchy[0][pid][3] != -1 and hierarchy[0][hierarchy[0][pid][3]][0] < 0:
            ccc = conts[0]
            for i in range(1, len(out_cont)):
                ccc = np.concatenate((ccc, out_cont[i]), axis=0)
            # x, y, w, h = cv2.boundingRect(cont)
            conts.clear()
            # archiList[aid].contour = cont
            # archiList[aid].out_rect = [w, h]
            if hierarchy[0][pid][2] >= 0:
                aid += 1
                archiList.append(Archi(id=aid))
                archiList[aid - 1].append(archiList[aid])
        if hierarchy[0][pid][2] >= 0:
            pid = hierarchy[0][pid][2]
            q.put(pid)
        else:
            continue
        while hierarchy[0][pid][0] >= 0:
            pid = hierarchy[0][pid][0]
            q.put(pid)
    temp.append(archiList[0])
    return temp


def normalizeArchi(load_dir, save_dir):
    """svg转位图"""
    # svg_ls = os.listdir(load_dir)
    # for i,svg in enumerate(svg_ls):
    #     if svg[-4:] != '.svg':
    #         continue
    #     per = ET.parse(load_dir + svg)
    #     root = per.getroot()
    #     v = root.attrib['viewBox'].split(' ')
    #     scale = 5
    #     w, h = eval(v[2]) * scale, eval(v[3]) * scale
    #     root.set('viewBox', f'0 0 {w} {h}')
    #     ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
    #     root.set('style', f'enable-background:new 0 0 {w} {h};')
    #     root.set('transform', f"scale({scale})")
    #     per.write(load_dir + svg)
    #     cairosvg.svg2png(url=load_dir + svg, write_to=save_dir + str(i) + '.png')

    """位图转svg"""
    png_ls = [save_dir + i for i in os.listdir(save_dir)]
    for i, img_path in enumerate(png_ls):
        img = cv2.imread(img_path, 0)
        temp = Level_traversal(img)
        temp.saveSvg(f'../archis/cloud/{i + 1}.svg')


if __name__ == '__main__':
    normalizeArchi(load_dir="C:/Users/85365/Desktop/新建文件夹/", save_dir='../png/cloud/')

