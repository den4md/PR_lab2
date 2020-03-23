from tkinter import *
from tkinter import ttk, font
import thread_single
import threading


def show(root: Tk, elems, msgs, page, pages, inbox, sent, send_mail, open_mail, load, is_inbox):
    try:
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, sticky=(N, W, E, S))
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=9)
        elems.append(frame)

        leftside = ttk.Frame(frame)
        leftside.columnconfigure(0, weight=1)
        leftside.rowconfigure(0, weight=1)
        leftside.grid(row=0, column=0, rowspan=2, sticky=(W, N, E), padx=5, pady=5)

        listbox = Listbox(leftside, height=2, cursor='hand2', listvariable=StringVar(value=('Входящие', 'Исходящие')))
        if is_inbox:
            listbox.selection_set(0)
        else:
            listbox.selection_set(1)
        fid = listbox.bind('<<ListboxSelect>>', lambda *args: change_box(root=root, listbox=listbox, is_inbox=is_inbox,
                                                                         load=load, inbox=inbox, sent=sent))
        listbox.grid(sticky=(N, W, E))
        elems.append((listbox, '<<ListboxSelect>>', fid))

        write = ttk.Button(leftside, text="Написать письмо", cursor='hand2',
                           command=lambda: write_click(load=load, root=root, send=send_mail))
        write.grid(sticky=(N, W, E), pady=10)

        refresh = ttk.Button(leftside, text="Обновить", cursor='hand2',
                             command=lambda: refresh_click(root=root,
                                                           is_inbox=is_inbox,
                                                           load=load,
                                                           inbox=inbox,
                                                           sent=sent))
        refresh.grid(sticky=(N, W, E))

        page_frame = ttk.Frame(frame)
        page_frame.rowconfigure(0, weight=1)
        page_frame.grid(row=0, column=1, sticky=(W, E, N), pady=5)

        pages_list = []
        if page != 1:
            pages_list.append('<<')
            pages_list.append('<')
        for i in range(page - 5, page + 6):
            if (i >= 1) and (i <= pages):
                pages_list.append(str(i))
        if page != pages:
            pages_list.append('>')
            pages_list.append('>>')
        j = 0
        for i in pages_list:
            p = ttk.Label(page_frame, text=i)
            if safe_cast(i) != page:
                f = font.Font(p, p.cget("font"))
                f.configure(underline=True, size=9)
                p.configure(font=f, cursor="hand2", foreground='Blue')
                fid = p.bind('<1>',
                             lambda e: label_click(root=root, is_inbox=is_inbox, load=load, inbox=inbox, sent=sent, e=e,
                                                   page=page, pages=pages))
                elems.append((p, '<1>', fid))
            page_frame.columnconfigure(j, weight=1)
            p.grid(row=0, column=j, padx=2)
            j += 1

        mails = Frame(frame, borderwidth=2)
        mails.columnconfigure(0, weight=1)
        mails.grid(row=1, column=1, padx=5, pady=5, sticky=(W, N, E, S))

        j = 0
        for m in msgs[:-1]:
            mailgrid(is_inbox, j, m, mails, elems, root, load, open_mail, page)

            s = ttk.Separator(mails, orient=HORIZONTAL)
            mails.rowconfigure(2 * j + 1, weight=0)
            s.grid(row=(2 * j + 1), column=0, columnspan=2, sticky=(W, E, N), padx=5, pady=5)

            j += 1

        if msgs:
            mailgrid(is_inbox, j, msgs[-1], mails, elems, root, load, open_mail, page)
    except RuntimeError:
        print('>Trying to paint mail screen after closing window')


def mailgrid(is_inbox, j, m, mails, elems, root, load, open_mail, page):
    try:
        mail = ttk.Frame(mails)
        mails.rowconfigure(2 * j, weight=0)
        mail.columnconfigure(0, weight=1)
        mail.columnconfigure(1, weight=1)
        mail.rowconfigure(0, weight=1)
        mail.rowconfigure(1, weight=1)
        mail.grid(row=(2 * j), column=0, sticky=(W, N, E))
        if is_inbox:
            tofrom = 'От: ' + m['From: ']
        else:
            tofrom = 'Кому: ' + m['To: ']
        to = ttk.Label(mail, text=tofrom)
        to.grid(row=0, column=0, sticky=W, padx=5)
        date = ttk.Label(mail, text=m['Date: '])
        date.grid(row=0, column=1, sticky=E, padx=5)
        subj = ttk.Label(mail, text=m['Subject: '])
        subj.grid(row=1, column=0, columnspan=2, sticky=W, padx=5)

        mail_element = [mail, to, date, subj]
        for m_e in mail_element:
            m_e.configure(cursor="hand2")
            fid = m_e.bind('<1>', lambda elem: mail_open(lambda: load(root, open_mail, (page, m))))
            elems.append((m_e, '<1>', fid))
    except TclError as e:
        print('>Something wrong with mail\r\n\t' + str(e))


def safe_cast(val, default=None):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def label_click(root, is_inbox, load, inbox, sent, e, page, pages):
    single = thread_single.Singleton()

    p = e.widget.cget('text')

    p = {
        '<<': 1,
        '<': page - 10,
        '>': page + 10,
        '>>': pages
    }.get(p, safe_cast(p))

    if p < 1:
        p = 1
    if p > pages:
        p = pages

    if is_inbox:
        single.thr = threading.Thread(target=load, args=(root, inbox, p))
    else:
        single.thr = threading.Thread(target=load, args=(root, sent, p))
    single.start()


def write_click(root, load, send):
    single = thread_single.Singleton()
    single.thr = threading.Thread(target=load, args=(root, send))
    single.start()


def refresh_click(root, is_inbox, load, inbox, sent):
    single = thread_single.Singleton()
    if is_inbox:
        single.thr = threading.Thread(target=load, args=(root, inbox))
    else:
        single.thr = threading.Thread(target=load, args=(root, sent))
    single.start()


def change_box(root, listbox, is_inbox, load, inbox, sent):
    a = listbox.curselection()
    if len(a) == 0:
        return
    if {
        0: True,
        1: False
    }.get(a[0], is_inbox) == is_inbox:
        return
    single = thread_single.Singleton()
    if is_inbox:
        single.thr = threading.Thread(target=load, args=(root, sent))
    else:
        single.thr = threading.Thread(target=load, args=(root, inbox))
    single.start()


def mail_open(lmbd):
    single = thread_single.Singleton()
    single.thr = threading.Thread(target=lmbd)
    single.start()
