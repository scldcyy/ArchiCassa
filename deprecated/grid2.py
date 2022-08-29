def drawRandomGrid2(savePath, temp):
    """
    网格布局
    :param savePath:
    :param temp:
    :return:
    """
    colorTemplate = ac.find('colors')[0].get('colors').split(' ')
    layout = ac.find('layout')
    archiInterval = eval(layout.get('archi-interval')[:-1]) * temp.width
    rasterNum = eval(layout.find('raster').get('num'))
    backgroundShadow = layout.find('background-shadow')
    prospectShot = layout.find('prospect-shot')
    cloud = layout.find('cloud')
    archis = temp.elements
    h_divide_w = np.array([archi.out_rect[1] / archi.out_rect[0] for archi in archis])
    num = len(archis)
    w = temp.width
    h = temp.height
    rect_ls = [[0, 0, w / 2, h], [w / 2, 0, w / 2, h]]
    while len(rect_ls) < num:
        # S = [0.0] + [rect[2] * rect[3] / w / h for rect in rect_ls]
        # S_cum = [S[i] + S[i + 1] for i in range(len(S) - 1)]
        # chs = random.random()
        # for i in range(len(S_cum)):
        #     if chs <= S_cum[i]:
        #         break
        i = np.argmax([rect[2] * rect[3] for rect in rect_ls])
        r = rect_ls.pop(i)
        # direct = random.randint(0, 1)
        direct = np.argmax(r[2:])
        if direct == 0:
            slc = random.uniform(r[2] * 0.4, r[2] * 0.6)
            # slc = r[2] / 2
            ele1 = [r[0], r[1], slc, r[3]]
            ele2 = [r[0] + slc, r[1], r[2] - slc, r[3]]
        else:
            slc = random.uniform(r[3] * 0.4, r[3] * 0.6)
            # slc = r[3] / 2
            ele1 = [r[0], r[1], r[2], slc]
            ele2 = [r[0], r[1] + slc, r[2], r[3] - slc]
        rect_ls = rect_ls[:i] + [ele1, ele2] + rect_ls[i:]
    for i in range(num):
        print(h_divide_w[i])
    for i, archi in enumerate(archis):
        archi_h_div_w = h_divide_w[i]
        const_w, const_h = rect_ls[i][2], rect_ls[i][3]
        step = const_w
        if archi_h_div_w > const_h / const_w:
            step = const_h / archi_h_div_w
        ratio = step / archi.out_rect[0] * 0.8
        c = color_generator()
        update_dict = {
            'transform': f'translate({rect_ls[i][0] + (rect_ls[i][2] - archi.out_rect[0] * ratio) / 2}'
                         f',{rect_ls[i][1] + (rect_ls[i][3] - archi.out_rect[1] * ratio) / 2}) scale({ratio})',
            'fill': c,
            'stroke': c}
        archi.args.update(update_dict)
        # archi.children = [archi.children[0]]
    for i in range(num):
        temp.elements = [(BasicElement(TAG_NAME='rect', x=rect_ls[i][0] + 5, y=rect_ls[i][1] + 5,
                                       width=rect_ls[i][2] - 10,
                                       height=rect_ls[i][3] - 10, fill=color_generator()))] + temp.elements
    temp.saveSvg(savePath)