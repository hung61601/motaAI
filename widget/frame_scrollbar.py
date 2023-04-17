# -*- coding: utf-8 -*-
"""
FrameScrollbar            by Hung1    2020/6/21

可以根據Frame的大小產生滾動條。
設定contents_center之後，當畫布大於內容窗口時，內容可以置中。
"""
import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk


class AutoScrollbar(ttk.Scrollbar):
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


class FrameScrollbar(tk.Frame):
    def __init__(self, mainframe, bg='light gray', contents_center=False):
        tk.Frame.__init__(self, master=mainframe, bg=bg)
        # 內容是否置中
        self.contents_center = contents_center
        # 滾動條
        vbar = AutoScrollbar(self, orient='vertical')
        hbar = AutoScrollbar(self, orient='horizontal')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='we')
        # 畫布
        self.canvas = tk.Canvas(self, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set,
                                background=bg)
        self.canvas.grid(row=0, column=0, sticky='nswe')
        # 滾動條滾動處理
        vbar.config(command=self.canvas.yview)
        hbar.config(command=self.canvas.xview)
        # 畫布延伸填滿窗口
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # 內容框架
        self.contents = tk.Frame(self.canvas, background=bg)
        self.canvas.create_window(0, 0, window=self.contents, anchor='nw')
        # 滾動範圍判斷
        self.canvas.bind('<Configure>', self._update_scroll_region)
        # 鼠標進入窗口範圍內啟用滾動條
        self.canvas.bind('<Enter>', self._set_binds_canvas)
        # 鼠標離開窗口範圍內禁用滾動條
        self.canvas.bind('<Leave>', self._unset_binds_canvas)

    def clear(self):
        """銷毀框架中的所有小部件"""
        for widget in self.contents.winfo_children():
            widget.destroy()
        self.contents.configure(height=1, width=1)

    def update(self):
        """繼承update，刷新滾動條事件"""
        tk.Frame.update(self)
        self._update_scroll_region(None)

    def _move_to_center(self):
        x = max(0, self.canvas.winfo_width() // 2 - self.contents.winfo_width() // 2)
        y = max(0, self.canvas.winfo_height() // 2 - self.contents.winfo_height() // 2)
        self.canvas.scan_dragto(x, y, gain=1)

    def _update_scroll_region(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        if self.contents_center:
            self._move_to_center()

    def _set_binds_canvas(self, event):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unset_binds_canvas(self, event):
        self.canvas.unbind_all('<MouseWheel>')

    def _on_mousewheel(self, event):
        # 當內容不足時，禁止任何滾動處理
        if self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')


# 測試
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x400')
    notebook = ttk.Notebook(root)
    frm = FrameScrollbar(notebook)
    for i in range(5):
        f = tk.Frame(frm.contents)
        label = tk.Label(f, text=f'label text {i * 2}', width=40, height=10)
        label.pack(expand=True, side='left')
        label = tk.Label(f, text=f'label text {i * 2 + 1}', width=40, height=10)
        label.pack(expand=True, side='right')
        f.pack()
    # 其他裝飾
    notebook.add(frm, text='frm')
    tab = tk.Frame(notebook, bg='blue')
    notebook.add(tab, text='tag')
    notebook.place(relwidth=0.6, relheight=1.0)
    lfrm = ttk.LabelFrame(root, text='Information')
    scr = tk.scrolledtext.ScrolledText(lfrm)
    lfrm.place(relx=0.6, relwidth=0.4, relheight=1.0)
    scr.pack(fill='both', expand=True)
    for i in range(51):
        scr.insert(tk.END, f'{i}\n')
    root.mainloop()
