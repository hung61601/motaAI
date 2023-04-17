# -*- coding: utf-8 -*-
"""
ui_text 文本讀取            by Hung1    2020/7/5

讀取目錄下的String.py檔，String.py檔不用被打包進程式裡，且檔案可公開並可供其他人檢視。
"""
import sys
import tkinter as tk
import tkinter.messagebox

filepath = 'translation\\Strings.py'


def _showwarning(text):
    try:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showwarning('Error', text)
        root.destroy()
    except:
        pass
    sys.exit()


try:
    # 將檔案文本當成有效Python代碼來執行
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'))
except FileNotFoundError:
    _showwarning('File not found: %s' % filepath)
except:
    _showwarning('File open Error: %s' % filepath)
