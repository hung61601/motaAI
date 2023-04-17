# -*- coding: utf-8 -*-
import os
import sys
current_dir = os.path.dirname(sys.argv[0])
lib_dir = os.path.join(current_dir, 'lib')
sys.path.append(lib_dir)
# os.environ['path'] += ';./lib'

import re
import time
import psutil
import datetime
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.font as tkFont
import numpy.distutils.cpuinfo
from PIL import ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from widget.label_image import LabelImage
from widget.frame_scrollbar import FrameScrollbar
from widget.advanced_form import AdvancedForm
from widget.combobox import ExtendCombobox
from widget.tooltip import Tooltip
from widget.animation_environment import Mota
from util.model import MotaModel
from util import results_plot
import calculation
from translation import ui_text as UItext


# ============================================================================
#  Window 視窗操作介面  V3.0    by Hung1    2020/6/18
# ----------------------------------------------------------------------------
#  視覺化的使用者操作視窗。
#  V2.0 改變了版面配置，並支援多層塔的顯示
#  V3.0 大幅更新了所有功能，添加模型預測與動畫顯示和主選單
# ============================================================================
class Window(tk.Tk):
    # ------------------------------------------------------------------------
    #  初始化
    # ------------------------------------------------------------------------
    def __init__(self):
        super(Window, self).__init__()                     # 建立視窗
        self.version = UItext.LABEL['version']             # 版本編號
        win_width = 800                                    # 視窗大小
        win_height = 600
        x = (self.winfo_screenwidth() - win_width) // 2
        y = (self.winfo_screenheight() - win_height) // 3
        self.geometry('%sx%s+%s+%s' % (win_width, win_height, x, y))
        self.minsize(win_width, win_height)                # 最小縮放範圍
        author = '      – by Hung1'
        self.title(UItext.LABEL['window_title'] + author)  # 視窗標題
        self.iconbitmap('pictures/th170_kutaka.ico')       # 更換窗口圖標
        self.floor_max = 0                                 # 樓層最大值
        self.floor_index = 0                               # 樓層索引值
        self.action_list = []                              # 行動列表
        self.cal = calculation.Calculation()
        self.style_design()
        self.build_menu_window()
        self.build_train_window()

    # ------------------------------------------------------------------------
    #  樣式設計
    # ------------------------------------------------------------------------
    def style_design(self):
        # 預設字體設定
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(**UItext.FONT['TkDefaultFont'])
        text_font = tkFont.nametofont("TkTextFont")
        text_font.configure(**UItext.FONT['TkTextFont'])
        fixed_font = tkFont.nametofont("TkFixedFont")
        fixed_font.configure(**UItext.FONT['TkFixedFont'])
        # Changing Widget Colors 更改小部件顏色
        # https://wiki.tcl-lang.org/page/Changing+Widget+Colors
        style = ttk.Style(self)
        style.theme_use('clam')
        # 刪除「獲得焦點時」，會出現一圈虛線的樣式
        # print(style.layout('TButton'))
        style.layout('TButton', [
            ('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [
                # ('Button.focus', {'sticky': 'nswe', 'children': [
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'})]
                        })]
                    })]
                # })]
            )
        style.layout('TNotebook.Tab', [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                    # ('Notebook.focus', {'side': 'top', 'sticky': 'nswe', 'children': [
                        ('Notebook.label', {'side': 'top', 'sticky': ''})]
                        })]
                    # })]
                })]
            )
        style.configure('red.TButton', background='#FFEEEE', bordercolor='red',
                        font=UItext.FONT['menu_normal'])
        style.configure('blue.TButton', background='#EEEEFF', bordercolor='blue',
                        font=UItext.FONT['menu_normal'])
        style.configure('green.TButton', background='#EEFFEE', bordercolor='green',
                        font=UItext.FONT['menu_normal'])
        style.map('red.TButton', font=[('active', UItext.FONT['menu_active'])],
                  foreground=[('pressed', '#FF5555'), ('active', 'black')],
                  background=[('pressed', '#FFFF55'), ('active', '#FF6666')])
        style.map('blue.TButton', font=[('active', UItext.FONT['menu_active'])],
                  foreground=[('pressed', '#5555FF'), ('active', 'black')],
                  background=[('pressed', '#FFFF55'), ('active', '#6666FF')])
        style.map('green.TButton', font=[('active', UItext.FONT['menu_active'])],
                  foreground=[('pressed', '#33AA33'), ('active', 'black')],
                  background=[('pressed', '#FFFF55'), ('active', '#33AA33')])
        style.configure('sub.TButton', background='#223A33', foreground='white',
                        bordercolor='black', font=UItext.FONT['sub_menu'])
        style.map('sub.TButton', bordercolor=[('active', '#FFFF00')],
                  foreground=[('active', '#FFFF55')],
                  background=[('active', '#334A55')])
        style.configure('TNotebook', background='#FFF5DD')
        style.configure('TNotebook.Tab', background='bisque')
        style.map('TNotebook.Tab',
                  background=[('selected', 'turquoise')])
        style.configure('attribute.Treeview.Heading', background='#FFDD88', selectbackground='blue')
        style.map('attribute.Treeview.Heading',
                  background=[('active', '#FFFF88')])
        style.map('attribute.Treeview',
                  background=[('selected', '#7755FF')])
        style.configure('state.Treeview', rowheight=25, font=UItext.FONT['state_table'])
        style.configure('state.Treeview.Heading',
                        background='#888866', foreground='white', relief='flat', rowheight=10)
        style.map('state.Treeview.Heading',
                  background=[('active', '#888866')],
                  relief=[('active', 'groove')])
        style.configure('switch.TButton', background='#66AA88',
                        lightcolor='white', darkcolor='black', bordercolor='#AA6600')
        style.map('switch.TButton',
                  background=[('disabled', '#DCDAD5'), ('pressed', '#AAEECC'), ('active', '#99DDBB')])
        style.configure('TCombobox')
        style.map('TCombobox',
                  fieldbackground=[('readonly', 'white')],
                  selectbackground=[('readonly', 'white')],
                  selectforeground=[('readonly', 'black')])
        style.configure('yellow.TButton', background='#CCFFEE',
                        lightcolor='white', darkcolor='black', bordercolor='black')
        style.map('yellow.TButton',
                  background=[('pressed', 'white'), ('active', '#FFFF88')])
        style.configure('stop.TButton', background='#CCFFEE', foreground='red',
                        lightcolor='white', darkcolor='black', bordercolor='black')
        style.map('stop.TButton',
                  background=[('pressed', 'white'), ('active', '#FFFF88')])

    # ------------------------------------------------------------------------
    #  建立主選單框架
    # ------------------------------------------------------------------------
    def build_menu_window(self):
        # Menubutton 選單按鈕
        # 背景圖片
        self.background = LabelImage(self, 'pictures/background.jpg')
        self.background.pack(fill='both', expand=1)
        # 主選單按鈕
        self.menu_btn_img1 = ImageTk.PhotoImage(file='pictures/th170_kutaka.ico')
        self.menu_btn_img2 = ImageTk.PhotoImage(file='pictures/th170_keiki.png')
        self.menu_btn_img3 = ImageTk.PhotoImage(file='pictures/th110_koishi.png')
        self.menu_btn1 = ttk.Button(self, text=UItext.BUTTON['menu_btn1'], image=self.menu_btn_img1,
                                    compound='left', style='red.TButton', command=self.main_menu_command1)
        self.menu_btn1.place(x=-120, relx=0.5, rely=0.45, width=240)
        self.menu_btn2 = ttk.Button(self, text=UItext.BUTTON['menu_btn2'], image=self.menu_btn_img2,
                                    compound='left', style='blue.TButton', command=self.main_menu_command2)
        self.menu_btn2.place(x=-120, relx=0.5, rely=0.6, width=240)
        self.menu_btn3 = ttk.Button(self, text=UItext.BUTTON['menu_btn3'], image=self.menu_btn_img3,
                                    compound='left', style='green.TButton', command=self.main_menu_command3)
        self.menu_btn3.place(x=-120, relx=0.5, rely=0.75, width=240)
        # 文字LOGO
        self.text_logo = self.background.create_label_widget('pictures/text_logo.png', master=self)
        self.text_logo.place(x=-290, y=-60, relx=0.5, rely=0.2)
        # 作者訊息
        self.author_msg = self.background.create_label_widget(master=self, text=UItext.LABEL['author_msg'])
        self.author_msg.place(x=-232, y=-24, width=220, height=16, relx=1.0, rely=1.0)
        # 選單標題
        self.menu_lab = self.background.create_label_widget('pictures/menu_red.png', master=self,
                                                            font=UItext.FONT['menu_label'])
        # 選單按鈕
        self.menu_sub_btn = []
        for i in range(4):
            self.menu_sub_btn.append(ttk.Button(self, style='sub.TButton'))

    # ------------------------------------------------------------------------
    #  建立訓練視窗框架
    # ------------------------------------------------------------------------
    def build_train_window(self):
        # 地圖顯示
        self.frm = tk.LabelFrame(self, text=UItext.FRAME['animation_map'], bg='#FFF5DD')
        self.mota_env = Mota(self.frm)
        self.anima_frm = self.mota_env.anima_frame
        # 地圖工具提示
        self.map_lab_tooltip_img = ImageTk.PhotoImage(file='pictures/tooltip.png')
        self.map_lab_tooltip = tk.Label(self, image=self.map_lab_tooltip_img, bg='#FFF5DD', bd=0)
        self.map_lab_tooltip_window = Tooltip(self.map_lab_tooltip, wait_time=100)
        # 選項卡
        self.nb = ttk.Notebook(self)
        self.tab1 = FrameScrollbar(self.nb, bg='lavender')
        self.nb.add(self.tab1, text=UItext.FRAME['tab1'])
        self.tab2 = FrameScrollbar(self.nb, bg='lightyellow', contents_center=True)
        self.nb.add(self.tab2, text=UItext.FRAME['tab2'])
        # 資料庫選擇窗口
        self.dataset_frm = tk.LabelFrame(self, text=UItext.FRAME['dataset'], bg='#FFF5DD')
        self.dataset_main_lab = tk.Label(self.dataset_frm, text=UItext.LABEL['dataset'],
                                         font=UItext.FONT['dataset_title'], fg='deep pink', bg='#FFF5DD')
        self.dataset_main_lab.place(relx=0.46, rely=0.01, relwidth=0.53)
        self.dataset_lab1 = tk.Label(self.dataset_frm, text=UItext.LABEL['dataset_lab1'], bg='#FFF5DD')
        self.dataset_lab1.place(relx=0.01, rely=0.04, relwidth=0.15)
        self.dataset_lab2 = tk.Label(self.dataset_frm, text=UItext.LABEL['dataset_lab2'], bg='#FFF5DD')
        self.dataset_lab2.place(relx=0.01, rely=0.10, relwidth=0.15)
        self.dataset_lab3 = tk.Label(self.dataset_frm, text=UItext.LABEL['dataset_lab3'], bg='#FFF5DD')
        self.dataset_lab3.place(relx=0.01, rely=0.16, relwidth=0.28)
        self.dataset_lab4 = tk.Label(self.dataset_frm, text=UItext.LABEL['dataset_lab4'], bg='#FFF5DD')
        self.dataset_lab4.place(relx=0.31, rely=0.16, relwidth=0.68)
        self.dataset_lab5 = tk.Label(self.dataset_frm, height=2, wraplength=240, fg='purple', bg='#FFF5DD',
                                     text=UItext.LABEL['dataset_tips'], font=UItext.FONT['dataset_tips'])
        self.dataset_lab5.place(relx=0.46, rely=0.07, relwidth=0.53)
        self.dataset_comb1 = ExtendCombobox(self.dataset_frm, state='readonly')
        self.dataset_comb1.bind('<<ComboboxSelected>>', self.environment_callback)
        self.dataset_comb1.place(relx=0.16, rely=0.04, relwidth=0.28)
        self.dataset_comb2 = ExtendCombobox(self.dataset_frm, state='readonly')
        self.dataset_comb2.bind('<<ComboboxSelected>>', self.algorithm_callback)
        self.dataset_comb2.place(relx=0.16, rely=0.10, relwidth=0.28)
        self.file_name_dict = {}  # 檔案名稱字典
        columns = UItext.TABLE['path_file1_columns']
        widths = UItext.TABLE['path_file1_widths']
        self.dataset_form1 = AdvancedForm(self.dataset_frm, columns, widths, [], bg='#FEF4B7')
        self.dataset_form1.treeview.config(style='attribute.Treeview')
        self.dataset_form1.treeview.bind('<ButtonRelease-1>', self.dataset_insert)
        self.dataset_form1.place(relx=0.01, rely=0.21, relwidth=0.28, relheight=0.78)
        columns = UItext.TABLE['path_file2_columns']
        widths = UItext.TABLE['path_file2_widths']
        self.dataset_form2 = AdvancedForm(self.dataset_frm, columns, widths, [], bg='#FEF4B7')
        self.dataset_form2.treeview.config(style='attribute.Treeview')
        self.dataset_form2.treeview.bind('<ButtonRelease-1>', self.dataset_delete)
        self.dataset_form2.place(relx=0.31, rely=0.21, relwidth=0.68, relheight=0.78)
        # 狀態訊息
        # 參考：https://stackoverflow.com/questions/42708050/tkinter-treeview-heading-styling
        self.build_state_table()
        # 切換按鈕
        self.down_btn = ttk.Button(self, text=UItext.BUTTON['down'], style='switch.TButton')
        self.switch_btn = ttk.Button(self, text=UItext.BUTTON['attribute_disable'], style='switch.TButton')
        self.up_btn = ttk.Button(self, text=UItext.BUTTON['up'], style='switch.TButton')
        self.down_btn.config(state='disabled', command=self.floor_down)
        self.switch_btn.config(state='disabled', command=self.switch_nb_window)
        self.up_btn.config(state='disabled', command=self.floor_up)
        # 地圖名稱
        self.name_lab = self.background.create_label_widget(master=self, text=self.version,
                                                            font=UItext.FONT['version'])
        # 節點連線顯示按鈕
        self.line_visible_img = ImageTk.PhotoImage(file='pictures/line_visible.png')
        self.line_invisible_img = ImageTk.PhotoImage(file='pictures/line_invisible.png')
        self.line_btn = tk.Button(self, image=self.line_visible_img, background='#FEF2B8',
                                  compound='center', command=self.change_line_state)
        Tooltip(self.line_btn, text=UItext.TOOLTIP['event_link_btn'])
        # 橫幅LOGO
        self.logo_center_img = ImageTk.PhotoImage(file='pictures/logo_center.png')
        self.logo_center = tk.Label(self, image=self.logo_center_img, background='#8ECCF3', bd=0)
        self.logo_left_img = ImageTk.PhotoImage(file='pictures/logo_left.png')
        self.logo_left = tk.Label(self, image=self.logo_left_img, bd=0)
        self.logo_right_img = ImageTk.PhotoImage(file='pictures/logo_right.png')
        self.logo_right = tk.Label(self, image=self.logo_right_img, bd=0)
        Tooltip(self.logo_center, text=UItext.TOOLTIP['picture'], wait_time=1000)  # 彩蛋
        # 輸入資料標題
        self.enter_lab1 = self.background.create_label_widget(master=self)
        self.enter_lab2 = self.background.create_label_widget(master=self)
        self.enter_lab3 = self.background.create_label_widget(master=self)
        # 工具提示
        self.lab_tooltip = self.background.create_label_widget('pictures/tooltip.png', master=self)
        self.lab_tooltip_window = Tooltip(self.lab_tooltip, wait_time=100)
        # 下拉式選單
        self.enter_comb = ExtendCombobox(self, state='readonly')
        self.enter_comb2 = ExtendCombobox(self, state='readonly')
        # 輸入框
        self.enter_en = ttk.Entry(self)
        # 滑動條
        self.fast_lab = self.background.create_label_widget('pictures/fast.png', master=self)
        self.pause_lab = self.background.create_label_widget('pictures/pause.png', master=self)
        self.speed_scale = tk.Scale(self, label=UItext.LABEL['speed_scale'], bg='#FFE8A9',
                                    highlightthickness=4, highlightbackground='#FEFDD1',
                                    from_=0, to=500, orient='horizontal',
                                    showvalue=True, tickinterval=250, resolution=10,
                                    command=self.set_interval_time)
        self.speed_scale.set(250)
        # 返回按鈕
        self.back_btn_img = ImageTk.PhotoImage(file='pictures/back.png')
        self.back_btn = ttk.Button(self, text=UItext.BUTTON['back'], image=self.back_btn_img,
                                   compound='left', style='yellow.TButton')
        # 前進按鈕
        self.play_btn_img = ImageTk.PhotoImage(file='pictures/play.png')
        self.play_btn = ttk.Button(self, text=UItext.BUTTON['play'], image=self.play_btn_img,
                                   compound='left', style='yellow.TButton')
        # 確認按鈕
        self.enter_btn_img = ImageTk.PhotoImage(file='pictures/ok.png')
        self.enter_btn = ttk.Button(self, text=UItext.BUTTON['enter'], image=self.enter_btn_img,
                                    compound='left', style='yellow.TButton')
        # 中止按鈕
        self.stop_btn_img = ImageTk.PhotoImage(file='pictures/stop.png')
        self.stop_btn = ttk.Button(self, text=UItext.BUTTON['stop'], image=self.stop_btn_img,
                                   compound='left', style='stop.TButton',
                                   command=self.cal.stop)
        # 選項按鈕
        self.option_btn1 = ttk.Button(self, style='yellow.TButton')
        self.option_btn2 = ttk.Button(self, style='yellow.TButton')
        # 行動列表
        columns = UItext.TABLE['action_list_columns']
        widths = UItext.TABLE['action_list_widths']
        self.actions_form = AdvancedForm(self, columns, widths, [], bg='#FEF4B7')
        self.actions_form.treeview.config(style='attribute.Treeview')
        self.actions_form.treeview.bind('<ButtonRelease-1>', self.actions_form_click_on)
        # 訊息文本
        self.info_frm = tk.LabelFrame(self, text=UItext.FRAME['information'], bg='#FEF4B7')
        self.info_text = scrolledtext.ScrolledText(self.info_frm, wrap='word',  # 自動換行
                                                   font=UItext.FONT['information'])
        self.info_text.tag_config('tips', foreground='#0000AA', font=UItext.FONT['information'])
        self.info_text.tag_config('obvious', foreground='#AA0000', font=UItext.FONT['information'])
        self.info_text.config(state='disabled')
        self.info_text.pack(fill='both', expand=True)
        # 返回主選單按鈕
        self.home_btn_img = ImageTk.PhotoImage(file='pictures/home.png')
        self.home_btn = tk.Button(self, text=UItext.BUTTON['home'], image=self.home_btn_img,
                                  compound='left', command=self.return_menu_window)

    # ------------------------------------------------------------------------
    #  建立狀態窗口
    # ------------------------------------------------------------------------
    def build_state_table(self):
        columns = UItext.TABLE['state_columns']
        widths = UItext.TABLE['state_widths']
        self.mota_env.build_state_table(self, columns, widths, show='headings',
                                        height=1, style='state.Treeview')
        self.state_table = self.mota_env.state_table

    # ------------------------------------------------------------------------
    #  添加訊息文本內容
    # ------------------------------------------------------------------------
    def add_info(self, text, *args, sleep_time=0.0, clear=False, update=False):
        self.info_text.config(state='normal')
        if sleep_time > 0:
            time.sleep(sleep_time)
        if clear:
            self.info_text.delete(1.0, 'end')
        self.info_text.insert('end', text, *args)
        self.info_text.config(state='disabled')
        if update:
            self.info_text.see('end')
            self.info_text.update()

    # ------------------------------------------------------------------------
    #  添加電腦系統訊息文本
    # ------------------------------------------------------------------------
    def insert_pc_system_info(self):
        self.add_info(UItext.INFO['pc_info1'])
        info = psutil.virtual_memory()
        processor_name = numpy.distutils.cpuinfo.cpu.info[0]['ProcessorNameString']
        total_memory_bytes = info.total
        memory_bytes = psutil.Process(os.getpid()).memory_info().rss
        self.add_info(UItext.INFO['pc_info2'] % processor_name)
        self.add_info(UItext.INFO['pc_info3'] % (total_memory_bytes / 1024 / 1024 / 1024))
        self.add_info(UItext.INFO['pc_info4'] % (memory_bytes / 1024 / 1024 / 1024))
        self.add_info(UItext.INFO['pc_info5'] % info.percent)
        self.add_info(UItext.INFO['pc_info6'] % psutil.cpu_count())
        self.add_info(UItext.INFO['pc_info7'] % psutil.cpu_count(logical=False))

    # ------------------------------------------------------------------------
    #  返回主選單窗口
    # ------------------------------------------------------------------------
    def return_menu_window(self):
        # 進行中標誌
        self.processing = False
        # 建立新遊戲環境
        self.mota_env.destroy_anima_frame()
        self.mota_env.destroy_state_table()
        del self.mota_env
        self.mota_env = Mota(self.frm)
        self.anima_frm = self.mota_env.anima_frame
        self.build_state_table()
        self.update_switch_btn(disable=True)
        self.map_lab_tooltip.place_forget()
        self.frm.place_forget()
        self.dataset_frm.place_forget()
        self.tab1.clear()
        self.tab2.clear()
        self.down_btn.place_forget()
        self.switch_btn.place_forget()
        self.up_btn.place_forget()
        self.name_lab.config(text=self.version)
        self.name_lab.place_forget()
        self.line_btn.config(image=self.line_visible_img)
        self.line_btn.place_forget()
        self.logo_center.place_forget()
        self.logo_left.place_forget()
        self.logo_right.place_forget()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_lab2.place_forget()
        self.enter_lab3.place_forget()
        self.enter_comb.set('')
        self.enter_comb.config(state='readonly')
        self.enter_comb.unbind('<<ComboboxSelected>>')
        self.enter_comb2.set('')
        self.enter_comb2.config(state='readonly')
        self.enter_en.config(state='enabled', justify='left')
        self.enter_en.delete(0, 'end')
        self.enter_comb.place_forget()
        self.enter_comb2.place_forget()
        self.enter_en.place_forget()
        self.back_btn.place_forget()
        self.play_btn.place_forget()
        self.enter_btn.place_forget()
        self.stop_btn.place_forget()
        self.option_btn1.config(state='enabled')
        self.option_btn2.config(state='enabled')
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        self.fast_lab.place_forget()
        self.pause_lab.place_forget()
        self.speed_scale.place_forget()
        self.actions_form.place_forget()
        self.info_frm.place_forget()
        self.add_info('', clear=True)
        self.home_btn.place_forget()
        self.text_logo.place(x=-290, y=-60, relx=0.5, rely=0.2)
        self.author_msg.place(x=-232, y=-24, width=220, height=16, relx=1.0, rely=1.0)
        self.menu_btn1.place(x=-120, relx=0.5, rely=0.45, width=240)
        self.menu_btn2.place(x=-120, relx=0.5, rely=0.6, width=240)
        self.menu_btn3.place(x=-120, relx=0.5, rely=0.75, width=240)
        self.menu_lab.place_forget()
        for i in range(4):
            self.menu_sub_btn[i].place_forget()

    # ------------------------------------------------------------------------
    #  隱藏主選單窗口
    # ------------------------------------------------------------------------
    def hide_menu_window(self):
        self.menu_btn1.place_forget()
        self.menu_btn2.place_forget()
        self.menu_btn3.place_forget()
        self.text_logo.place_forget()
        self.author_msg.place_forget()
        self.menu_lab.place_forget()
        for i in range(4):
            self.menu_sub_btn[i].place_forget()

    # ------------------------------------------------------------------------
    #  產生通關路線之選項
    # ------------------------------------------------------------------------
    def main_menu_command1(self):
        self.menu_btn1.place_forget()
        self.menu_btn2.place_forget()
        self.menu_btn3.place_forget()
        self.background.change_widget_image(self.menu_lab, 'pictures/menu_red.png')
        self.menu_lab.place(x=-120, relx=0.5, rely=0.4, width=240)
        self.menu_lab.config(text=UItext.LABEL['menu_lab1'], fg='#FFEEEE')
        self.menu_sub_btn[0].config(text=UItext.BUTTON['menu_sub1'], command=self.sub_menu_command1)
        self.menu_sub_btn[1].config(text=UItext.BUTTON['menu_sub2'], command=self.sub_menu_command2)
        self.menu_sub_btn[2].config(text=UItext.BUTTON['menu_sub3'], command=self.sub_menu_command3)
        self.menu_sub_btn[3].config(text=UItext.BUTTON['menu_back'], command=self.return_menu_window)
        for i in range(3):
            self.menu_sub_btn[i].place(x=-120, relx=0.5, rely=0.1 * i + 0.55, width=240, height=40)
        i += 1
        self.menu_sub_btn[i].place(x=-50, relx=0.5, rely=0.1 * i + 0.55, width=100, height=40)

    # ------------------------------------------------------------------------
    #  訓練模型之選項
    # ------------------------------------------------------------------------
    def main_menu_command2(self):
        self.menu_btn1.place_forget()
        self.menu_btn2.place_forget()
        self.menu_btn3.place_forget()
        self.background.change_widget_image(self.menu_lab, 'pictures/menu_blue.png')
        self.menu_lab.place(x=-120, relx=0.5, rely=0.4, width=240)
        self.menu_lab.config(text=UItext.LABEL['menu_lab2'], fg='#EEEEFF')
        self.menu_sub_btn[0].config(text=UItext.BUTTON['menu_sub4'], command=self.sub_menu_command4)
        self.menu_sub_btn[1].config(text=UItext.BUTTON['menu_back'], command=self.return_menu_window)
        for i in range(1):
            self.menu_sub_btn[i].place(x=-120, relx=0.5, rely=0.1 * i + 0.6, width=240, height=40)
        i += 1
        self.menu_sub_btn[i].place(x=-50, relx=0.5, rely=0.1 * i + 0.6, width=100, height=40)

    # ------------------------------------------------------------------------
    #  演示路線之選項
    # ------------------------------------------------------------------------
    def main_menu_command3(self):
        self.menu_btn1.place_forget()
        self.menu_btn2.place_forget()
        self.menu_btn3.place_forget()
        self.background.change_widget_image(self.menu_lab, 'pictures/menu_green.png')
        self.menu_lab.place(x=-120, relx=0.5, rely=0.4, width=240)
        self.menu_lab.config(text=UItext.LABEL['menu_lab3'], fg='#EEFFEE')
        self.menu_sub_btn[0].config(text=UItext.BUTTON['menu_sub5'], command=self.sub_menu_command5)
        self.menu_sub_btn[1].config(text=UItext.BUTTON['menu_back'], command=self.return_menu_window)
        for i in range(1):
            self.menu_sub_btn[i].place(x=-120, relx=0.5, rely=0.1 * i + 0.57, width=240, height=40)
        i += 1
        self.menu_sub_btn[i].place(x=-50, relx=0.5, rely=0.1 * i + 0.57, width=100, height=40)

    # ------------------------------------------------------------------------
    #  基礎窗口佈局
    # ------------------------------------------------------------------------
    def base_window_layout(self):
        self.frm.place(x=4, y=8, width=4, height=-101, relwidth=0.6, relheight=1.0)
        self.state_table.place(x=4, y=-96, width=4, rely=1.0, relx=0, relwidth=0.6)
        self.down_btn.place(x=4, y=-38, rely=1.0, relx=0.0, relwidth=0.2)
        self.switch_btn.place(x=6, y=-38, rely=1.0, relx=0.2, relwidth=0.2)
        self.up_btn.place(x=8, y=-38, rely=1.0, relx=0.4, relwidth=0.2)
        self.name_lab.place(x=12, y=18, width=-16, height=14, relx=0.6, relwidth=0.4)
        self.logo_center.place(x=12, y=42, width=-16, relx=0.6, relwidth=0.4)
        self.logo_left.place(x=12, y=42, width=20, relx=0.6)
        self.logo_right.place(x=-24, y=42, width=20, relx=1.0)
        self.lab_tooltip.place(x=12, y=130, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['game_map']
        self.enter_lab1.config(text=UItext.LABEL['game_map'])
        self.enter_lab1.place(x=12, y=156, width=80, height=22, relx=0.6)
        self.enter_comb.config(values=Mota.get_file_name())
        self.enter_comb.place(x=90, y=156, width=-116, relx=0.6, relwidth=0.31)
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)
        self.info_frm.place(x=12, y=214, width=-16, height=-256, relx=0.6, relwidth=0.4, relheight=1.0)
        self.home_btn.place(y=-39, rely=1.0, relx=0.7, relwidth=0.2)

    # ------------------------------------------------------------------------
    #  選項：代理自我學習
    # ------------------------------------------------------------------------
    def sub_menu_command1(self):
        self.hide_menu_window()
        self.base_window_layout()
        self.enter_btn.config(command=lambda: self.create_environment('self_learn'))
        self.add_info(UItext.INFO['tips'], 'tips')
        self.add_info(UItext.INFO['start1'], 'tips')
        self.insert_pc_system_info()

    # ------------------------------------------------------------------------
    #  建立魔塔遊戲環境
    # ------------------------------------------------------------------------
    def create_environment(self, branch='self_learn'):
        env_name = self.enter_comb.get()
        # 例外處理
        if not env_name:
            return
        self.enter_comb.set('')
        self.enter_btn.place_forget()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.home_btn.config(state='disabled')
        self.add_info(UItext.INFO['build_env1'] % env_name, update=True)
        start_time = time.perf_counter()
        count1 = self.mota_env.build_env(env_name)
        self.mota_env.create_map()
        count2 = self.mota_env.create_nodes()
        self.add_info(UItext.INFO['build_env2'] % (time.perf_counter() - start_time), update=True)
        start_time = time.perf_counter()
        self.mota_env.build_anima_frame(bg='#FFF5DD')
        self.add_info(UItext.INFO['build_env3'] % (time.perf_counter() - start_time), update=True)
        self.add_info(UItext.INFO['build_env4'] % self.mota_env.get_layer(), sleep_time=0.1)
        self.add_info(UItext.INFO['build_env5'] % count1)
        self.add_info(UItext.INFO['build_env6'] % count2)
        self.map_lab_tooltip.place(x=120, y=4)
        self.map_lab_tooltip_window.text = UItext.TOOLTIP['animation_map']
        self.update_switch_btn()
        self.line_btn.place(x=12, y=12, relx=0.6)
        # 分支選擇
        if branch == 'self_learn':
            self.create_self_learn_algorithm()
        elif branch == 'manual_learn':
            self.option_btn1.config(text=UItext.BUTTON['manual_start'],
                                    command=self.create_manual_learn)
            self.option_btn1.place(x=12, y=152, width=-16, relx=0.7, relwidth=0.2)
        elif branch == 'model_learn':
            self.create_model_learn_algorithm()
        elif branch == 'model_predict':
            self.create_model_learn_algorithm(is_predict=True)
        elif branch == 'replay':
            self.create_replay_menu()
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  建立自我學習演算法輸入
    # ------------------------------------------------------------------------
    def create_self_learn_algorithm(self):
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['self_algorithm']
        self.enter_lab1.config(text=UItext.LABEL['algorithm'])
        self.enter_lab1.place(x=12, y=142, width=80, height=22, relx=0.6)
        self.enter_comb.config(values=calculation.SELF_ALGORITHM)
        self.enter_comb.place(x=90, y=142, width=-116, relx=0.6, relwidth=0.31)
        self.enter_lab2.config(text=UItext.LABEL['round'])
        self.enter_lab2.place(x=12, y=178, width=80, height=22, relx=0.6)
        self.enter_en.place(x=90, y=178, width=-116, relx=0.6, relwidth=0.31)
        self.enter_btn.config(command=self.self_learn)
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)

    # ------------------------------------------------------------------------
    #  回到選項一開始
    # ------------------------------------------------------------------------
    def back_to_start(self, command):
        self.return_menu_window()
        command()

    # ------------------------------------------------------------------------
    #  重新選擇自我學習演算法
    # ------------------------------------------------------------------------
    def reselect_self_learn_algorithm(self):
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        self.home_btn.config(state='disabled')
        self.create_self_learn_algorithm()
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  設定動畫每一幀間隔時間
    # ------------------------------------------------------------------------
    def set_interval_time(self, value):
        value = int(value)
        if value == int(self.speed_scale['from']):
            self.cal.fast()
            self.update_switch_btn()
        elif value == int(self.speed_scale['to']):
            self.cal.pause()
            self.update_switch_btn()
        else:
            self.cal.resume()
            self.cal.interval_time = value * 0.001
            self.update_switch_btn(disable=True)

    # ------------------------------------------------------------------------
    #  計時器
    # ------------------------------------------------------------------------
    def time_count(self):
        t = time.perf_counter() - self.cal.start_time
        s = t % 60
        m = int(t) // 60 % 60
        h = int(t) // 3600
        self.info_text.config(state='normal')
        self.info_text.delete('end-5l', 'end-1l')
        if not self.cal.show_frame:
            self.add_info(UItext.INFO['speed_scale1'], 'obvious')
        elif self.cal.pause_flag:
            self.add_info(UItext.INFO['speed_scale2'], 'obvious')
        else:
            self.add_info('\n')
        self.add_info(UItext.INFO['time1'] % self.cal.now_round)
        self.add_info(UItext.INFO['time2'] % (h, m, s))
        self.add_info(UItext.INFO['time3'] % self.cal.highest_score, update=True)

    # ------------------------------------------------------------------------
    #  代理自我學習
    # ------------------------------------------------------------------------
    def self_learn(self):
        algorithm_name = self.enter_comb.get()
        rounds = self.enter_en.get()
        # 例外處理
        if not algorithm_name or not rounds:
            return
        try:
            rounds = int(rounds)
        except ValueError:
            self.add_info(UItext.INFO['warning1'], 'tips', update=True)
            return
        if rounds <= 0:
            self.add_info(UItext.INFO['warning2'], 'tips', update=True)
            return
        self.enter_btn.place_forget()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.enter_lab2.place_forget()
        self.enter_en.place_forget()
        self.home_btn.config(state='disabled')
        self.speed_scale.config(command=self.set_interval_time)
        self.set_interval_time(self.speed_scale.get())  # 切換按鈕也一同更新
        self.add_info(UItext.INFO['train1'] % algorithm_name)
        self.add_info(UItext.INFO['train2'] % rounds, update=True)
        self.add_info('\n', sleep_time=0.1, update=True)
        self.add_info(UItext.INFO['train3'], sleep_time=0.01, update=True)
        self.add_info('\n', sleep_time=0.01, update=True)
        self.add_info('\n', sleep_time=0.01, update=True)
        time.sleep(0.2)
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['speed_scale']
        self.fast_lab.place(x=-20, y=166, relx=0.65)
        self.pause_lab.place(x=4, y=166, relx=0.85)
        self.speed_scale.place(y=126, relx=0.65, relwidth=0.2)
        self.stop_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)
        self.cal.set_parameters(self.mota_env, algorithm_name, rounds,
                                refresh_function=self.time_count)
        # 訓練開始前刷新一次
        self.training_result_refresh(refresh_btn=True)
        self.cal.run()
        # 訓練結束後
        self.update_switch_btn()
        self.time_count()
        if self.cal.best_success_path:
            self.save_path_data(self.enter_comb.get(),
                                self.cal.best_success_path, self.cal.highest_score)
        else:
            self.add_info(UItext.INFO['end1'], update=True)
        self.training_result_refresh(refresh_btn=False)
        self.add_info(UItext.INFO['end2'], sleep_time=0.1, update=True)
        self.lab_tooltip.place_forget()
        self.fast_lab.place_forget()
        self.pause_lab.place_forget()
        self.speed_scale.place_forget()
        self.stop_btn.place_forget()
        self.option_btn1.config(text=UItext.BUTTON['restart1'],
                                command=lambda: self.back_to_start(self.sub_menu_command1))
        self.option_btn1.place(x=12, y=132, width=-16, relx=0.65, relwidth=0.3)
        self.option_btn2.config(text=UItext.BUTTON['restart2'],
                                command=self.reselect_self_learn_algorithm)
        self.option_btn2.place(x=12, y=172, width=-16, relx=0.65, relwidth=0.3)
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  顯示上一樓層
    # ------------------------------------------------------------------------
    def floor_up(self):
        self.anima_frm.up_floor()
        if self.nb.winfo_viewable():
            self.attribute_refresh()
        self.update_switch_btn()

    # ------------------------------------------------------------------------
    #  顯示下一樓層
    # ------------------------------------------------------------------------
    def floor_down(self):
        self.anima_frm.down_floor()
        if self.nb.winfo_viewable():
            self.attribute_refresh()
        self.update_switch_btn()

    # ------------------------------------------------------------------------
    #  切換選項卡窗口
    # ------------------------------------------------------------------------
    def switch_nb_window(self):
        if self.nb.winfo_viewable():
            self.hide_nb_window()
        else:
            self.attribute_refresh()
            self.show_nb_window()
            self.nb.update()  # 此目的為了讓winfo_viewable()更新，以觸發update_switch_btn()的條件
        self.update_switch_btn()

    # ------------------------------------------------------------------------
    #  顯示選項卡窗口
    # ------------------------------------------------------------------------
    def show_nb_window(self):
        self.nb.place(x=4, y=8, width=4, height=-101, relwidth=0.6, relheight=1.0)
        self.map_lab_tooltip.place_forget()

    # ------------------------------------------------------------------------
    #  隱藏選項卡窗口
    # ------------------------------------------------------------------------
    def hide_nb_window(self):
        self.nb.place_forget()
        self.map_lab_tooltip.place(x=120, y=4)

    # ------------------------------------------------------------------------
    #  更新切換按鈕名稱
    # ------------------------------------------------------------------------
    def update_switch_btn(self, disable=False):
        if disable:
            # 避免set_interval_time()連續運行多次
            if str(self.switch_btn['state']) == 'normal':
                self.up_btn.config(text=UItext.BUTTON['up'], state='disabled')
                self.down_btn.config(text=UItext.BUTTON['down'], state='disabled')
                self.switch_btn.config(text=UItext.BUTTON['attribute_disable'], state='disabled')
                self.hide_nb_window()
        else:
            now_floor = self.anima_frm.now_floor
            if self.anima_frm.check_up_floor():
                # 讓按鈕光標能夠保持啟用顏色
                if str(self.up_btn['state']) != 'normal':
                    self.up_btn.config(text=UItext.BUTTON['up'], state='normal')
            else:
                self.up_btn.config(text=UItext.BUTTON['up'], state='disabled')
            if self.anima_frm.check_down_floor():
                # 讓按鈕光標能夠保持啟用顏色
                if str(self.down_btn['state']) != 'normal':
                    self.down_btn.config(text=UItext.BUTTON['down'], state='normal')
            else:
                self.down_btn.config(text=UItext.BUTTON['down'], state='disabled')
            if self.nb.winfo_viewable():
                self.switch_btn.config(text=UItext.BUTTON['map'] % now_floor, state='normal')
            else:
                self.switch_btn.config(text=UItext.BUTTON['attribute'] % now_floor, state='normal')

    # ------------------------------------------------------------------------
    #  改變節點連線狀態
    # ------------------------------------------------------------------------
    def change_line_state(self):
        if self.anima_frm.line_visible:
            self.mota_env.anima_line_visible(False)
            self.line_btn.config(image=self.line_invisible_img)
        else:
            self.mota_env.anima_line_visible(True)
            self.line_btn.config(image=self.line_visible_img)
        self.mota_env.update_frame()

    # ------------------------------------------------------------------------
    #  樓層資訊刷新
    # ------------------------------------------------------------------------
    def attribute_refresh(self):
        def create_from():
            af = AdvancedForm(self.tab1.contents, columns, widths, data, bg=bg, bd=4)
            af.treeview.config(style='attribute.Treeview')
            af.pack(anchor='w')

        # 清除內容
        self.tab1.clear()
        # self.tab1.update()  # 這一行是為了解決刷新畫面時會出現閃過的白色矩形
        # 基本資料
        floor = self.anima_frm.now_floor
        font1 = UItext.FONT['attribute_title']
        font2 = UItext.FONT['attribute_null']
        bg = 'lavender'
        # 工具提示
        frame = tk.Frame(self.tab1.contents, bg=bg)
        lab = tk.Label(frame, image=self.map_lab_tooltip_img, bg=bg, bd=0)
        Tooltip(lab, text=UItext.TOOLTIP['floor_information'], wait_time=100)
        lab.pack(side='left')
        # 文字資訊
        text = UItext.LABEL['floor_info1'] % floor
        tk.Label(frame, text=text, font=font1, bg=bg).pack(side='right', padx=2)
        frame.pack(anchor='w')
        text = UItext.LABEL['floor_info2'] % len(self.mota_env.get_floor_pos(floor))
        tk.Label(self.tab1.contents, text=text, font=font1, bg=bg).pack(anchor='w', padx=5)
        # # 繪製表格
        font_color = 'DarkSlateBlue'
        data = self.mota_env.get_floor_data(floor, 'enemies')  # 怪物
        tk.Label(self.tab1.contents, text=UItext.LABEL['enemies'],
                 font=font1, bg=bg, fg=font_color).pack(anchor='w', padx=5)
        if data:
            columns = UItext.TABLE['enemies_columns']
            widths = UItext.TABLE['enemies_widths']
            create_from()
        else:
            tk.Label(self.tab1.contents, text=UItext.LABEL['no_data'],
                     font=font2, bg=bg).pack(anchor='w', padx=20, pady=5)
        data = self.mota_env.get_floor_data(floor, 'items')  # 道具
        tk.Label(self.tab1.contents, text=UItext.LABEL['items'],
                 font=font1, bg=bg, fg=font_color).pack(anchor='w', padx=5)
        if data:
            columns = UItext.TABLE['items_columns']
            widths = UItext.TABLE['items_widths']
            create_from()
        else:
            tk.Label(self.tab1.contents, text=UItext.LABEL['no_data'],
                     font=font2, bg=bg).pack(anchor='w', padx=20, pady=5)
        data = self.mota_env.get_floor_data(floor, 'npcs')  # 角色
        if data:
            tk.Label(self.tab1.contents, text=UItext.LABEL['npcs'],
                     font=font1, bg=bg, fg=font_color).pack(anchor='w', padx=5)
            columns = UItext.TABLE['npcs_columns']
            widths = UItext.TABLE['npcs_widths']
            create_from()
        data = self.mota_env.get_floor_data(floor, 'afterEvent')  # 事件後
        if data:
            tk.Label(self.tab1.contents, text=UItext.LABEL['afterEvent'],
                     font=font1, bg=bg, fg=font_color).pack(anchor='w', padx=5)
            columns = UItext.TABLE['afterEvent_columns']
            widths = UItext.TABLE['afterEvent_widths']
            create_from()
        self.tab1.update()

    # ------------------------------------------------------------------------
    #  訓練結果刷新
    # ------------------------------------------------------------------------
    def training_result_refresh(self, refresh_btn=True):
        def print_info():
            file_name = self.save_result_chart(fig)
            lab.config(text=UItext.LABEL['print_chart'] % file_name)
            btn.config(style='switch.TButton', state='disabled')

        # 清除內容
        self.tab2.clear()
        # 基本資料
        bg = 'lightyellow'
        font = UItext.FONT['result_label']
        t = time.perf_counter() - self.cal.start_time
        now_round = self.cal.now_round
        highest_score = self.cal.highest_score
        data = self.cal.get_train_data()
        # 工具提示
        frame = tk.Frame(self.tab2.contents, bg=bg)
        lab = tk.Label(frame, image=self.map_lab_tooltip_img, bg=bg, bd=0)
        Tooltip(lab, text=UItext.TOOLTIP['training_result'], wait_time=100)
        lab.pack(side='left')
        # 文字資訊
        text = UItext.LABEL['training_result1'] % (int(t) // 3600, int(t) // 60 % 60, t % 60)
        tk.Label(frame, text=text, font=font, bg=bg).pack(side='right', padx=2)
        if refresh_btn:
            tk.Label(frame, text=UItext.LABEL['training_result2'],
                     font=font, fg='red', bg=bg).pack(side='right', padx=2)
        else:
            tk.Label(frame, text=UItext.LABEL['training_result3'],
                     font=font, fg='purple', bg=bg).pack(side='right', padx=6)
        frame.pack(anchor='w')
        frame = tk.Frame(self.tab2.contents, bg=bg)
        text = UItext.LABEL['training_result4'] % now_round
        tk.Label(frame, text=text, font=font, bg=bg).pack(side='left', padx=5)
        text = UItext.LABEL['training_result5'] % highest_score
        tk.Label(frame, text=text, font=font, bg=bg).pack(side='right', padx=20)
        frame.pack(fill='x')
        # 折線圖
        fig = results_plot.get_figure(data, color='steelblue', facecolor=bg, figsize=(7.5, 5), dpi=64)
        canvas = FigureCanvasTkAgg(fig, self.tab2.contents)
        canvas.get_tk_widget().pack()
        # 按鈕
        frame = tk.Frame(self.tab2.contents, bg=bg)
        if refresh_btn:
            ttk.Button(frame, text=UItext.BUTTON['refresh'], command=self.training_result_refresh,
                       width=16, style='yellow.TButton').pack(side='left', padx=20)
        else:
            ttk.Button(frame, text=UItext.BUTTON['refresh'], state='disabled',
                       width=16, style='switch.TButton').pack(side='left', padx=20)
        btn = ttk.Button(frame, text=UItext.BUTTON['print'], width=14, command=print_info,
                         style='yellow.TButton')
        btn.pack(side='right', padx=20)
        frame.pack()
        # 提示訊息
        lab = tk.Label(self.tab2.contents, font=UItext.FONT['chart_print_info'], fg='red', bg=bg)
        lab.pack(pady=8)
        self.tab2.update()

    # ------------------------------------------------------------------------
    #  儲存通關路線檔
    # ------------------------------------------------------------------------
    def save_path_data(self, algorithm_name, path, score):
        data = self.mota_env.convert_action_index(path)
        env_name = self.mota_env.env_name
        dir_path = f'path/{env_name}/{algorithm_name}'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 建立檔案名稱
        pattern = re.compile('(\d+)')
        i = 0
        for file_name in os.listdir(dir_path):
            match = re.match(pattern, file_name)
            if match is not None:
                num = int(re.match(pattern, file_name).group(1))
                if i < num:
                    i = num
        file_name = '{:s}/{:03d}_{:d}.npy'.format(dir_path, i + 1, score)
        np.save(file_name, data)
        self.add_info(UItext.INFO['end3'] % file_name, 'tips', update=True)

    # ------------------------------------------------------------------------
    #  儲存訓練結果折線圖
    # ------------------------------------------------------------------------
    def save_result_chart(self, figure):
        dir_path = 'output'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        now_time = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        file_name = f'{dir_path}/chart_{now_time}.png'
        figure.savefig(file_name, dpi=300)
        return file_name

    # ------------------------------------------------------------------------
    #  選項：手動輸入路線
    # ------------------------------------------------------------------------
    def sub_menu_command2(self):
        self.hide_menu_window()
        self.base_window_layout()
        self.enter_btn.config(command=lambda: self.create_environment('manual_learn'))
        self.add_info(UItext.INFO['tips'], 'tips')
        self.add_info(UItext.INFO['start2'], 'tips')

    # ------------------------------------------------------------------------
    #  建立手動輸入行動操作面板
    # ------------------------------------------------------------------------
    def create_manual_learn(self):
        self.option_btn1.place_forget()
        self.add_info(UItext.INFO['start3'], 'tips', clear=True)
        self.info_frm.place(y=0, height=-42, rely=0.83, relheight=0.17)  # 更新
        self.lab_tooltip.place(x=12, y=124, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['action_index']
        self.enter_lab1.config(text=UItext.LABEL['action_index'])
        self.enter_lab1.place(x=24, y=142, width=-50, height=22, relx=0.7, relwidth=0.2)
        self.enter_en.config(justify='center')
        self.enter_en.place(x=24, y=168, width=-44, relx=0.7, relwidth=0.2)
        self.back_btn.config(command=self.back_action)
        self.back_btn.place(x=16, y=148, width=0, relx=0.6, relwidth=0.09)
        self.enter_btn.config(command=self.enter_action)
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)
        self.enter_lab2.config(text=UItext.LABEL['action_list'])
        self.enter_lab2.place(x=24, y=200, width=-50, height=22, relx=0.7, relwidth=0.2)
        self.actions_form.place(x=12, y=224, width=-16, height=-224, relx=0.6, relwidth=0.4, relheight=0.83)
        self.actions_form_refresh()

    # ------------------------------------------------------------------------
    #  手動輸入行動結束
    # ------------------------------------------------------------------------
    def manual_learn_finish(self):
        self.info_frm.place(y=214, height=-256, rely=0, relheight=1.0)  # 更新
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_en.place_forget()
        self.back_btn.place_forget()
        self.enter_btn.place_forget()
        self.enter_lab2.place_forget()
        self.actions_form.place_forget()
        self.option_btn1.config(text=UItext.BUTTON['restart1'],
                                command=lambda: self.back_to_start(self.sub_menu_command2))
        self.option_btn1.place(x=12, y=152, width=-16, relx=0.65, relwidth=0.3)

    # ------------------------------------------------------------------------
    #  行動列表刷新
    # ------------------------------------------------------------------------
    def actions_form_refresh(self):
        self.actions_form.clear()
        self.action_list = self.mota_env.get_feasible_actions()
        data = []
        for index, action in enumerate(self.action_list, 1):
            data.append([index, str(self.mota_env.n2p[action]), action.class_, action.id])
        self.actions_form.insert(data)
        self.actions_form.update()

    # ------------------------------------------------------------------------
    #  行動列表點擊處理
    # ------------------------------------------------------------------------
    def actions_form_click_on(self, event):
        tree = self.actions_form.treeview
        data = tree.selection()
        if data:
            col = tree.item(tree.selection()[0], 'values')
            self.set_action_index(int(col[0]))

    # ------------------------------------------------------------------------
    #  設置行動索引值，並更新光標位置
    #  index_p: 被加過1的index
    # ------------------------------------------------------------------------
    def set_action_index(self, index_p):
        self.enter_en.delete(0, 'end')
        self.enter_en.insert(0, index_p)
        if self.action_list:
            action = self.action_list[index_p - 1]
            pos = self.mota_env.n2p[action]
            self.anima_frm.show_cursor(pos)
        self.update_switch_btn()
        if self.nb.winfo_viewable():
            self.attribute_refresh()

    # ------------------------------------------------------------------------
    #  退回行動
    # ------------------------------------------------------------------------
    def back_action(self):
        count = self.mota_env.get_step_count()
        if count >= 1:
            self.mota_env.back_step(1, refresh_frame=True)
            self.actions_form_refresh()
            self.set_action_index(1)  # 設置輸入框初始值
        if count > 1:
            self.add_info(UItext.INFO['step1'] % self.mota_env.get_step_count(), clear=True)
        else:
            self.add_info(UItext.INFO['step2'], clear=True)
        self.enter_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  輸入行動
    # ------------------------------------------------------------------------
    def enter_action(self):
        index = self.enter_en.get()
        # 例外處理
        if not index:
            return
        try:
            index = int(index)
            if index < 1:
                raise
            action = self.action_list[index - 1]
        except:
            self.add_info(UItext.INFO['warning3'], 'tips', clear=True)
            return
        ending = self.mota_env.step(action, refresh_frame=True)
        if ending == 'clear':
            self.add_info('', clear=True)
            score = self.mota_env.player.hp
            path = self.mota_env.observation.copy()
            self.mota_env.reset()
            self.save_path_data('manual', path, score)
            self.add_info(UItext.INFO['end4'] % score)
            self.manual_learn_finish()
        else:
            self.actions_form_refresh()
            self.set_action_index(1)  # 設置輸入框初始值
            if self.action_list:
                self.add_info(UItext.INFO['step1'] % self.mota_env.get_step_count(), clear=True)
            else:
                self.add_info(UItext.INFO['step3'], clear=True)
                self.enter_btn.config(state='disabled')

    # ------------------------------------------------------------------------
    #  選項：以模型產生路線
    # ------------------------------------------------------------------------
    def sub_menu_command3(self):
        def choose_environment(text, type_name):
            self.option_btn1.place_forget()
            self.option_btn2.place_forget()
            self.base_window_layout()
            self.add_info(UItext.INFO['use_model'] % text, 'tips', clear=True)
            self.insert_pc_system_info()
            self.enter_btn.config(command=lambda: self.create_environment(type_name))

        self.hide_menu_window()
        self.base_window_layout()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.enter_btn.place_forget()
        text = UItext.BUTTON['model_learn']
        self.option_btn1.config(text=text, command=lambda: choose_environment(text, 'model_learn'))
        self.option_btn1.place(x=12, y=132, width=-16, relx=0.65, relwidth=0.3)
        text2 = UItext.BUTTON['model_predict']
        self.option_btn2.config(text=text2, command=lambda: choose_environment(text2, 'model_predict'))
        self.option_btn2.place(x=12, y=172, width=-16, relx=0.65, relwidth=0.3)
        self.add_info(UItext.INFO['tips'], 'tips')
        self.add_info(UItext.INFO['start4'], 'tips')
        self.add_info(UItext.INFO['model_info'], 'tips')

    # ------------------------------------------------------------------------
    #  建立模型學習演算法輸入
    #  is_predict:  是否為一般模型預測
    # ------------------------------------------------------------------------
    def create_model_learn_algorithm(self, is_predict=False):
        if not is_predict:
            self.lab_tooltip.place(x=12, y=120, relx=0.6)
            self.lab_tooltip_window.text = UItext.TOOLTIP['model_learn']
            self.enter_comb.config(values=calculation.MODEL_ALGORITHM)
        else:
            self.lab_tooltip_window.text = UItext.TOOLTIP['model_predict']
            self.enter_comb.config(values=calculation.MODEL_PREDICT)
            self.enter_comb.current(0)
            self.enter_comb.config(state='disabled')
            self.enter_en.insert(0, 1)
            self.enter_en.config(state='disabled')
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.enter_lab3.config(text=UItext.LABEL['model'])
        self.enter_lab3.place(x=12, y=136, width=80, height=22, relx=0.6)
        self.enter_comb2.config(values=self.get_model_name())
        self.enter_comb2.place(x=90, y=136, width=-116, relx=0.6, relwidth=0.31)
        self.enter_lab1.config(text=UItext.LABEL['algorithm'])
        self.enter_lab1.place(x=12, y=160, width=80, height=22, relx=0.6)
        self.enter_comb.place(x=90, y=160, width=-116, relx=0.6, relwidth=0.31)
        self.enter_lab2.config(text=UItext.LABEL['round'])
        self.enter_lab2.place(x=12, y=184, width=80, height=22, relx=0.6)
        self.enter_en.place(x=90, y=184, width=-116, relx=0.6, relwidth=0.31)
        self.enter_btn.config(command=lambda: self.model_learn(is_predict))
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)

    # ------------------------------------------------------------------------
    #  重新選擇模型學習演算法
    # ------------------------------------------------------------------------
    def reselect_model_learn_algorithm(self, is_predict=False):
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        self.home_btn.config(state='disabled')
        self.create_model_learn_algorithm(is_predict)
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  選項：以模型產生路線
    # ------------------------------------------------------------------------
    def model_learn(self, is_predict=False):
        model_name = self.enter_comb2.get()
        algorithm_name = self.enter_comb.get()
        rounds = self.enter_en.get()
        # 例外處理
        if not model_name or not algorithm_name or not rounds:
            return
        try:
            rounds = int(rounds)
        except ValueError:
            self.add_info(UItext.INFO['warning1'], 'tips', update=True)
            return
        if rounds <= 0:
            self.add_info(UItext.INFO['warning2'], 'tips', update=True)
            return
        self.enter_btn.place_forget()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.enter_lab2.place_forget()
        self.enter_en.place_forget()
        self.enter_lab3.place_forget()
        self.enter_comb2.place_forget()
        self.home_btn.config(state='disabled')
        self.set_interval_time(self.speed_scale.get())  # 切換按鈕也一同更新
        self.add_info(UItext.INFO['train1'] % algorithm_name)
        self.add_info(UItext.INFO['train2'] % rounds, update=True)
        self.add_info('\n', sleep_time=0.1, update=True)
        self.add_info(UItext.INFO['train3'], sleep_time=0.01, update=True)
        self.add_info('\n', sleep_time=0.01, update=True)
        self.add_info('\n', sleep_time=0.01, update=True)
        time.sleep(0.2)
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['speed_scale']
        self.fast_lab.place(x=-20, y=166, relx=0.65)
        self.pause_lab.place(x=4, y=166, relx=0.85)
        self.speed_scale.place(y=126, relx=0.65, relwidth=0.2)
        self.stop_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)
        model_path = f'model/{model_name}'
        self.cal.set_parameters(self.mota_env, algorithm_name, rounds,
                                model_path=model_path, refresh_function=self.time_count)
        # 訓練開始前刷新一次
        self.training_result_refresh(refresh_btn=True)
        self.cal.run()
        # 訓練結束後
        self.update_switch_btn()
        self.time_count()
        if self.cal.best_success_path:
            self.save_path_data(self.enter_comb.get(),
                                self.cal.best_success_path, self.cal.highest_score)
        else:
            self.add_info(UItext.INFO['end1'], update=True)
        self.training_result_refresh(refresh_btn=False)
        self.add_info(UItext.INFO['end2'], sleep_time=0.1, update=True)
        self.lab_tooltip.place_forget()
        self.fast_lab.place_forget()
        self.pause_lab.place_forget()
        self.speed_scale.place_forget()
        self.stop_btn.place_forget()
        self.option_btn1.config(text=UItext.BUTTON['restart3'],
                                command=lambda: self.back_to_start(self.sub_menu_command3))
        self.option_btn1.place(x=12, y=132, width=-16, relx=0.65, relwidth=0.3)
        self.option_btn2.config(text=UItext.BUTTON['restart4'],
                                command=lambda: self.reselect_model_learn_algorithm(is_predict))
        self.option_btn2.place(x=12, y=172, width=-16, relx=0.65, relwidth=0.3)
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  獲取模型名稱
    # ------------------------------------------------------------------------
    def get_model_name(self):
        dir_path = 'model'
        if os.path.exists(dir_path):
            model_list = []
            pattern = re.compile('((?!_config).)*$')
            for file_name in os.listdir(dir_path):
                match = re.match(pattern, file_name)
                if match is not None:
                    model_list.append(file_name)
            return model_list
        else:
            return []

    # ------------------------------------------------------------------------
    #  選項：使用通關路線訓練
    # ------------------------------------------------------------------------
    def sub_menu_command4(self):
        self.hide_menu_window()
        self.base_window_layout()
        self.enter_comb.place_forget()
        self.enter_btn.place_forget()
        # 清除資料庫選擇的內容
        self.dataset_comb1.set('')
        self.dataset_comb2.set('')
        self.dataset_form1.clear()
        self.dataset_form2.clear()
        self.file_name_dict.clear()
        dir_path = 'path'
        if os.path.exists(dir_path):
            self.dataset_comb1.config(values=os.listdir(dir_path))
        else:
            self.dataset_comb1.config(values=[])
        self.dataset_frm.place(x=4, y=8, width=4, height=-101, relwidth=0.6, relheight=1.0)
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['train_model']
        self.enter_lab1.config(text=UItext.LABEL['train_model'])
        self.update_model_option_btn()
        self.enter_lab1.place(x=24, y=122, width=-40, height=22, relx=0.7, relwidth=0.2)
        self.option_btn1.config(text=UItext.BUTTON['specialization'],
                                command=lambda: self.create_model_train_architecture(True))
        self.option_btn1.place(x=12, y=148, width=-16, relx=0.65, relwidth=0.3)
        self.option_btn2.config(text=UItext.BUTTON['generalization'],
                                command=lambda: self.create_model_train_architecture(False))
        self.option_btn2.place(x=12, y=182, width=-16, relx=0.65, relwidth=0.3)
        self.add_info(UItext.INFO['tips'], 'tips')
        self.add_info(UItext.INFO['start5'], 'tips')
        self.add_info(UItext.INFO['train_model_info'], 'tips')

    # ------------------------------------------------------------------------
    #  建立訓練模型架構輸入
    # ------------------------------------------------------------------------
    def create_model_train_architecture(self, specialization=True):
        self.dataset_frm.place_forget()
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        length = sum([len(s) for s in self.file_name_dict.values()])
        self.add_info(UItext.INFO['train4'] % length)
        self.lab_tooltip.place(x=12, y=130, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['model_architecture']
        self.enter_lab1.config(text=UItext.LABEL['model_architecture'])
        self.enter_lab1.place(x=12, y=156, width=80, height=22, relx=0.6, relwidth=0)
        self.enter_comb.config(values=MotaModel.MODEL_TYPE)
        self.enter_comb.place(x=90, y=156, width=-116, relx=0.6, relwidth=0.31)
        self.enter_btn.config(command=lambda: self.model_train(specialization))
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)

    # ------------------------------------------------------------------------
    #  重新選擇訓練模型架構
    # ------------------------------------------------------------------------
    def reselect_model_architecture(self, specialization=True):
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        self.home_btn.config(state='disabled')
        self.create_model_train_architecture(specialization)
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  模型訓練
    # ------------------------------------------------------------------------
    def model_train(self, specialization=True):
        def thread_task():
            model.train(model_type)
            self.processing = False

        model_type = self.enter_comb.get()
        # 例外處理
        if not model_type:
            return
        self.enter_btn.place_forget()
        self.lab_tooltip.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.home_btn.config(state='disabled')
        self.add_info(UItext.INFO['train5'] % model_type, update=True)
        model = MotaModel()
        self.add_info(UItext.INFO['train6'], sleep_time=0.1, update=True)
        self.add_info('\n')
        # 建立訓練集
        count = 0
        length = sum([len(s) for s in self.file_name_dict.values()])
        start_time = time.perf_counter()
        for env_name, paths in self.file_name_dict.items():
            for file_name in paths:
                self.info_text.config(state='normal')
                self.info_text.delete('end-2l', 'end-1l')
                self.add_info(UItext.INFO['train7'] % (count, length), update=True)
                data = np.load(f'path/{env_name}/{file_name}')
                model.create_dataset(env_name, data)
                count += 1
        self.info_text.config(state='normal')
        self.info_text.delete('end-2l', 'end-1l')
        self.add_info(UItext.INFO['train7'] % (count, length), update=True)
        # 資料預處理
        model.preprocess()
        self.info_text.config(state='normal')
        self.info_text.delete('end-3l', 'end-1l')
        self.add_info(UItext.INFO['create_model1'] % (time.perf_counter() - start_time), update=True)
        self.add_info(UItext.INFO['create_model2'] % len(model.df.index))
        # 訓練模型
        self.add_info(UItext.INFO['train8'], sleep_time=0.1, update=True)
        self.add_info('\n')
        self.processing = True
        t = threading.Thread(target=thread_task)
        start_time = time.perf_counter()
        t.start()
        while self.processing:
            time.sleep(0.02)
            self.info_text.config(state='normal')
            self.info_text.delete('end-2l', 'end-1l')
            self.add_info(UItext.INFO['train_model_time'] % (time.perf_counter() - start_time), update=True)
        self.info_text.config(state='normal')
        self.info_text.delete('end-3l', 'end-1l')
        self.add_info(UItext.INFO['create_model3'] % (time.perf_counter() - start_time), update=True)
        self.add_info(UItext.INFO['create_model4'] % (model.train_accuracy * 100))
        # 模型儲存
        dir_path = 'model'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        pattern = re.compile('(\d+)')
        i = 0
        for file_name in os.listdir(dir_path):
            match = re.match(pattern, file_name)
            if match is not None:
                num = int(re.match(pattern, file_name).group(1))
                if i < num:
                    i = num
        ch = 's' if specialization else 'g'
        model_name = 'None'
        if len(self.file_name_dict) == 1:
            for n in self.file_name_dict:
                model_name = n
        else:
            model_name = 'merge'
        file_name = 'model/{:03d}{:s}_{:s}.pkl'.format(i + 1, ch, model_name)
        model.save_model(file_name)
        self.add_info(UItext.INFO['end5'] % file_name, 'tips', update=True)
        self.add_info(UItext.INFO['end6'], update=True)
        self.option_btn1.config(state='enabled')
        self.option_btn1.config(text=UItext.BUTTON['restart5'],
                                command=lambda: self.back_to_start(self.sub_menu_command4))
        self.option_btn1.place(x=12, y=132, width=-16, relx=0.65, relwidth=0.3)
        self.option_btn2.config(text=UItext.BUTTON['restart6'],
                                command=lambda: self.reselect_model_architecture(specialization))
        self.option_btn2.place(x=12, y=172, width=-16, relx=0.65, relwidth=0.3)
        self.home_btn.config(state='normal')

    # ------------------------------------------------------------------------
    #  環境下拉式選單選擇後處理
    # ------------------------------------------------------------------------
    def environment_callback(self, event):
        self.dataset_comb2.set('')
        self.dataset_form1.clear()
        env_name = self.dataset_comb1.get()
        dir_path = f'path/{env_name}'
        self.dataset_comb2.config(values=os.listdir(dir_path))
        self.dataset_form1.update()

    # ------------------------------------------------------------------------
    #  演算法下拉式選單選擇後處理
    # ------------------------------------------------------------------------
    def algorithm_callback(self, event):
        self.dataset_form1.clear()
        env_name = self.dataset_comb1.get()
        alg_name = self.dataset_comb2.get()
        dir_path = f'path/{env_name}/{alg_name}'
        data = [[s] for s in os.listdir(dir_path)]
        self.dataset_form1.insert(data)
        self.dataset_form1.update()

    # ------------------------------------------------------------------------
    #  資料集新增
    # ------------------------------------------------------------------------
    def dataset_insert(self, event):
        tree = self.dataset_form1.treeview
        data = []
        env_name = self.dataset_comb1.get()
        alg_name = self.dataset_comb2.get()
        for item in tree.selection():
            file_name = tree.item(item, 'values')[0]
            path = f'{alg_name}/{file_name}'
            if env_name not in self.file_name_dict:
                self.file_name_dict[env_name] = set()
            if path not in self.file_name_dict[env_name]:
                data.append([env_name, alg_name, file_name])
                self.file_name_dict[env_name].add(path)
        self.dataset_form2.insert(data)
        self.update_model_option_btn()

    # ------------------------------------------------------------------------
    #  資料集刪除
    # ------------------------------------------------------------------------
    def dataset_delete(self, event):
        tree = self.dataset_form2.treeview
        items = tree.selection()
        for item in items:
            env_name, alg_name, file_name = tree.item(item, 'values')
            path = f'{alg_name}/{file_name}'
            self.file_name_dict[env_name].remove(path)
            if not self.file_name_dict[env_name]:
                self.file_name_dict.pop(env_name)
        self.dataset_form2.delete(items)
        self.update_model_option_btn()

    # ------------------------------------------------------------------------
    #  更新模型訓練方向按扭
    # ------------------------------------------------------------------------
    def update_model_option_btn(self):
        if self.file_name_dict:
            if len(self.file_name_dict) == 1:
                self.option_btn1.config(state='enabled')
            else:
                self.option_btn1.config(state='disabled')
            self.option_btn2.config(state='enabled')
        else:
            self.option_btn1.config(state='disabled')
            self.option_btn2.config(state='disabled')

    # ------------------------------------------------------------------------
    #  選項：使用現有資料庫
    # ------------------------------------------------------------------------
    def sub_menu_command5(self):
        self.hide_menu_window()
        self.base_window_layout()
        self.enter_btn.config(command=lambda: self.create_environment('replay'))
        self.add_info(UItext.INFO['tips'], 'tips')
        self.add_info(UItext.INFO['start6'], 'tips')

    # ------------------------------------------------------------------------
    #  建立通關路線回放選單輸入
    # ------------------------------------------------------------------------
    def create_replay_menu(self):
        self.lab_tooltip.place(x=12, y=120, relx=0.6)
        self.lab_tooltip_window.text = UItext.TOOLTIP['replay']
        self.enter_lab1.config(text=UItext.LABEL['replay_algorithm'])
        self.enter_lab1.place(x=12, y=142, width=80, height=22, relx=0.6)
        dir_path = f'path/{self.mota_env.env_name}'
        if os.path.exists(dir_path):
            self.enter_comb.config(values=os.listdir(dir_path))
        else:
            self.enter_comb.config(values=[])
        self.enter_comb.bind('<<ComboboxSelected>>', self.set_replay_combobox)
        self.enter_comb.place(x=90, y=142, width=-116, relx=0.6, relwidth=0.31)
        self.enter_lab2.config(text=UItext.LABEL['clear_path'])
        self.enter_lab2.place(x=12, y=178, width=80, height=22, relx=0.6)
        self.enter_comb2.config(values=[])
        self.enter_comb2.place(x=90, y=178, width=-116, relx=0.6, relwidth=0.31)
        self.enter_btn.config(command=self.replay)
        self.enter_btn.place(x=-12, y=148, width=0, relx=0.91, relwidth=0.09)

    # ------------------------------------------------------------------------
    #  重新選擇通關路線回放選單
    # ------------------------------------------------------------------------
    def reselect_replay_menu(self):
        self.option_btn1.place_forget()
        self.option_btn2.place_forget()
        self.mota_env.reset(refresh_frame=True)
        self.create_replay_menu()

    # ------------------------------------------------------------------------
    #  通關路線回放
    # ------------------------------------------------------------------------
    def replay(self):
        algorithm_name = self.enter_comb.get()
        file_name = self.enter_comb2.get()
        # 例外處理
        if not algorithm_name or not file_name:
            return
        self.enter_btn.place_forget()
        self.enter_lab1.place_forget()
        self.enter_comb.place_forget()
        self.enter_lab2.place_forget()
        self.enter_comb2.place_forget()
        self.lab_tooltip_window.text = UItext.TOOLTIP['replay_scale']
        self.play_btn.config(command=self.replay_enter_action)
        self.play_btn.place(x=-12, y=127, width=0, relx=0.9, relwidth=0.09)
        self.back_btn.config(command=self.replay_back_action)
        self.back_btn.place(x=-12, y=169, width=0, relx=0.9, relwidth=0.09)
        self.pause_lab.place(x=4, y=166, relx=0.85)
        self.speed_scale.config(command=self.replay_set_interval_time)
        self.speed_scale.place(y=126, relx=0.65, relwidth=0.2)
        self.speed_scale.set(500)
        self.add_info(UItext.INFO['replay'])
        self.add_info('\n', update=True)
        path = f'path/{self.mota_env.env_name}/{algorithm_name}/{file_name}'
        self.replay_action_index = np.load(path)
        self.replay_step_num = 0
        self.replay_next_time = time.perf_counter()
        self.processing = True
        self.after(10, self.replay_check)

    # ------------------------------------------------------------------------
    #  通關路線回放結束
    # ------------------------------------------------------------------------
    def replay_finish(self):
        self.processing = False
        self.add_info(UItext.INFO['replay_finish'], 'obvious', update=True)
        self.lab_tooltip.place_forget()
        self.play_btn.place_forget()
        self.back_btn.place_forget()
        self.pause_lab.place_forget()
        self.speed_scale.place_forget()
        self.option_btn1.config(text=UItext.BUTTON['restart1'],
                                command=lambda: self.back_to_start(self.sub_menu_command5))
        self.option_btn1.place(x=12, y=132, width=-16, relx=0.65, relwidth=0.3)
        self.option_btn2.config(text=UItext.BUTTON['restart7'],
                                command=self.reselect_replay_menu)
        self.option_btn2.place(x=12, y=172, width=-16, relx=0.65, relwidth=0.3)

    # ------------------------------------------------------------------------
    #  回放固定時間檢查(取代while True的作法)
    # ------------------------------------------------------------------------
    def replay_check(self):
        if self.processing:
            if not self.replay_pause and time.perf_counter() > self.replay_next_time:
                self.replay_next_time = time.perf_counter() + self.speed_scale.get() * 0.001
                self.replay_enter_action()
            self.after(10, self.replay_check)

    # ------------------------------------------------------------------------
    #  設定動畫每一幀間隔時間(用於演示路線)
    # ------------------------------------------------------------------------
    def replay_set_interval_time(self, value):
        if int(value) == self.speed_scale['to']:
            self.replay_pause = True
            self.play_btn.config(state='enabled')
            self.back_btn.config(state='enabled')
        else:
            self.replay_pause = False
            self.play_btn.config(state='disabled')
            self.back_btn.config(state='disabled')

    # ------------------------------------------------------------------------
    #  退回行動(用於演示路線)
    # ------------------------------------------------------------------------
    def replay_back_action(self):
        if self.replay_step_num > 0:
            self.mota_env.back_step(1, refresh_frame=True)
            self.replay_step_num -= 1
            self.info_text.config(state='normal')
            self.info_text.delete('end-2l', 'end-1l')
            self.add_info(UItext.INFO['step1'] % self.mota_env.get_step_count())
            self.add_info('\n')
            self.info_text.see('end')  # 取代update，加速播放
            # 更新顯示屬性
            self.update_switch_btn()
            if self.nb.winfo_viewable():
                self.attribute_refresh()

    # ------------------------------------------------------------------------
    #  輸入行動(用於演示路線)
    # ------------------------------------------------------------------------
    def replay_enter_action(self):
        if self.replay_step_num < len(self.replay_action_index):
            actions = self.mota_env.get_actions()
            index = self.replay_action_index[self.replay_step_num]
            self.mota_env.step(actions[index], refresh_frame=True)
            self.replay_step_num += 1
            self.info_text.config(state='normal')
            self.info_text.delete('end-2l', 'end-1l')
            self.add_info(UItext.INFO['step1'] % self.mota_env.get_step_count())
            self.add_info('\n')
            self.info_text.see('end')  # 取代update，加速播放
            # 更新顯示屬性
            self.update_switch_btn()
            if self.nb.winfo_viewable():
                self.attribute_refresh()
        else:
            # 回放結束
            self.replay_finish()

    # ------------------------------------------------------------------------
    #  設置通關路線選單
    # ------------------------------------------------------------------------
    def set_replay_combobox(self, event):
        algorithm_name = self.enter_comb.get()
        dir_path = f'path/{self.mota_env.env_name}/{algorithm_name}'
        if os.path.exists(dir_path):
            self.enter_comb2.config(values=os.listdir(dir_path))
        else:
            self.enter_comb2.config(values=[])
        self.enter_comb2.set('')


if __name__ == '__main__':
    window = Window()
    window.mainloop()
