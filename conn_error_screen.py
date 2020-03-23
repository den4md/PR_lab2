from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import threading

import thread_single

image = None
image_set = False


def show(root: Tk, elems, load, logic):
    try:
        frame = ttk.Frame(root)

        global image_set
        if not image_set:
            global image
            image = ImageTk.PhotoImage(Image.open("imgs/wifi.png"))
            image_set = True

        label = ttk.Label(frame, text='wifi_image')
        label['image'] = image

        label2 = ttk.Label(frame, text='Что-то не так с интернет-соединением')

        single = thread_single.Singleton()
        single.thr = threading.Thread(target=load, args=(root, logic))
        btn = ttk.Button(frame, text='Побробовать ещё', command=lambda: single.start())

        elems.append(frame)
        # elems.append(label)
        # elems.append(label2)
        # elems.append(btn)
        frame.grid()
        label.grid()
        label2.grid()
        btn.grid(pady=20)
    except RuntimeError:
        print('>Trying to paint error screen after closing window')
