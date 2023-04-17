# -*- coding: utf-8 -*-
"""
LabelImage            by Hung1    2020/6/19

能夠隨著窗口縮放，圖片尺寸也會跟著改變。
在該類底下創建的圖片小部件不會隨著窗口縮放而被延伸，且支援透明效果。
可以作為窗口背景以及標題圖片使用。
"""
import tkinter as tk
from PIL import Image, ImageTk


class _LabelWidget(tk.Label):
    """作為Label_Image內部小部件使用"""

    # 以root參數取代了master參數，解決小部件個別在place後進行update_widget會發生圖像無法顯示的問題。
    def __init__(self, im, root, **kw):
        tk.Label.__init__(self, **kw)
        self.im = im
        self.root = root

    def grid(self, **kw):
        print('Warning: Label_Widget use grid is not debugged.')
        tk.Label.grid(self, **kw)
        self.root.update_widget(self)

    def pack(self, **kw):
        print('Warning: Label_Widget use pack is not debugged.')
        tk.Label.pack(self, **kw)
        self.root.update_widget(self)

    def place(self, **kw):
        # 不設置width和height(或是relwidth和relheight)，會導致文字加圖片的Label存在邊框，且無法去除的問題。
        if not ('width' in kw or 'relwidth' in kw):
            if self.im is None:
                raise tk.TclError('Label_Widget is not setting width.')
            else:
                width, _ = self.im.size
                kw['width'] = width
        if not ('height' in kw or 'relheight' in kw):
            if self.im is None:
                raise tk.TclError('Label_Widget is not setting height.')
            else:
                _, height = self.im.size
                kw['height'] = height
        tk.Label.place(self, **kw)
        self.root.update_widget(self)


class LabelImage(tk.Label):
    def __init__(self, mainframe, picture_path):
        """初始化"""
        self.im = Image.open(picture_path)
        self.im_copy = self.im.copy()
        self.img = ImageTk.PhotoImage(self.im)
        self.widget_image = {}
        tk.Label.__init__(self, master=mainframe, image=self.img)
        self.bind('<Configure>', self._resize_image)

    def _resize_image(self, event):
        """改變圖片尺寸"""
        new_width = event.width
        new_height = event.height
        self.im = self.im_copy.resize((new_width, new_height))
        self.img = ImageTk.PhotoImage(self.im)
        self.configure(image=self.img)
        self.update_all_widget()

    def create_label_widget(self, image_path=None, **kw):
        """創建Label小部件"""
        if image_path is None:
            im = None
            lab = _LabelWidget(im=im, root=self, bd=0, compound='center', **kw)
        else:
            im = Image.open(image_path)
            img = ImageTk.PhotoImage(im)
            # 不添加image這個參數，會導致部件使用預設窗口大小
            lab = _LabelWidget(im=im, root=self, image=img, bd=0, compound='center', **kw)
        self.widget_image[lab] = None
        return lab

    def change_widget_image(self, lab, new_image_path):
        """改變Label小部件的圖片"""
        lab.im = Image.open(new_image_path)
        self.update_widget(lab)

    def update_all_widget(self):
        """更新全部Label小部件"""
        for lab in self.widget_image:
            self.update_widget(lab)

    def update_widget(self, lab):
        """更新Label小部件"""
        lab.update()
        if lab.winfo_viewable():
            x, y = lab.winfo_x(), lab.winfo_y()
            width, height = lab.winfo_width(), lab.winfo_height()
            region = (x, y, x + width, y + height)
            cropped = self.im.crop(region)
            if lab.im is not None:
                r, g, b, a = lab.im.split()
                cropped.paste(lab.im, (0, 0), mask=a)
            img = ImageTk.PhotoImage(cropped)
            lab.configure(image=img)
            self.widget_image[lab] = img


# 測試
if __name__ == '__main__':
    def show():
        image_lab.place(x=-290, y=-73, relx=0.5, rely=0.2)
        text_lab.place(height=20, relx=0.4, rely=0.4, relwidth=0.2)
        image_text_lab.place(x=-120, y=0, relx=0.5, rely=0.5)


    def hide():
        image_lab.place_forget()
        text_lab.place_forget()
        image_text_lab.place_forget()
        text_lab.config(text='New Label Text')


    root_window = tk.Tk()
    root_window.title("Title")
    root_window.geometry("800x600")
    root_window.configure(background="black")
    background = LabelImage(root_window, '../pictures/background.jpg')
    background.pack(fill='both', expand=1)
    image_lab = background.create_label_widget('../pictures/text_logo.png', master=root_window)
    text_lab = background.create_label_widget(text='Label Text', master=root_window, font='Arial 16')
    image_text_lab = background.create_label_widget('../pictures/menu_red.png', master=root_window, text='Label Text',
                                                    font='Arial 16')
    tk.Button(root_window, text='show', command=show).place(x=-50, relx=0.5, rely=0.7, width=100)
    tk.Button(root_window, text='hide', command=hide).place(x=-50, relx=0.5, rely=0.8, width=100)
    root_window.mainloop()

'''
參考資料：
【编程】Tkinter组件的背景透明
https://www.jianshu.com/p/d27a772d402d
Basic Widget Methods
https://effbot.org/tkinterbook/widget.htm
The Tkinter Label Widget
http://effbot.org/tkinterbook/label.htm
The Tkinter Button Widget
http://effbot.org/tkinterbook/button.htm
How to change ttk button background and foreground when hover it in tkinter
https://stackoverflow.com/questions/57186536/how-to-change-ttk-button-background-and-foreground-when-hover-it-in-tkinter
Tkinter 8.5 reference: a GUI for Python
https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-map.html
'''
