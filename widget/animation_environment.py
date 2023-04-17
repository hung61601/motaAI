# -*- coding: utf-8 -*-
"""
Animation            by Hung1    2020/7/16

可以顯示代理在環境中行動的過程動畫。
繼承 Mota 類別，在裡面創建與操作 Animation 物件。
支援圖片置中、鼠標拖曳、自動滾動條等功能。
添加了可自由顯示/隱藏節點連線
"""
from env import environment
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class Mota(environment.Mota):
    def __init__(self, mainframe=None):
        """繼承Mota類別"""
        environment.Mota.__init__(self)
        self.anima_frame = Animation(mainframe)
        self.state_table = None
        self.cursor_image_path = 'pictures/cursor.png'

    def create_map(self):
        """建立地圖圖塊"""
        width = self.env_data['floors']['width']
        height = self.env_data['floors']['height']
        map_ = self.env_data['floors']['map']
        maps = self.env_data['maps']
        tile = self.env_data['icons']
        tile_image = Image.open(self.tile_path)
        # 地板平鋪式背景
        bg = Image.new('RGBA', (width * 32, height * 32))
        bf = tile_image.crop((0, 0, 32, 32))
        for i in range(0, width * 32, 32):
            for j in range(0, height * 32, 32):
                bg.paste(bf, (i, j))
        self.anima_frame.bg_image = ImageTk.PhotoImage(bg)
        # 將圖片切成獨立小圖塊
        et = []
        max_tile_id = tile_image.size[0] // 32 * tile_image.size[1] // 32
        for tile_id in range(max_tile_id):
            local = (tile_id % 16 * 32, tile_id // 16 * 32, tile_id % 16 * 32 + 32, tile_id // 16 * 32 + 32)
            et.append(tile_image.crop(local))
        # 建立每一樓層非地板圖塊
        for z, y, x in self.pos_iter():
            n = map_[z][y][x]
            if n == 0:
                continue
            tile_id = tile[maps[n]['id']]
            img = et[tile_id]
            self.anima_frame.create_tile(pos=(z, y, x), image=ImageTk.PhotoImage(img))
            # 同座標多事件
            e = 1
            while True:
                if (z, y, x, e) not in self.p2n:
                    break
                self.anima_frame.create_tile(pos=(z, y, x, e), image=ImageTk.PhotoImage(img))
                e += 1

    def create_nodes(self):
        """建立節點連線"""
        return_ = environment.Mota.create_nodes(self)
        for node, pos in self.n2p.items():
            for node2 in node.links:
                self.anima_frame.create_link(pos, self.n2p[node2])
        return return_

    def build_anima_frame(self, **kwargs):
        """建立動畫框架"""
        img = Image.open(self.cursor_image_path)
        self.anima_frame.cursor_image = ImageTk.PhotoImage(img)
        self.anima_frame.build_canvas(player_pos=self.n2p[self.player], **kwargs)
        for pos in self.env_data['floors']['disable']:
            self.anima_frame.hide_tile(pos)
            self.anima_frame.hide_line(pos)
        self.refresh_state_table()

    def build_state_table(self, mainframe, columns, widths, **kwargs):
        """建立狀態表格"""
        self.state_table = ttk.Treeview(mainframe, columns=columns, **kwargs)
        for c, w in zip(columns, widths):
            self.state_table.column(c, width=w, anchor='center')
            self.state_table.heading(c, text=c)
        self.state_table.insert('', 'end', values=['--'] * len(columns))

    def refresh_state_table(self):
        """刷新狀態窗口"""
        if self.state_table:
            for item in self.state_table.get_children():
                self.state_table.delete(item)
            self.state_table.insert('', 'end', values=list(self.get_player_state()))

    def destroy_anima_frame(self):
        """摧毀動畫框架"""
        # 此方法還是會崩潰
        # for widget in self.anima_frame.winfo_children():
        #     widget.destroy()
        if self.anima_frame.canvas:
            for widget in self.anima_frame.canvas.winfo_children():
                widget.destroy()
            self.anima_frame.canvas.destroy()
        self.anima_frame.destroy()
        # 用以釋放記憶體資源，避免導致程式崩潰
        del self.anima_frame

    def destroy_state_table(self):
        """摧毀狀態表格"""
        self.state_table.destroy()
        # 用以釋放記憶體資源，避免導致程式崩潰
        del self.state_table

    def step(self, action, refresh_frame=False, **kwargs):
        """輸入行動"""
        if refresh_frame:
            pos = self.n2p[self.observation[-1]]
            self.anima_frame.hide_line(pos)
            return_ = environment.Mota.step(self, action, **kwargs)
            pos = self.n2p[action]
            if action.activated:
                self.anima_frame.hide_tile(pos)
            # 主角移動
            self.anima_frame.player_move(pos)
            # 行動後連線
            for node2 in self.get_actions():
                self.anima_frame.show_line(pos, self.n2p[node2])
            self.anima_frame.top_player()
            # 事件後處理(全局處理)
            if pos in self.env_data['floors']['afterEvent']:
                for command in self.env_data['floors']['afterEvent'][pos]:
                    if command['type'] == 'open':
                        pos = command['loc']
                        self.anima_frame.hide_tile(pos)
                        self.anima_frame.hide_line(pos)
                    elif command['type'] == 'enable':
                        pos = command['loc']
                        self.anima_frame.show_tile(pos)
            self.refresh_state_table()
            return return_
        else:
            return environment.Mota.step(self, action, **kwargs)

    def back_step(self, times, refresh_frame=False):
        """退回行動"""
        if refresh_frame:
            # 懶得做了......
            if times != 1:
                raise tk.TclError('You can only use 1 time in back_step refresh_frame')
            pos = self.n2p[self.observation[-times]]
            self.anima_frame.show_tile(pos)
            # 事件後處理(全局處理)
            if pos in self.env_data['floors']['afterEvent']:
                for command in self.env_data['floors']['afterEvent'][pos]:
                    if command['type'] == 'open':
                        pos2 = command['loc']
                        self.anima_frame.show_tile(pos2)
                        for node2 in self.observation[-times].links:
                            self.anima_frame.show_line(pos2, self.n2p[node2])
                    elif command['type'] == 'enable':
                        pos = command['loc']
                        self.anima_frame.hide_tile(pos)
                        self.anima_frame.hide_line(pos)
            environment.Mota.back_step(self, times)
            # 返回後
            self.anima_frame.delete_new_lines()
            pos = self.n2p[self.observation[-times]]
            self.anima_frame.player_move(pos)
            for node2 in self.get_actions():
                self.anima_frame.show_line(pos, self.n2p[node2])
            self.anima_frame.top_player()
            self.refresh_state_table()
        else:
            environment.Mota.back_step(self, times)

    def reset(self, refresh_frame=False):
        """重置環境"""
        environment.Mota.reset(self)
        if refresh_frame:
            self.anima_frame.is_hidden.clear()
            self.anima_frame.delete_new_lines()
            for pos in self.env_data['floors']['disable']:
                self.anima_frame.hide_tile(pos)
                self.anima_frame.hide_line(pos)
            pos = self.n2p[self.player]
            self.anima_frame.player_move(pos)
            # 若主角在初始樓層時重置，則另外進行刷新。
            if pos[0] == self.anima_frame.now_floor:
                self.anima_frame.change_floor(self.anima_frame.now_floor)
            self.refresh_state_table()

    def frame_reset(self):
        """重置窗口並回復原本環境進度。該方法會花上較長時間"""
        original_observation = self.observation.copy()
        self.reset(refresh_frame=True)
        for action in original_observation[1:]:
            self.step(action, refresh_frame=False)

    def frame_recover(self):
        """追回動畫進度。該方法會花上較長時間"""
        original_observation = self.observation.copy()
        self.reset(refresh_frame=True)
        for action in original_observation[1:-1]:
            pos = self.n2p[self.observation[-1]]
            self.anima_frame.hide_line(pos)
            environment.Mota.step(self, action)
            pos = self.n2p[action]
            if action.activated:
                self.anima_frame.hide_tile(pos)
            # 事件後處理(全局處理)
            if pos in self.env_data['floors']['afterEvent']:
                for command in self.env_data['floors']['afterEvent'][pos]:
                    if command['type'] == 'open':
                        pos = command['loc']
                        self.anima_frame.hide_tile(pos)
                        self.anima_frame.hide_line(pos)
        if len(original_observation) > 1:
            self.step(original_observation[-1], refresh_frame=True)

    def anima_line_visible(self, is_visible=True):
        """改變動畫連線是否可見"""
        self.anima_frame.line_visible = is_visible
        self.anima_frame.change_new_lines_visible()
        self.anima_frame.change_floor(self.anima_frame.now_floor)

    def update_frame(self):
        """更新動畫和狀態窗口"""
        self.anima_frame.update()
        if self.state_table:
            self.state_table.update()


class AutoScrollbar(ttk.Scrollbar):
    """自動滾動條"""

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class Animation(tk.Frame):
    """動畫框架，作為Mota內部使用"""

    def __init__(self, mainframe):
        """初始化"""
        tk.Frame.__init__(self, master=mainframe)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.max_floor_num = 0
        self.canvas = None
        self.bg_image = None
        self.cursor_image = None
        self.floor_items = {}
        self.floor_lines = {}
        self.tile_id = {}
        self.link_id = []
        self.items_id = {}
        self.lines_id = {}
        self.lines_id_t2 = {}  # 適用於hide_line()
        self.new_lines_id = {}
        self.player = None
        self.player_pos = None
        self.cursor_pos = (-1, -1, -1)
        self.is_hidden = set()
        self.now_floor = 0
        self.line_visible = True
        self.ever_used_mouse = False  # 自動置中窗口判斷用

    def create_tile(self, pos, image):
        """儲存圖塊圖片"""
        self.tile_id[pos] = image

    def create_link(self, pos, pos2):
        """儲存連線資訊"""
        # 不取同座標事件
        pos = pos[:3]
        pos2 = pos2[:3]
        if (pos, pos2) not in self.link_id:
            if (pos2, pos) not in self.link_id:
                if pos[0] == pos2[0]:
                    self.link_id.append((pos, pos2))

    def build_canvas(self, player_pos, bg='blue'):
        """建立畫布"""
        self.player_pos = player_pos
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        self.canvas = tk.Canvas(self.master, highlightthickness=0, bg=bg,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        vbar.config(command=self.canvas.yview)
        hbar.config(command=self.canvas.xview)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        # 事件處理
        self.canvas.bind('<ButtonPress-1>', self._move_from)
        self.canvas.bind('<B1-Motion>', self._move_to)
        self.canvas.bind('<Configure>', self._update_scroll_region)
        # 地板背景
        self.background = self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
        # 圖塊
        for pos, img in self.tile_id.items():
            self.items_id[pos] = self.canvas.create_image(pos[2] * 32, pos[1] * 32,
                                                          image=img, anchor='nw', state='hidden')
            if pos[0] not in self.floor_items:
                self.floor_items[pos[0]] = []
                self.floor_lines[pos[0]] = []
            if pos != self.player_pos:
                self.floor_items[pos[0]].append(self.items_id[pos])
        # 連線
        for label in self.link_id:
            x0, y0 = label[0][2] * 32 + 16, label[0][1] * 32 + 16
            x1, y1 = label[1][2] * 32 + 16, label[1][1] * 32 + 16
            self.lines_id[label] = self.canvas.create_line(x0, y0, x1, y1, fill='#01FF11',
                                                           width=3, stipple='gray50', state='hidden')
            self.floor_lines[label[0][0]].append(self.lines_id[label])
            if label[0] not in self.lines_id_t2:
                self.lines_id_t2[label[0]] = []
            self.lines_id_t2[label[0]].append(self.lines_id[label])
            if label[1] not in self.lines_id_t2:
                self.lines_id_t2[label[1]] = []
            self.lines_id_t2[label[1]].append(self.lines_id[label])
        # 更新畫布拖曳範圍
        self.canvas.update()
        self._update_scroll_region(None)
        # 紀錄最大樓層數
        self.max_floor_num = max(self.floor_items)
        # 創建光標(中心錨點)
        self.cursor = self.canvas.create_image(0, 0, image=self.cursor_image,
                                               anchor='center', state='hidden')
        # 主角就位
        self.player = self.items_id[self.player_pos]
        self.change_floor(self.player_pos[0])
        self.top_player()

    def _move_from(self, event):
        """記住以前使用鼠標滾動的坐標"""
        self.ever_used_mouse = True
        self.canvas.scan_mark(event.x, event.y)

    def _move_to(self, event):
        """將畫布移動到新位置"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _move_to_center(self, width, height):
        """將畫布移動到中央位置"""
        x = max(0, self.canvas.winfo_width() // 2 - width // 2)
        y = max(0, self.canvas.winfo_height() // 2 - height // 2)
        self.canvas.scan_dragto(x, y, gain=1)

    def _update_scroll_region(self, event):
        """更新滾動範圍"""
        width, height = self.bg_image.width(), self.bg_image.height()
        if not self.ever_used_mouse:
            self._move_to_center(width, height)
        self.canvas.config(scrollregion=(0, 0, width, height))

    def hide_tile(self, pos):
        """隱藏圖塊"""
        item = self.items_id[pos]
        self.canvas.itemconfig(item, state='hidden')
        self.is_hidden.add(item)

    def show_tile(self, pos):
        """顯示圖塊"""
        item = self.items_id[pos]
        # 若連線在當前樓層才顯示
        if pos[0] == self.now_floor:
            self.canvas.itemconfig(item, state='normal')
        if item in self.is_hidden:
            self.is_hidden.remove(item)

    def _hide_line(self, pos, pos2):
        """隱藏連線(廢棄)"""
        label = (pos, pos2)
        label2 = (pos2, pos)
        if label in self.lines_id:
            item = self.lines_id[label]
        elif label2 in self.lines_id:
            item = self.lines_id[label2]
        elif label in self.new_lines_id:
            item = self.new_lines_id[label]
            self.canvas.delete(item)
            self.new_lines_id.pop(label)
            return
        elif label2 in self.new_lines_id:
            item = self.new_lines_id[label2]
            self.canvas.delete(item)
            self.new_lines_id.pop(label2)
            return
        else:
            return
        self.canvas.itemconfig(item, state='hidden')
        self.is_hidden.add(item)

    def hide_line(self, pos):
        """隱藏連線"""
        if pos in self.lines_id_t2:
            for item in self.lines_id_t2[pos]:
                self.canvas.itemconfig(item, state='hidden')
                self.is_hidden.add(item)
        self.delete_new_lines()

    def delete_new_lines(self):
        """刪除新建連線"""
        for line in self.new_lines_id.values():
            self.canvas.delete(line)
        self.new_lines_id.clear()

    def change_new_lines_visible(self):
        """改變新建連線是否可見"""
        if self.line_visible:
            for line in self.new_lines_id.values():
                self.canvas.itemconfig(line, state='normal')
        else:
            for line in self.new_lines_id.values():
                self.canvas.itemconfig(line, state='hidden')

    def show_line(self, pos, pos2):
        """顯示連線"""
        label = (pos, pos2)
        label2 = (pos2, pos)
        if label in self.lines_id:
            item = self.lines_id[label]
        elif label2 in self.lines_id:
            item = self.lines_id[label2]
        elif label in self.new_lines_id:
            item = self.new_lines_id[label]
        elif label2 in self.new_lines_id:
            item = self.new_lines_id[label2]
        # 建立新連線
        elif pos[0] == pos2[0] and pos[0] == self.now_floor:
            x0, y0 = label[0][2] * 32 + 16, label[0][1] * 32 + 16
            x1, y1 = label[1][2] * 32 + 16, label[1][1] * 32 + 16
            self.new_lines_id[label] = self.canvas.create_line(x0, y0, x1, y1, fill='#01FF11', width=3,
                                                               stipple='gray50')
            if not self.line_visible:  # 添加可自由顯示連線
                self.canvas.itemconfig(self.new_lines_id[label], state='hidden')
            return
        else:
            return
        # 若連線在當前樓層才顯示
        if pos[0] == self.now_floor:
            if self.line_visible:  # 添加可自由顯示連線
                self.canvas.itemconfig(item, state='normal')
            else:
                self.canvas.itemconfig(item, state='hidden')
        if item in self.is_hidden:
            self.is_hidden.remove(item)

    def player_move(self, pos):
        """玩家移動"""
        self.player_pos = pos
        if self.now_floor != pos[0]:
            self.delete_new_lines()
            self.change_floor(pos[0])
        else:
            # 主角一定會顯示
            self.canvas.itemconfig(self.player, state='normal')
        self.canvas.coords(self.player, pos[2] * 32, pos[1] * 32)

    def top_player(self):
        """將主角移到圖層最頂層"""
        self.canvas.tag_raise(self.player)

    def change_floor(self, floor):
        """切換樓層地圖"""
        if self.now_floor != floor:
            # 隱藏之前樓層物件
            for item in self.floor_items[self.now_floor]:
                self.canvas.itemconfig(item, state='hidden')
            for line in self.floor_lines[self.now_floor]:
                self.canvas.itemconfig(line, state='hidden')
            for line in self.new_lines_id.values():
                self.canvas.itemconfig(line, state='hidden')
            self.now_floor = floor
        # 顯示切換後樓層物件
        for item in self.floor_items[self.now_floor]:
            if item not in self.is_hidden:
                self.canvas.itemconfig(item, state='normal')
        for line in self.floor_lines[self.now_floor]:
            if line not in self.is_hidden:
                # 添加可自由顯示連線
                if self.line_visible:
                    self.canvas.itemconfig(line, state='normal')
                else:
                    self.canvas.itemconfig(line, state='hidden')
        for label, line in self.new_lines_id.items():
            # 添加可自由顯示連線(新線特別處理)
            if label[0][0] == self.now_floor and self.line_visible:
                self.canvas.itemconfig(line, state='normal')
            else:
                self.canvas.itemconfig(line, state='hidden')
        # 若主角在當前樓層，則顯示主角
        if self.player_pos[0] == floor:
            self.canvas.itemconfig(self.player, state='normal')
        else:
            self.canvas.itemconfig(self.player, state='hidden')
        # 若光標在當前樓層，則顯示光標
        if self.cursor_pos[0] == floor:
            self.canvas.itemconfig(self.cursor, state='normal')
        else:
            self.canvas.itemconfig(self.cursor, state='hidden')

    def check_up_floor(self):
        """檢查是否有上樓層"""
        if self.now_floor == self.max_floor_num:
            return False
        else:
            return True

    def check_down_floor(self):
        """檢查是否有下樓層"""
        if self.now_floor == 0:
            return False
        else:
            return True

    def up_floor(self):
        """切換至當前上一樓層，該方法供外部使用"""
        if self.check_up_floor():
            self.change_floor(self.now_floor + 1)

    def down_floor(self):
        """切換至當前下一樓層，該方法供外部使用"""
        if self.check_down_floor():
            self.change_floor(self.now_floor - 1)

    def show_cursor(self, pos):
        """顯示光標，該方法供外部使用"""
        self.cursor_pos = pos
        self.canvas.tag_raise(self.cursor)
        self.canvas.coords(self.cursor, pos[2] * 32 + 16, pos[1] * 32 + 16)
        self.change_floor(pos[0])

    def hide_cursor(self):
        """隱藏光標，該方法供外部使用"""
        self.cursor_pos = (-1, -1, -1)
        self.canvas.itemconfig(self.cursor, state='hidden')


# 測試
if __name__ == '__main__':
    import time


    def run():
        btn.place_forget()
        choose_index_list = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0,
            0, 2, 0, 1, 0, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 2,
            2, 0, 4, 0, 0, 0, 1, 5, 4, 0, 0, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 1, 3, 0, 0,
            1, 1, 0, 0, 0, 0, 3, 1, 0, 0, 0, 0, 1, 2, 0, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0,
            0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 2, 5, 1, 0, 0, 0, 9, 2, 8, 1, 1, 0, 0, 0, 0,
            0, 1, 2, 1, 0, 17, 0, 13, 0, 4, 0, 0, 22, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 1, 25,
            0, 11, 2, 2, 1, 1, 1, 0, 0, 13, 10, 0, 7, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 4,
            1, 0, 16, 6, 1, 1, 0, 9, 19, 19, 0, 0, 0, 0, 0, 0, 20, 1, 1, 9, 9, 0, 16, 1, 16,
            5, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 1, 0, 0, 4, 7, 18, 0, 21, 24, 2, 0, 33, 17,
            0, 1, 0, 0, 0, 0, 7, 0, 0, 6, 2, 0, 1, 5, 11, 0, 0, 0, 0, 0, 15, 2, 28, 24, 2,
            0, 0, 14, 0, 0, 0, 1, 0, 0, 0, 28, 0, 0, 0, 0, 5, 40, 5, 42, 1, 5, 40, 24, 3, 3,
            0, 0, 0, 0, 0, 1, 0, 0, 43, 0, 0, 0, 0, 0, 0, 0, 38, 5, 0, 2, 0, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 2, 24, 0, 0, 48, 18, 0, 0, 0, 41, 0, 0, 0, 0, 0, 0, 1, 0,
            0, 0, 0, 0, 30, 27, 0, 0, 0, 1, 1, 0, 44, 2, 0, 1, 26, 0, 13, 0, 35, 0, 0, 13, 23,
            40, 6, 0, 1, 0, 21, 0, 1, 0, 0, 0, 11, 0, 27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 43, 17, 0, 0, 1, 43, 0, 0, 0, 43, 1, 9, 0, 48, 0, 0, 7, 0, 1, 1,
            6, 0, 0, 42, 0, 0, 3, 0, 0, 11, 0, 25, 0, 43, 40, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 44, 0, 0, 38, 42, 0, 0, 0, 2, 2, 0, 2, 2, 1, 1, 0, 0, 1, 42, 0,
            0, 47, 0, 42, 0, 0, 46, 0, 0, 19, 19, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 45, 2, 0, 0, 0, 2, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 53, 0, 0, 57, 33, 25, 0, 0, 0, 0, 0,
            1, 0, 0, 0, 0, 0, 50, 0, 0, 53, 0, 0, 15, 24, 0, 1, 0, 47, 0, 0, 0, 40, 0, 0, 0,
            0, 0, 40, 0, 0, 51, 52, 0, 0, 0, 51, 0, 6, 0, 0, 0, 0, 0, 59, 0, 0, 7, 0, 0, 0,
            0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 54, 7, 45, 47, 2, 0, 0, 0, 8, 0, 0,
            0, 40, 0, 0, 0, 0, 42, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            56, 2, 0, 32, 21, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 55, 0, 52, 57, 0, 56, 8, 55,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
            2, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0,
            0, 1, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 2, 6, 49, 71, 29, 40, 0, 0,
            71, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 20, 22, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 1, 0, 0,
            0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 4, 8, 0, 0, 1,
            0, 1, 0, 0, 2, 2, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 7, 0, 0, 1, 0, 0,
            1, 5, 2, 0, 0, 0, 0, 4, 0, 0, 0, 0, 3, 19, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
            4, 0, 6, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 6, 16, 78, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            78, 0, 0, 0, 74, 0, 0, 0, 72, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 45, 0, 0,
            0, 0, 0, 46, 0, 0, 1, 0, 8, 28, 41, 40, 0, 0, 37, 1, 12, 23, 12, 32, 12, 0, 0, 0, 3,
            24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 0, 0, 5, 21, 20, 0, 20, 0, 2, 0, 0, 0, 0, 12,
            9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0, 2, 0, 0, 1, 1, 0, 2, 4, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
            0]
        for _ in range(1):
            for i, index in enumerate(choose_index_list):
                actions = env.get_feasible_actions()
                env.step(actions[index], refresh_frame=True)
                # time.sleep(0.05)
                env.update_frame()
            print('score:', env.player.hp)
            time.sleep(2)
            for j in range(len(choose_index_list)):
                env.back_step(1, refresh_frame=True)
                time.sleep(0.05)
                env.update_frame()
            env.reset()
            root.update()
            time.sleep(0.3)


    def show_line():
        env.anima_line_visible(True)
        root.update()


    def hide_line():
        env.anima_line_visible(False)
        root.update()


    root = tk.Tk()
    winWidth = 806
    winHeight = 499
    _x = (root.winfo_screenwidth() - winWidth) // 2
    _y = (root.winfo_screenheight() - winHeight) // 3
    root.geometry('%sx%s+%s+%s' % (winWidth, winHeight, _x, _y))
    # 左側畫面
    frm = ttk.LabelFrame(text='Animation Map')
    frm.place(relwidth=0.6, relheight=1.0)
    # 動畫窗口
    env = Mota(frm)
    env.cursor_image_path = '../pictures/cursor.png'
    env.tile_path = '../pictures/baseTile.png'
    env.build_env('24層魔塔 (html5)')
    btn = tk.Button(root, text='run', command=run)
    btn.place(relx=0.7, rely=0.5, width=160)
    btn2 = tk.Button(root, text='show line', command=show_line)
    btn2.place(relx=0.7, rely=0.6, width=160)
    btn3 = tk.Button(root, text='hide line', command=hide_line)
    btn3.place(relx=0.7, rely=0.7, width=160)
    env.create_map()
    env.create_nodes()
    env.build_anima_frame()
    root.mainloop()
