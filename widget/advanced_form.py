# -*- coding: utf-8 -*-
"""
AdvancedForm            by Hung1    2020/1/19

高級表格。
1. 可以點選欄位進行排序
2. 彩色表格(windows失效)
3. 有滾動條
逐行讀取檔案：
https://www.itread01.com/content/1546998967.html
"""
import tkinter as tk
from tkinter import ttk


class AdvancedForm(tk.Frame):
    def __init__(self, mainframe, columns, widths, data, min_len=0, max_len=10, **kwargs):
        tk.Frame.__init__(self, master=mainframe, **kwargs)
        self.columns = columns
        self.length = len(data)
        self.min_len = min_len
        if min_len > max_len:
            self.max_len = self.min_len
        else:
            self.max_len = max_len
        # 滾動條
        self.scrollbar = ttk.Scrollbar(self)
        # 表格
        self.treeview = ttk.Treeview(self, height=self._get_height(),
                                     show='headings', columns=columns)
        for c, w in zip(columns, widths):
            self.treeview.column(c, width=w, anchor='center')
            self.treeview.heading(c, text=c, command=lambda _c=c: self._treeview_sort_column(_c, False))
        for i in range(self.length):
            self.treeview.insert('', i, values=data[i])
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.treeview.yview)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # 此滾動條顯示是由max_len判斷，要由yview判斷請執行update()
        if self.length > max_len:
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.treeview.grid(row=0, column=0, sticky='nswe')

    def clear(self):
        """清除表格內容"""
        self.length = 0
        self._recover_heading()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.treeview.configure(height=self._get_height())

    def insert(self, data):
        """表格插入新內容"""
        self.length += len(data)
        self.treeview.configure(height=self._get_height())
        for col in data:
            self.treeview.insert('', 'end', values=col)

    def delete(self, items):
        """表格刪除內容"""
        self.length -= len(items)
        for item in items:
            self.treeview.delete(item)
        self.treeview.configure(height=self._get_height())

    def update(self):
        """繼承update，刷新滾動條"""
        tk.Frame.update(self)
        if self.treeview.yview() != (0.0, 1.0):
            self.scrollbar.grid(row=0, column=1, sticky='ns')
        else:
            self.scrollbar.grid_forget()

    def _get_height(self):
        return min(self.max_len, max(self.min_len, self.length))

    def _recover_heading(self):
        for c in self.columns:
            self.treeview.heading(c, text=c,
                                  command=lambda _c=c: self._treeview_sort_column(_c, False))

    def _treeview_sort_column(self, _c, reverse):
        children = [(self.treeview.set(k, _c), k) for k in self.treeview.get_children('')]
        children.sort(reverse=reverse)
        for index, (val, k) in enumerate(children):
            self.treeview.move(k, '', index)
        # 復原標題
        self._recover_heading()
        # 重寫標題，下次變倒序
        pattern = '↑' if reverse else '↓'
        self.treeview.heading(_c, text=pattern + _c,
                              command=lambda: self._treeview_sort_column(_c, not reverse))


if __name__ == '__main__':
    import pandas as pd

    show_num = [32, 33, 34, 35]
    maps = {
        32: {'cls': 'enemies', 'id': 'greenSlime'},
        33: {'cls': 'enemies', 'id': 'redSlime'},
        34: {'cls': 'enemies', 'id': 'bat'},
        35: {'cls': 'enemies', 'id': 'skeleton'},
        36: {'cls': 'enemies', 'id': 'bluePriest'},
        37: {'cls': 'enemies', 'id': 'blackSlime'},
    }
    enemies = {
        'greenSlime': {'hp': 35, 'atk': 10, 'def': 2, 'money': 1, 'exp': 0},
        'redSlime': {'hp': 45, 'atk': 12, 'def': 4, 'money': 1, 'exp': 0},
        'bat': {'hp': 30, 'atk': 18, 'def': 1, 'money': 1, 'exp': 0},
        'skeleton': {'hp': 50, 'atk': 25, 'def': 0, 'money': 1, 'exp': 0},
        'bluePriest': {'hp': 60, 'atk': 20, 'def': 5, 'money': 1, 'exp': 0},
        'blackSlime': {'hp': 80, 'atk': 24, 'def': 10, 'money': 1, 'exp': 0},
        'yellowGuard': {'hp': 150, 'atk': 20, 'def': 15, 'money': 1, 'exp': 0}
    }
    test_columns = ['num', 'id', 'hp', 'atk', 'def', 'money', 'exp']
    test_widths = [50, 150, 70, 50, 50, 50, 50]
    show_merge = [{**maps[k], **enemies[maps[k]['id']]} for k in show_num]
    df = pd.DataFrame(show_merge).fillna('')
    df['num'] = show_num
    df = df[test_columns]
    show_data = df.values.tolist()

    root = tk.Tk()
    root.title("Advanced Form Test")
    root.geometry("800x600")
    af = AdvancedForm(root, test_columns, test_widths, show_data * 1, min_len=5)
    af.pack(fill='x')
    af.clear()
    af.insert(show_data * 4)
    af.update()
    root.mainloop()
