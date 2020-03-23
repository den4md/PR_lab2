from tkinter import *
from tkinter import ttk


def show(root: Tk, elems):
    try:
        frame = ttk.Frame(root)
        lbl = ttk.Label(frame, text="Loading...")
        prgrs = ttk.Progressbar(frame, length=300)
        elems.append(frame)
        # elems.append(lbl)
        # elems.append(prgrs)

        frame.grid()
        lbl.grid(column=0, row=0, sticky=S)
        prgrs.grid(column=0, row=1, sticky=N, pady=5)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        prgrs.start()
    except RuntimeError:
        print('>Trying to paint load screen after closing window')
