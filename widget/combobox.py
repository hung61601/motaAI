# -*- coding: utf-8 -*-
"""
可以根據文字寬度更改下拉列表框的寬度。
來源自：
https://stackoverflow.com/questions/39915275/change-width-of-dropdown-listbox-of-a-ttk-combobox
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont


class ExtendCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        ttk.Combobox.__init__(self, *args, **kwargs)
        self.bind('<Configure>', self._on_combo_configure)

    def _on_combo_configure(self, event):
        combo = event.widget
        style = ttk.Style()
        # check if the combobox already has the "postoffest" property
        current_combo_style = combo.cget('style') or "TCombobox"
        if len(style.lookup(current_combo_style, 'postoffset')) > 0:
            return
        combo_values = combo.cget('values')
        if len(combo_values) == 0:
            return
        longest_value = max(combo_values, key=len)
        font = tkfont.nametofont(str(combo.cget('font')))
        width = font.measure(longest_value + "0") - event.width
        if width < 0:
            # no need to make the popdown smaller
            return
        # create a unique style name using widget's id
        unique_name = 'Combobox{}'.format(combo.winfo_id())
        # the new style must inherit from current widget style (unless it's our custom style!)
        if unique_name in current_combo_style:
            style_name = current_combo_style
        else:
            style_name = "{}.{}".format(unique_name, current_combo_style)

        style.configure(style_name, postoffset=(0, 0, width, 0))
        combo.configure(style=style_name)


# 測試
if __name__ == '__main__':
    root = tk.Tk()
    root.title("testing the combobox")
    root.geometry('300x300+50+50')
    fruit = ['apples are the best', 'bananas are way more better']

    c = ExtendCombobox(root, values=fruit, width=10)
    c.pack()

    c1 = ExtendCombobox(root, values=['shorter', 'than', 'widget'], width=15)
    c1.pack()

    root.mainloop()
