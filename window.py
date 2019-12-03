# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import psutil
import time
import sys
import os
import canvas_resize                  # 畫布自由縮放

#----------------------------------------------------------------------------
#  全局變量
#----------------------------------------------------------------------------
MESSAGE_SPEED = 0.1        # 每則訊息發送時間間隔

#============================================================================
#  Window 視窗操作介面  V2.0
#----------------------------------------------------------------------------
#  視覺化的使用者操作視窗。
#  V2.0 改變了版面配置，並支援多層塔的顯示
#============================================================================
class Window(tk.Tk):
    #------------------------------------------------------------------------
    #  初始化
    #------------------------------------------------------------------------
    def __init__(self, version: int):
        super(Window, self).__init__()      # 建立視窗
        self.version = version              # 版本編號
        self.geometry('846x499')            # 視窗大小
        self.title('Mota AI')               # 視窗標題
        self.attributes('-topmost', True)   # 讓窗口保持在上
        #self.resizable(False, False)       # 禁止改變窗口大小
        self.iconbitmap('pictures/th170_kutaka.ico')  # 更換窗口圖標
        self.mota_env = None
        self._build_window()
    #------------------------------------------------------------------------
    #  建立顯示框架
    #------------------------------------------------------------------------
    def _build_window(self):
        # 地圖顯示區
        frm = ttk.LabelFrame(self, text='Compiled Map')
        frm.place(height=-40, relwidth=0.6, relheight=1.0)
        # 文件名顯示
        self.lab = tk.Label(self, text='Ver {}'.format(self.version) ,font=('Arial', 12))
        self.lab.place(y=2, relx=0.6, relwidth=0.4)
        # 主按鈕
        self.main_btn = ttk.Button(self, width=20, text='選擇地圖文件', command=self.open_file)
        self.main_btn.place(x=40, y=25, width=-80, height=30, relx=0.6, relwidth=0.4)
        # 地圖按鈕
        self.up_btn = ttk.Button(self, width=20, text='下一層', command=self.floor_down)
        self.up_btn.place(y=-35, rely=1.0, relx=0.0, relwidth=0.2)
        self.up_btn.config(state='disabled')
        self.now_btn = ttk.Button(self, width=20, text='顯示屬性', command=self.floor_show)
        self.now_btn.place(y=-35, rely=1.0, relx=0.2, relwidth=0.2)
        self.now_btn.config(state='disabled')
        self.down_btn = ttk.Button(self, width=20, text='上一層', command=self.floor_up)
        self.down_btn.place(y=-35, rely=1.0, relx=0.4, relwidth=0.2)
        self.down_btn.config(state='disabled')
        # LOGO
        im = Image.open('pictures/logo.jpg')
        self.img = ImageTk.PhotoImage(im)
        imLabel = tk.Label(self, image=self.img)
        imLabel.place(y=60, relx=0.6, relwidth=0.4)
        # 訊息(進程)提示
        frm2 = ttk.LabelFrame(self, text='Information')
        scr = scrolledtext.ScrolledText(frm2)
        scr.pack(fill='both', expand=True)
        frm2.place(x=10, y=120, width=-20, height=-130, relx=0.6, relwidth=0.4, relheight=1.0)
        # 初始提示
        scr.insert(tk.END, '根目錄下有data/mapData.txt可作為範例，\n')
        scr.insert(tk.END, '選擇檔案後將逐步運行程式。\n')
        scr.insert(tk.END, '如果要創新地圖，請到database.py做設定。\n\n')
        info = psutil.virtual_memory()
        scr.insert(tk.END, '内存使用量﹍： %12d bytes\n' % psutil.Process(os.getpid()).memory_info().rss)
        scr.insert(tk.END, '總內存﹍﹍﹍： %12d bytes\n' % info.total)
        scr.insert(tk.END, '總內存使用率： %12s %%\n' % info.percent)
        scr.insert(tk.END, 'ＣＰＵ個數﹍： %12d 個\n' % psutil.cpu_count(logical=True))
    #------------------------------------------------------------------------
    #  開啟檔案
    #------------------------------------------------------------------------
    def open_file(self):
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.realpath(sys.argv[0])),
            title='選擇一個地圖數據：(Excel編輯的txt檔)',
            filetypes=[('mapData', '.txt')])
        if filename != '':
            self.lab.config(text = os.path.basename(filename))
            # 繪製地圖時出錯，則返回錯誤訊息
            mapData = self.read_mapTxt(filename)
            if self.draw_map(mapData):
                messagebox.showwarning('友情提醒', '你的電腦遭到不明侵入...咳咳\n是文字檔格式不對，請重新檢查！')
            else:
                self.main_btn.config(state='disabled')
                global cv
                cv = canvas_resize.Zoom_Advanced(frm, path='data/motaMap.png')
                cv.update()
                # 加載數據庫
                database.load_data(os.path.basename(filename))
                self.add_information('-------------------------------------\n'
                                '已成功讀取地圖數據，並產生完成圖片。\n')
                self.add_information('請按下一步...\n')
                self.main_btn.config(text='開始建圖', command=lambda: self.button_create_nodes(mapData), state='enabled')
    #------------------------------------------------------------------------
    #  讀取檔案
    #------------------------------------------------------------------------
    def read_mapTxt(filename):
        # 讀取檔案
        with open(filename, mode = 'r', encoding = 'utf-8') as file:
            # 用 while 逐行讀取檔案內容，直至檔案結尾
            maxCol = 0
            maxRow = 0
            mapArray = []
            lineArray = list(map(int, file.readline().split())) # 數字陣列
            while lineArray:
                # 將地圖數據保存至二維陣列(全數字)
                mapArray.append(lineArray)
                  # 更新最大行列數
                if len(lineArray) > maxCol:
                     maxCol = len(lineArray)
                maxRow += 1
                lineArray = list(map(int, file.readline().split()))
        file.close()
        mapData = (mapArray, maxCol, maxRow)
        return mapData
    #------------------------------------------------------------------------
    #  繪製地圖
    #------------------------------------------------------------------------
    def draw_map(mapData):
        mapArray, maxCol, maxRow = mapData
        # 利用地圖數據還原出地圖圖片
        finImage = Image.new('RGBA', (maxCol*32, maxRow*32))
        tileImage = Image.open('pictures/baseTile.png')
        floorTile = tileImage.crop((32, 0, 64, 32))
        for j in range(maxRow):
            for i in range(maxCol):
                try:
                    tileID = int(mapArray[j][i])
                except:
                    tileID = 0  # 當沒有編號時，默認為0(牆壁)
                # 編號超出範圍，返回錯誤結果
                if 0 > tileID > 255:
                    return True
                # 當是事件時，先繪製地板
                if tileID > 1:
                    finImage.paste(floorTile, (i * 32, j * 32))
                # 獲取事件圖塊
                local = (tileID % 16 * 32, tileID // 16 * 32, tileID % 16 * 32 + 32, tileID // 16 * 32 + 32)
                eventTile = tileImage.crop(local)
                # 分離通道並進行透明度拼貼
                r,g,b,a = eventTile.split()
                finImage.paste(eventTile, (i * 32, j * 32), mask = a)
        # 將已繪製完成的圖片儲存
        finImage.save('data/motaMap.png')
    #------------------------------------------------------------------------
    #  添加提示訊息
    #------------------------------------------------------------------------
    def add_information(text):
        scr.insert(tk.END, text)
        scr.see(tk.END)
        time.sleep(MESSAGE_SPEED)
        scr.update()
    #------------------------------------------------------------------------
    #  切換下一層樓
    #------------------------------------------------------------------------
    def floor_down(self):
        pass
    #------------------------------------------------------------------------
    #  顯示
    #------------------------------------------------------------------------
    def floor_show(self):
        pass
    #------------------------------------------------------------------------
    #  切換下一層樓
    #------------------------------------------------------------------------
    def floor_up(self):
        pass

if __name__ == '__main__':
    env = Window()
    env.mainloop()