import pygame
from pygame.locals import QUIT
import sys
import tkinter.messagebox

over_pos = []
source_pos = []  # 起始位置方格
dest_pos = []  # 目标位置方格
block_pos = []  # 障碍物位置方格


# 地图类，地图长宽，初始元素全部为0。0表示可通行点，1表示不可通行点
class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]

    # 生成不可通过点
    def createBlock(self, block_pos):
        for item in block_pos:
            self.map[(item[0][1] - 27) // 44][(item[0][0] - 27) // 44] = 1

    def showMap(self):
        print(30 * '*')
        for row in self.map:
            s = ''
            for entry in row:
                s += ' ' + str(entry) + ' '
            print(s)


# 地图初始化
WIDTH = 14
HEIGHT = 14
map = Map(WIDTH, HEIGHT)


#  搜索路径时用到的节点类
class SearchEntry():
    def __init__(self, x, y, g_cost, f_cost=0, pre_entry=None):
        self.x = x
        self.y = y
        # cost move form start entry to this entry
        self.g_cost = g_cost
        self.f_cost = f_cost
        self.pre_entry = pre_entry

    def getPos(self):
        return self.x, self.y


#  算法主题函数
def A_Star_Search(map, source, dest):
    global over_pos  # 将over_pos设置为全局变量

    #  移动到新位置，当超出地图边界或者新位置是不可同行处，location为当前位置，offset为移动方位
    def getNewPosition(map, location, offset):
        x, y = (location.x + offset[0], location.y + offset[1])
        if x < 0 or x >= map.width or y < 0 or y >= map.height or map.map[y][x] == 1:
            return None
        return (x, y)

    def getPositions(map, location):
        # 定义四邻接移动方式，左右下上
        offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        # 将四个方向的位置都放入poslist数组，然后返回此数组
        poslist = []
        for offset in offsets:
            pos = getNewPosition(map, location, offset)
            if pos is not None:
                poslist.append(pos)
        return poslist

    # 定义返回当前点与目标点曼哈顿距离的函数
    def calHeuristic(pos, dest):
        return abs(dest.x - pos[0]) + abs(dest.y - pos[1])

    def getMoveCost(location, pos):
        if location.x != pos[0] and location.y != pos[1]:
            return 1.4
        else:
            return 1

    # 检查节点是否在list(openlist或closedlist)中
    def isInList(list, pos):
        if pos in list:
            return list[pos]
        return None

    def addAdjacentPositions(map, location, dest, openlist, closedlist):
        poslist = getPositions(map, location)  # 从当前位置搜索四个方向的位置
        for pos in poslist:
            # 如果节点已经在closed表中，那么不用继续放入
            if isInList(closedlist, pos) is None:
                findEntry = isInList(openlist, pos)
                h_cost = calHeuristic(pos, dest)
                g_cost = location.g_cost + getMoveCost(location, pos)
                if findEntry is None:
                    # 如果不在open表中，则置入
                    openlist[pos] = SearchEntry(pos[0], pos[1], g_cost, g_cost + h_cost, location)
                elif findEntry.g_cost > g_cost:
                    # 更新代价
                    findEntry.g_cost = g_cost
                    findEntry.f_cost = g_cost + h_cost
                    findEntry.pre_entry = location

    # 找到open表中最小代价的节点
    def getFastPosition(openlist):
        fast = None
        for entry in openlist.values():
            if fast is None:
                fast = entry
            elif fast.f_cost > entry.f_cost:
                fast = entry
        return fast

    openlist = {}
    closedlist = {}
    location = SearchEntry(source[0], source[1], 0.0)
    dest = SearchEntry(dest[0], dest[1], 0.0)
    openlist[source] = location
    while True:
        location = getFastPosition(openlist)
        if location is None:
            print("can't find valid path")
            break

        if location.x == dest.x and location.y == dest.y:
            break

        closedlist[location.getPos()] = location
        openlist.pop(location.getPos())
        addAdjacentPositions(map, location, dest, openlist, closedlist)

    # 将路径标记为2
    while location is not None:
        map.map[location.y][location.x] = 2
        over_pos.append([[location.x * 44 + 27, location.y * 44 + 27], [255, 200, 0], 3])
        location = location.pre_entry


root = tkinter.Tk()
root.withdraw()
tkinter.messagebox.showinfo('Instructions', 'Click the left mouse button to set the starting point, middle mouse button to set obstacles, and right mouse button to set the target point')
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%使用Pygame进行可视化%%%%%%%%%%%%BY%%%%%%LSW%%%%%%%%%%%%%
# 初始化pygame
pygame.init()
# 获取对显示系统的访问，并创建一个窗口screen
# 窗口大小为670x670
pygame.display.set_caption('A_STAR')
screen = pygame.display.set_mode((670, 670))
screen_color = [0, 0, 0]  # 设置画布颜色
line_color = [255, 255, 255]  # 设置线条颜色


# 输入鼠标点击的位置，返回该位置所在棋盘的区域
def find_pos(x, y):
    for i in range(27, 670 - 44, 44):
        for j in range(27, 670 - 44, 44):
            L1 = i
            L2 = i + 44
            R1 = j
            R2 = j + 44
            if x >= L1 and x <= L2 and y >= R1 and y <= R2:
                return i, j
    return x, y


# 清除one_pos
def clear_pos(one_pos):
    while one_pos:
        one_pos.pop()


flag_mouse = False  # 循环中表征鼠标点击的标签
tim = 0
source_color = [0, 0, 255]  # 起点方格的颜色
dest_color = [255, 0, 255]  # 目标方格的颜色
block_color = [255, 0, 0]  # 不可通行方格的颜色
while True:  # 不断刷新画布
    for event in pygame.event.get():  # 获取事件，如果鼠标点击右上角关闭按钮，关闭
        if event.type is QUIT:
            sys.exit()
    screen.fill(screen_color)  # 清屏
    for i in range(27, 670, 44):
        # 先画竖线
        if i == 27 or i == 670 - 27:  # 边缘粗线
            pygame.draw.line(screen, line_color, [i, 27], [i, 670 - 27], 4)
        else:
            pygame.draw.line(screen, line_color, [i, 27], [i, 670 - 27], 2)
        # 再画横线
        if i == 27 or i == 670 - 27:  # 边缘粗线
            pygame.draw.line(screen, line_color, [27, i], [670 - 27, i], 4)
        else:
            pygame.draw.line(screen, line_color, [27, i], [670 - 27, i], 2)
    # 获取鼠标坐标信息
    x, y = pygame.mouse.get_pos()
    x, y = find_pos(x, y)
    pygame.draw.rect(screen, [0, 229, 238], [x, y, 44, 44], 2)
    keys_pressed = pygame.mouse.get_pressed()  # 获取鼠标按键信息
    # 点击鼠标左键设置起点;点击鼠标中键设置不可通行方格；点击鼠标右键设置目标方格
    if keys_pressed[0]:
        flag_mouse = True
        if source_pos:  # 如果在已存在起始点的情况下继续增加起始点，则需要先弹出先前的点
            source_pos.pop()
        source_pos.append([[x, y], source_color, 0])  # 0表示起点
    if keys_pressed[1]:
        flag_mouse = True
        block_pos.append([[x, y], block_color, 1])  # 1表示障碍物
    if keys_pressed[2]:
        flag_mouse = True
        if dest_pos:
            dest_pos.pop()
        dest_pos.append([[x, y], dest_color, 2])  # 2表示目标点

    # 鼠标左键延时作用
    if flag_mouse:
        tim += 1
    if tim % 200 == 0:  # 延时200ms
        flag_mouse = False
        tim = 0
    map.createBlock(block_pos)
    source = ()
    dest = ()
    # 初始化起始节点与目标节点
    if source_pos:
        source = ((source_pos[0][0][0] - 27) // 44, (source_pos[0][0][1] - 27) // 44)
        clear_pos(over_pos)
    if dest_pos and source_pos:
        dest = ((dest_pos[0][0][0] - 27) // 44, (dest_pos[0][0][1] - 27) // 44)
        clear_pos(over_pos)
        A_Star_Search(map, source, dest)
    for val in over_pos:  # 显示open、closed表中的点
        pygame.draw.rect(screen, val[1], [val[0][0], val[0][1], 44, 44], 0)
    for val in source_pos:  # 显示起始点
        pygame.draw.rect(screen, val[1], [val[0][0], val[0][1], 44, 44], 0)
    for val in dest_pos:  # 显示目标点
        pygame.draw.rect(screen, val[1], [val[0][0], val[0][1], 44, 44], 0)
    for val in block_pos:  # 显示障碍点
        pygame.draw.rect(screen, val[1], [val[0][0], val[0][1], 44, 44], 0)
    pygame.display.update()  # 刷新显示
