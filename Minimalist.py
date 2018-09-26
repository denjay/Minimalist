#!/usr/bin/python3
'''
很早之前写的pythonr软件，代码不好看
操作方法：左键双击窗口换肤，右键双击退出程序；右键单击窗口左侧切换显示流量还是CPU和内存占用；右键单击窗口右侧切换显示全部或一部分内容。
悬浮窗口移动到屏幕右边时会自动隐藏，当鼠标再次移动到悬浮窗口上时，悬浮窗口会弹出。
09版更新：增加CPU和内存占用显示
'''
import time
import pickle
import os
import os.path
import sys
import tkinter as tk


def humanize(flow):
    '''人性化显示流量单位'''
    n = 0
    while flow >= 1000:
        flow /= 1024
        n += 1
    if n == 2:
        return '{:.1f}'.format(flow) + 'MB'
    else:
        return '{:.0f}'.format(flow) + ('B', 'KB')[n]


def get_cpu_and_mem_data():
    global mode1
    global cpu_data0
    global time0
    global flag
    if flag == 0 or time0 == 0:
        time0 = time.time()
        cpu_data0 = open('/proc/stat', 'r').readline().split()[1:]
        time.sleep(0.5)

    time1 = time.time()
    cpu_data1 = open('/proc/stat', 'r').readline().split()[1:]
    cpu_usage_rate = 1 - (int(cpu_data1[3]) - int(cpu_data0[3])) / \
        sum(map(lambda x, y: int(y) - int(x), cpu_data0, cpu_data1))
    # 避免由于计算误差出现使用率超过100%的情况
    if cpu_usage_rate > 1.0:
        cpu_usage_rate = 1.0

    cpu_data0 = cpu_data1
    time0 = time1
    flag = 1
    if mode1 == 1:
        return ' CPU:{:.0f}% '.format(cpu_usage_rate * 100)
    else:
        memory_data = open('/proc/meminfo', 'r').readlines()
        memory_usage_rate = 1 - \
            int(memory_data[2].split()[1]) / int(memory_data[0].split()[1])
        return ' CPU:{:.0f}%   MEM:{:.0f}% '.format(cpu_usage_rate * 100, memory_usage_rate * 100)


# 获得流量数据
def get_net_data():
    global rec_list0
    global tra_list0
    global time0
    global flag
    rec_list1 = []
    tra_list1 = []
    if flag == 1 or time0 == 0:
        rec_list0 = []
        tra_list0 = []
        datas = open('/proc/net/dev', 'r').readlines()[2:]
        time0 = time.time()
        for data in datas:
            rec_list0.append(int(data.split()[1]))
            tra_list0.append(int(data.split()[9]))
        time.sleep(0.5)

    datas = open('/proc/net/dev', 'r').readlines()[2:]
    time1 = time.time()
    for data in datas:
        rec_list1.append(int(data.split()[1]))
        tra_list1.append(int(data.split()[9]))
    receive = max(map(lambda x, y: y - x, rec_list0,
                      rec_list1)) / (time1 - time0)
    transmit = max(map(lambda x, y: y - x, tra_list0,
                       tra_list1)) / (time1 - time0)
    receive = '↓ ' + humanize(receive)
    transmit = '↑ ' + humanize(transmit)
    rec_list0 = rec_list1.copy()
    tra_list0 = tra_list1.copy()
    time0 = time1
    flag = 0
    return '{:<8}'.format(receive), '{:>8} '.format(transmit)


def refresh():
    '''实时刷新流量显示'''
    if mode0 == 0:
        if mode1 == 1:
            l.config(text=get_net_data()[0], width=8)
        elif mode1 == 0:
            l.config(text=''.join(get_net_data()), width=16)
    else:
        if mode1 == 1:
            l.config(text=get_cpu_and_mem_data(), width=10)
        elif mode1 == 0:
            l.config(text=get_cpu_and_mem_data(), width=19)

    root.after(1000, refresh)


def move(e):
    '''移动窗口'''
    if e.x_root < root.winfo_screenwidth() - 10:
        new_x = e.x - x + root.winfo_x()
        new_y = e.y - y + root.winfo_y()
        if new_x < 10:
            new_x = 0
        if new_x > root.winfo_screenwidth() - root.winfo_width() - 10:
            new_x = root.winfo_screenwidth() - 4
        if new_y < 10:
            new_y = 0
        if new_y > root.winfo_screenheight() - root.winfo_height() - 10:
            new_y = root.winfo_screenheight() - root.winfo_height()
        root.geometry('+{}+{}'.format(new_x, new_y))


def click(e):
    '''左键单击窗口时获得鼠标位置，辅助移动窗口'''
    global x
    global y
    x = e.x
    y = e.y


def change_skin(e):
    global skins
    global skin
    if skin == len(skins) - 1:
        skin = 0
    else:
        skin += 1
    l.config(bg=skins[skin][0], fg=skins[skin][1])


def change_mode(e):
    '''切换显示内容'''
    if e.x > root.winfo_width() / 2:
        global mode1
        mode1 = (1 if mode1 == 0 else 0)
    else:
        global mode0
        mode0 = (1 if mode0 == 0 else 0)


def exit_program(e):
    '''退出程序，并保存退出之前状态'''
    if e.x > root.winfo_width() / 2:
        global mode1
        mode1 = (1 if mode1 == 0 else 0)
    else:
        global mode0
        mode0 = (1 if mode0 == 0 else 0)
    pos_x = root.winfo_x()
    pos_y = root.winfo_y()
    dic = {'pos_x': pos_x, 'pos_y': pos_y,
           'mode1': mode1, 'mode0': mode0, 'skin': skin}
    fl = open(sys.path[0] + '/config.pkl', 'wb')
    pickle.dump(dic, fl)
    fl.close()
    exit()


def show(e):
    '''取消隐藏'''
    if root.winfo_x() == root.winfo_screenwidth() - 4:
        root.geometry('+{}+{}'.format(root.winfo_screenwidth() -
                                      root.winfo_width() - 10, root.winfo_y()))


if __name__ == '__main__':
    # 判断是否安装过该软件，如果没有，就开始安装
    if os.path.exists(sys.path[0] + '/config.pkl'):
        fl = open(sys.path[0] + '/config.pkl', 'rb')
        dic = pickle.load(fl)
        fl.close()
        pos_x = dic.get('pos_x')
        pos_y = dic.get('pos_y')
        mode0 = dic.get('mode0')
        mode1 = dic.get('mode1')
        skin = dic.get('skin')
    else:
        version = 0.9
        pos_x = 0  # 窗口起始位置
        pos_y = 0  # 窗口起始位置
        mode0 = 0  # 决定显示的是流量还是内存和CPU占用，0表示显示网速，1表示显示内存和CPU占用
        mode1 = 0  # 显示模式,0表示窗口显示2个数据，1表示只显示下载速度或CPU占用率
        skin = 0  # 皮肤样式

        # 启动器图标所需内容
        content = '''[Desktop Entry]
Encoding=UTF-8
Name=Minimalist
Comment=极简系统监视器
Exec=python3 {}
Icon={}
Categories=Application;
Version={}
Type=Application
Terminal=false\n'''.format(os.path.realpath(__file__), sys.path[0] + '/Minimalist.png', version)
        launcher_path = os.environ['HOME'] + '/.local/share/applications/Minimalist.desktop'
        fl = open(launcher_path, 'w+')
        fl.write(content)
        fl.close()

    rec_list0 = []  # 初始数据
    tra_list0 = []  # 初始数据
    cpu_data0 = 0  # 初始数据
    x = 0  # 用于移动窗口时储存所需鼠标位置
    y = 0  # 用于移动窗口时储存所需鼠标位置
    skins = [('GreenYellow', 'black'), ('#F5BB00', 'white'),
             ('DeepSkyBlue', 'Ivory'), ('Violet', 'Ivory')]
    flag = 0  # 为0时表示上次查看的是流量
    time0 = 0

    root = tk.Tk()
    root.geometry('+{}+{}'.format(pos_x, pos_y))  # 窗口初始位置
    root.overrideredirect(True)  # 去掉标题栏
    root.wm_attributes('-topmost', 1)  # 置顶窗口
    l = tk.Label(root, text='   starting...   ',
                 bg=skins[skin][0], fg=skins[skin][1])
    l.pack()
    l.bind('<Button-1>', click)
    l.bind('<B1-Motion>', move)
    l.bind('<Double-Button-3>', exit_program)
    l.bind('<Double-Button-1>', change_skin)
    l.bind('<Button-3>', change_mode)
    l.bind('<Enter>', show)

    root.after(1000, refresh)
    root.mainloop()
