# -*- coding: utf-8 -*-
import numpy as np


# ============================================================================
#  LZW  快速壓縮    by Hung1  2019.12.1
# ----------------------------------------------------------------------------
#  使用LZW的方法壓縮字串。
#  由於壓縮字串會產生字典，以字典還原相對應的值，建議在同個系統下使用此類。
#  優點：
#  可以建立到達1,1141,111的字典元素編號
#  缺點：
#  解壓縮比起壓縮慢了5倍(or4倍)，建議少用或者使用雙向字典bidict
#  (~函式註解 ~字串描述)
# ============================================================================
class LZW:
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        self.__dict = {}  # 紀錄壓縮資訊
        self.num = 33  # 字典元素編號起始值(從可顯示字元開始)

    # ------------------------------------------------------------------------
    #  list壓縮成string
    #  直接調用self.__dict執行時間0.026秒，使用d間接調用執行時間0.022秒
    # ------------------------------------------------------------------------
    def compress(self, li: list) -> str:
        clist = []
        d = self.__dict
        for t in li:
            if t not in d:
                d[t] = chr(self.num)
                # d[self.num] = t
                self.num += 1
            clist.append(d[t])
        return ''.join([c for c in clist])

    """
    def zlib_compress(self, l: list) -> str:
        n = ['~'*(i//126)+chr(i%126) for i in ilist]
        return ''.join(n)
    """

    # ------------------------------------------------------------------------
    #  string解壓縮成list
    # ------------------------------------------------------------------------
    def decompress(self, s: str) -> list:
        tlist = []
        d = self.__dict
        for c in s:
            if c not in d.values():
                raise ValueError("No dictionary value found for the string")
            else:
                tlist.append(*[k for k, v in d.items() if v == c])
                # tlist.append(list(d.keys())[list(d.values()).index(c)]) # 方法二
                # tlist.append({v : k for k, v in d.items()}[c]) # 方法三
        return tlist

    # ------------------------------------------------------------------------
    #  快速解壓縮
    #  為了急速轉換，原本解壓比壓縮慢5倍時間，去除raise檢查，變為慢4倍(加速1.25倍)
    #  但發生轉換缺失時會沒有任何提醒
    # ------------------------------------------------------------------------
    def fast_decompress(self, s: str) -> list:
        tlist = []
        d = self.__dict
        for c in s:
            tlist.append(*[k for k, v in d.items() if v == c])
        return tlist

    # ------------------------------------------------------------------------
    #  輸出字典資訊存為檔案
    # ------------------------------------------------------------------------
    def save_data(self, filename: str = 'data/lzwDict'):
        np.save(filename + '.npy', self.__dict)

    # ------------------------------------------------------------------------
    #  載入字典檔案
    # ------------------------------------------------------------------------
    def load_data(self, filename: str = 'data/lzwDict'):
        self.__dict = np.load(filename + '.npy')

    # ------------------------------------------------------------------------
    #  定義物件的字串描述
    # ------------------------------------------------------------------------
    def __str__(self):
        return 'LZW_dict={}'.format(self.__dict)


# 功能測試
if __name__ == '__main__':
    import sys
    import zlib
    import gzip
    import timeit
    import random
    import matplotlib.pyplot as plt

    lzw = LZW()
    # array1 = [(1,1),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4)]
    array1 = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(80)]
    array2 = [(1, 1)]
    array3 = '123aabbcc'
    comp = lzw.compress(array1)
    comp2 = zlib.compress(str(array1).encode())
    print('使用資料：\n', array1)
    print('壓縮後：\n', comp)
    # print(timeit.timeit(stmt="test()", setup="from  __main__ import test", number=1))
    use_time1 = timeit.Timer('_ = str(array1)', 'from __main__ import array1').timeit(1000)
    use_time2 = timeit.Timer('_ = lzw.compress(array1)', 'from __main__ import lzw, array1').timeit(1000)
    use_time3 = timeit.Timer('_ = lzw.decompress(comp)', 'from __main__ import lzw, comp').timeit(1000)
    use_time4 = timeit.Timer('_ = lzw.fast_decompress(comp)', 'from __main__ import lzw, comp').timeit(1000)
    use_time5 = timeit.Timer('_ = zlib.compress(str(array1).encode())', 'from __main__ import zlib, array1').timeit(
        1000)
    use_time6 = timeit.Timer('_ = zlib.decompress(comp2).decode()', 'from __main__ import zlib, comp2').timeit(1000)
    print('使用原字串 %.15f 秒' % use_time1)
    print('  壓縮字串 %.15f 秒' % use_time2)
    print('解壓縮字串 %.15f 秒' % use_time3)
    print('快速解壓縮 %.15f 秒' % use_time4)
    print('  zlib壓縮 %.15f 秒' % use_time5)
    print('zlib解壓縮 %.15f 秒' % use_time6)
    comp_str1 = sys.getsizeof(str(array1))
    comp_str2 = sys.getsizeof(lzw.compress(array1))
    comp_str3 = sys.getsizeof(zlib.compress(str(array1).encode()))
    comp_str4 = sys.getsizeof(gzip.compress(str(array1).encode()))
    print(' str轉換後 %d 字元' % comp_str1)
    print(' lzw壓縮後 %d 字元' % comp_str2)
    print('zlib壓縮後 %d 字元' % comp_str3)
    print('gzip壓縮後 %d 字元' % comp_str4)

    # 時間圖表
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=70)  # plt.subplots(figsize=(6.4, 4.8), dpi=70)
    # fig.set_size_inches(6.4, 4.8)
    ax.set_title('compression and decompression runtime', fontsize=12, color='r')
    plt.xlabel('loop 1000 times')
    plt.ylabel('time (second)')
    # ax.set_xlim([1,6])
    ax.set_xlim([0, 7])
    # data = [use_time1, use_time2, use_time3, use_time4]
    data = [use_time1, use_time2, use_time3, use_time4, use_time5, use_time6]
    # ax.bar([2,3,4,5], data, 0.5, color=['#FF50CC','#FFAA22','#22AAFF','#2277FF'])
    ax.bar([1, 2, 3, 4, 5, 6], data, 0.5, color=['#FF50CC', '#FFAA22', '#22AAFF', '#2277FF', '#666666', '#444444'])
    # ax.set_xticklabels(['', 'str(list)', 'compress', 'dec', 'fast_dec',''])
    ax.set_xticklabels(['', 'str(list)', 'compress', 'dec', 'fast_dec', 'zlib_comp', 'zlib_dec'])
    plt.grid(axis='y', linestyle=':')
    plt.savefig('lzw_bar.png', dpi=600)
    plt.show()

    # 空間圖表
    _, ax = plt.subplots(figsize=(8, 4.5), dpi=70)
    ax.set_title('compressed capacity', fontsize=12, color='r')
    plt.xlabel('use sys.getsizeof() function')
    plt.ylabel('capacity (byte)')
    ax.set_xlim([0, 5])
    data = [comp_str1, comp_str2, comp_str3, comp_str4]
    ax.bar([1, 2, 3, 4], data, 0.4, color=['#FF50CC', '#FFAA22', '#666666', '#884422'])
    ax.set_xticklabels(['', 'str(list)', 'lzw', 'zlib', 'gzip'])
    plt.grid(axis='y', linestyle=':')
    plt.savefig('lzw_bar2.png', dpi=600)
    plt.show()

    # 正則表達式
    # # hex color with no alpha.
    #    match = re.match(r"\A#[a-fA-F0-9]{6}\Z", c)
    #    if match:
    #        return (tuple(int(n, 16) / 255
    #                      for n in [c[1:3], c[3:5], c[5:7]])
    #                + (alpha if alpha is not None else 1.,))

    # level=9
    # compresslevel=9
'''
參考資料：
python 将字典存储为文件(pickle method/numpy method)
https://blog.csdn.net/yangtf07/article/details/81571371
python相关的几种数据类型的存储读取方式
https://blog.csdn.net/index20001/article/details/79431372
'''
