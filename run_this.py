# -*- coding: utf-8 -*-
"""--------------------------------------------------------------------------
魔塔AI演算過程視窗        by Hung1

版本：1.0

更新日誌：
0.01  2019/07/29 開始製作。
0.1   2019/11/26 增加Q Learning V2.0版，高耦合。
0.2   2020/02/02 大幅調整程式結構，優化了各種計算的執行速度，更改使用者介面，
                 支持多樓層環境建立，更新Q Learning，豐富的分析圖表，拔除建圖的動
                 畫過程。
0.3   2020/02/18 增加24層魔塔，可支援該等級魔塔的環境，增加 4 種演算法。
0.4   2020/06/18 大幅更新了所有功能，添加模型預測與動畫顯示和主選單。
1.0   2020/08/18 完成GUI，整合了各種系統，該版本首次發布在Github上
--------------------------------------------------------------------------"""
from window import Window

# ----------------------------------------------------------------------------
#  主程式
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    win = Window()
    win.mainloop()