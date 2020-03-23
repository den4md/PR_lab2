from tkinter import *
from tkinter import messagebox, ttk, font
import threading
import re

import send_mail
import thread_single
from entry_placeholder import *
from text_placeholder import *


to_placeholder = ' Например: abc@de.com, mail@example.org, ...'
subj_placeholder = ' (Может быть незаполненной)'
text_placeholder = ' Сообщение'


def work(root: Tk, load, sent, elems: list):
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, sticky=(N, W, E, S), padx=10, pady=10)
    elems.append(frame)

    head_frame = ttk.Frame(frame)
    head_frame.pack(fill='x')

    head_left_frame = ttk.Frame(head_frame)
    head_left_frame.pack(side='left', padx=5)

    to_lbl = ttk.Label(head_left_frame, text='Кому:')
    to_lbl.pack(anchor='w')

    from_lbl = ttk.Label(head_left_frame, text="От:")
    from_lbl.pack(pady=10, anchor='w')

    subj_lbl = ttk.Label(head_left_frame, text='Тема:')
    subj_lbl.pack(anchor='w')

    head_right_frame = ttk.Frame(head_frame)
    head_right_frame.pack(fill='x', padx=5)

    to = EntryWithPlaceholder(head_right_frame, placeholder=to_placeholder, elems=elems)
    to.pack(fill='x')

    from_ = ttk.Entry(head_right_frame)
    from_.insert(0, 'denisstarr@gmail.com')
    from_.configure(state='readonly')
    from_.pack(fill='x', pady=10)

    subj = EntryWithPlaceholder(head_right_frame, subj_placeholder, elems=elems)
    subj.pack(fill='x')

    text = TextWithPlaceholder(frame, text_placeholder, elems=elems)
    text.configure(font=font.Font(to_lbl.cget('font')))
    text.pack(fill='both', expand=True, pady=20, padx=5)

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(side='bottom', fill='x', padx=5)

    btn_ok = ttk.Button(btn_frame, text='Отправить',
                        command=lambda: btn_ok_click(to=to, subj=subj, content=text, root=root, load=load, sent=sent))
    btn_ok.pack(side='right')

    btn_cancel = ttk.Button(btn_frame, text='Отменить',
                            command=lambda: btn_cancel_click(root=root, load=load, sent=sent))
    btn_cancel.pack(side='right', padx=10)


def validate_email(email):
    emails = clean_str(email).replace(' ', '').split(',')

    result = ''

    for e in emails:
        r = re.fullmatch(r'^\w+([.-]?\w+)*@\w+([.-]?\w+)$', e)
        if r is None:
            result += '<{}> '.format(e)

    return result


def btn_ok_click(to, subj, content, root: Tk, load, sent):
    v_e = validate_email(email=to.get().replace(to_placeholder, ''))    # non-valid emails str
    if clean_str(to.get().replace(to_placeholder, '')) != '':
        if v_e == '':
            if clean_str(content.get("1.0", 'end-1c').replace(text_placeholder, '')) != '':
                if send_mail.send(to=clean_str(to.get()).replace(' ', '').split(','), subj=clean_str(subj.get()),
                                  content=content.get("1.0", 'end-1c')):
                    messagebox.showinfo('Ok', 'Успешно отправлено')
                    change_screen(root=root, load=load, sent=sent)
                else:
                    messagebox.showerror('Ошибка', 'Ошибка при отправке')
            else:
                messagebox.showerror('Ошибка', 'Сообщение обязательно к заполнению')
        else:
            messagebox.showerror('Ошибка', 'Ошибка при валидации почтовых адресов:\n' + v_e)
    else:
        messagebox.showerror('Ошибка', 'Неободим минимум один почтовый адрес')


def clean_str(s: str):
    my_s = s

    for i in range(2):
        while my_s.__len__() != 0:
            r = re.match(r'^\s', my_s)
            if r is None:
                break
            my_s = my_s[1:]

        my_s = my_s[::-1]
    return my_s


def btn_cancel_click(root: Tk, load, sent):
    if messagebox.askyesno('', 'Вы уверены, что хотите выйти?'):
        change_screen(root=root, load=load, sent=sent)


def change_screen(root: Tk, load, sent):
    single = thread_single.Singleton()
    single.thr = threading.Thread(target=load, args=(root, sent))
    single.start()
