from colour import Color
import cv2
import drawSvg
import numpy as np
import random
from xml.etree import ElementTree as ET
from treelib import Tree
from torchvision import models, transforms
import torch
from model.resnet_FT import ResNetGAPFeatures as Net
import scipy.stats as st

prefix_tag = '{http://www.w3.org/2000/svg}'


def pts2path(ls):
    """
    路径列表转svg格式的path
    :param ls:
    :return:
    """
    if len(ls.shape) == 3:
        ls = np.squeeze(ls, axis=1)
    str_ls = [str(i[0]) + ' ' + str(i[1]) for i in ls]
    ans = []
    for i in str_ls:
        ans.append('L')
        ans.append(i)
    ans[0] = 'M'
    ans = ' '.join(ans) + ' z'
    return ans


def color_generator(mode=0):
    """
    产生随机颜色
    'Hexadecimal','RGB','binary'
    :param mode:
    :return:
    """
    if mode == 0:
        l = [str(i) for i in range(10)] + [chr(i) for i in range(65, 71)]
        color = '#'
        for i in range(6):
            r = random.randint(0, 15)
            color += l[r]
        return color
    elif mode == 1:
        return np.random.randint(0, 256, 3, dtype='uint8')
    else:
        return np.random.randint(0, 256, 1, dtype='uint8')


def rgb2hsl(rgb):
    """
    rgb与hsl转化
    :param rgb:
    :return:
    """
    color = Color(rgb)
    h, s, l = color.hsl
    return h, s, l


def measure_centroids(contour):
    """
    得到轮廓的位置、面积等信息
    :param contour:
    :return:
    """
    # 求取轮廓的面积
    area = cv2.contourArea(contour)
    # 得到轮廓的外接矩形
    x, y, w, h = cv2.boundingRect(contour)
    # 求取几何矩
    mm = cv2.moments(contour)
    # 得到中心位置
    cx = mm['m10'] / mm['m00']
    cy = mm['m01'] / mm['m00']
    return cx, cy, area


class Temp(drawSvg.Drawing):
    def __init__(self, width=720, height=1280, file=None, **svgArgs):
        """
        模板类，相当于svg背景，填充archi
        :param width:
        :param height:
        :param archi_tree:
        :param svgArgs:
        """
        super().__init__(width, height, origin=(0, -height), **svgArgs)
        self.file = file

    def iter(self):
        """迭代器类型，深度遍历"""
        stack = [self]
        while stack:
            elem = stack.pop()
            yield elem
            if elem == self:
                for i in range(-1, -len(elem.elements) - 1, -1):
                    stack.append(elem.elements[i])
            else:
                for i in range(-1, -len(elem.children) - 1, -1):
                    stack.append(elem.children[i])

    def score(self, im, use_cuda=False):
        if im is None:
            self.savePng('this.png')
            im = cv2.imread('this.png')
        save_path = "./002"
        checkpoint = "epoch_11.loss_0.3825238102562626.pth"
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize([299, 299]),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        im = transform(im)
        resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        net = Net(resnet, n_features=12)
        if use_cuda:
            resnet = resnet.cuda()
            net = net.cuda()
            net.load_state_dict(torch.load(f"{save_path}/{checkpoint}"))
            inp = im.unsqueeze(0).cuda()
            net.eval()
            p = net(inp)
            score = p.detach().cpu().numpy()[0, -1]
            print(f'得分{score}。')
            return score
        else:
            net.load_state_dict(torch.load(f"{save_path}/{checkpoint}", map_location=lambda storage, loc: storage))
            inp = im.unsqueeze(0)
            net.eval()
            p = net(inp)
            score = p.detach().numpy()[0, -1]
            print(f'得分{score}。')
            return score

    def getTree(self):
        return ET.parse(self.file)


class Archi(drawSvg.DrawingParentElement):
    def __init__(self, TAG_NAME='svg', cont=None, out_rect=None, file=None, **args):
        """
        每个archi对应一个svg文件，且其内部有更小的构件
        :param out_rect: [w,h] 外接矩形大小
        :param contour: [point 1,...,point n]，轮廓列表
        """
        super().__init__(**args)
        self.TAG_NAME = TAG_NAME
        self.contour = cont
        self.out_rect = np.array(out_rect)
        self.file = file

    def getTree(self):
        return ET.parse(self.file)

    def iter(self):
        stack = [self]
        while stack:
            elem = stack.pop()
            yield elem
            for i in range(-1, -len(elem.children) - 1, -1):
                stack.append(elem.children[i])


class BasicElement(drawSvg.DrawingBasicElement):
    def __init__(self, TAG_NAME, **args):
        """
        单节点svg元素
        :param TAG_NAME:
        :param args:
        """
        self.TAG_NAME = TAG_NAME
        super().__init__(**args)


class ParentsElement(drawSvg.DrawingParentElement):
    def __init__(self, TAG_NAME, **args):
        """
        多节点svg元素
        :param TAG_NAME:
        :param args:
        """
        self.TAG_NAME = TAG_NAME
        super().__init__(**args)
