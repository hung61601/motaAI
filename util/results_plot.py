# -*- coding: utf-8 -*-
import os
import copy
import datetime
import numpy as np
import matplotlib.pyplot as plt


# ============================================================================
#  SaveFile 儲存檔案  V2.0    by Hung1    2020/07/18
# ----------------------------------------------------------------------------
#  可以記錄每一回的訓練結果，並保存至檔案。
#  V1.0    2020.04.27
#  V1.1    2020.05.10
#  新增功能：若指定目錄不存在，則建立目錄
#  rounds變為可選參數
#  新增stop_time參數。sampling會回傳是否到達停止時間
#  將sampling和save_file的例外處理註解起來
#  V2.0    2020.07.18
#  刪減部分功能，適用於於Mota AI V0.4版本
# ============================================================================
class SaveFile:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self, env_name, algorithm_name):
        self.env_name = env_name
        self.score = []
        self._data = {'env_name': env_name,
                      'algorithm': algorithm_name,
                      'start_training_date': datetime.datetime.now(),
                      'score': self.score,
                      'round': []}
        self.dir_path = '../output/'

    # ------------------------------------------------------------------------
    #  取樣(紀錄資料)
    # ------------------------------------------------------------------------
    def sampling(self, score):
        self.score.append(score)

    # ------------------------------------------------------------------------
    #  取得訓練結果
    #  upper_limit: 資料筆數上限
    # ------------------------------------------------------------------------
    def get_data(self, upper_limit=100000):
        if upper_limit < 0 or len(self.score) < upper_limit:
            self._data['score'] = self.score
            self._data['round'] = list(range(1, len(self.score) + 1))
        else:
            c = int(len(self.score) // upper_limit)
            new_score = self.score[::c]
            self._data['score'] = new_score
            self._data['round'] = list(range(1, len(self.score) + 1, c))
        # 返回目前的訓練結果
        return copy.deepcopy(self._data)

    # ------------------------------------------------------------------------
    #  讀取檔案
    # ------------------------------------------------------------------------
    def load_data(self, file_name):
        return np.load(file_name, allow_pickle=True).item()

    # ------------------------------------------------------------------------
    #  訓練結果存檔
    # ------------------------------------------------------------------------
    def save_file(self):
        now_time = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
        file_name = f'{self.dir_path}results_{now_time}.npy'
        np.save(file_name, self.get_data(upper_limit=-1))
        print('output data path:', file_name)
        return file_name


alpha = 0.2  # 線條透明度
unicode_font = 'DFKai\-SB'  # unicode字體


def check_contain_chinese(check_str):
    """檢查是否為非英文字體"""
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def get_figure(data, color, avg_level=-1, exclude_zero=False, **kwargs):
    """產生位圖"""
    fig = plt.Figure(**kwargs)
    ax = fig.add_subplot()
    # fig, ax = plt.subplots(**kwargs)  # 會在Spyder的Console產生圖片
    if check_contain_chinese(data['env_name']):
        ax.set_title(data['env_name'], fontproperties=unicode_font, fontsize=16, color='b')
    else:
        ax.set_title(data['env_name'], fontsize=16, color='b')
    ax.set_xlabel('round')
    ax.set_ylabel('score (hp)')
    # 刪除所有分數為0的紀錄
    if exclude_zero:
        x_data = []
        y_data = []
        for x, y in zip(data['round'], data['score']):
            if y != 0:
                x_data.append(x)
                y_data.append(y)
    else:
        x_data = data['round']
        y_data = data['score']
    data_length = len(y_data)
    # 刻度定位器設置
    # 參考：https://matplotlib.org/3.1.0/api/ticker_api.html
    if not y_data or max(y_data) <= 5:
        ax.yaxis.set_major_locator(plt.MultipleLocator(1))
    if data_length <= 5:
        ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    # 範圍線繪製
    ax.plot(x_data, y_data, label=data['algorithm'], alpha=alpha, color=color)
    # 平均線繪製
    y_avg = []
    if y_data:
        if avg_level < 0:
            v = int(data_length // 100)  # 默認平均線等級
        else:
            v = avg_level
        c = v * 2 + 1
        total = 0
        for i in range(c):
            total += y_data[i]
            y_avg.append(total)
        for i in range(c, data_length):
            total = total + y_data[i] - y_data[i - c]
            y_avg.append(total)
        for i in range(data_length, data_length + c):
            total = total - y_data[i - c]
            y_avg.append(total)
        y_avg = y_avg[v:-v - 1]
        for i in range(v):
            y_avg[i] /= v + i + 1
        for i in range(v, data_length - v):
            y_avg[i] /= c
        for i in range(v, 0, -1):
            y_avg[-i] /= v + i
    ax.plot(x_data, y_avg, label=f"{data['algorithm']}(avg.)", color=color)
    ax.grid(linestyle=':')
    ax.legend(loc='upper left')
    return fig


# 測試
if __name__ == '__main__':
    import time
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    root = tk.Tk()
    sf = SaveFile('可以中文標題environment', 'algorithm')
    startTime = time.perf_counter()
    for test_score in np.sin(np.pi * np.arange(0, 90, 0.9)):
        sf.sampling(test_score)
    print('   sampling time:', time.perf_counter() - startTime)
    startTime = time.perf_counter()
    test_data = sf.get_data()
    test_fig = get_figure(test_data, color='steelblue',  # color='steelblue'/'coral'
                          figsize=(10, 6), facecolor='lavender', dpi=100)
    canvas = FigureCanvasTkAgg(test_fig, root)
    canvas.get_tk_widget().pack()
    print('draw figure time:', time.perf_counter() - startTime)
    root.mainloop()
