import base64
import quopri
from selenium import webdriver
from tkinter import *
import threading
import os

import load_screen
import read_mails
import conn_error_screen
import thread_single
import mail_list_screen
import send_mail_screen

elems = []  # Widgets on the root
msgs = []  # list of dictionaries (id, from/to, subject, date) of messages on current page
is_inbox = True  # does the current page is page of inbox messages?
pages = None  # number of available pages for current mailbox
mainlooped = False

driver = None
driver_is_active = False
DISCONNECTED_MSG = 'Unable to evaluate script: disconnected: not connected to DevTools\n'


def clean_root():
    for e in elems:
        if mainlooped:
            if issubclass(type(e), Widget):
                e.grid_forget()  # It's simple widget
            else:
                e[0].unbind(e[1], e[2])  # It's for unbinding
    elems.clear()


def settings(root):
    root.title('Gmail Client')
    root.geometry('800x600')
    root.minsize(800, 600)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    load(root, login)
    # load(root, send_mail)


def load(root, logic, page=None):
    clean_root()
    load_screen.show(root, elems)
    if page is None:
        logic(root)
    else:
        logic(root, page)


def error(root, logic):
    clean_root()
    conn_error_screen.show(root=root, elems=elems, load=load, logic=logic)


def login(root: Tk):
    mail_box = read_mails.login()

    if mail_box is None:
        error(root=root, logic=login)
    else:
        load(root, inbox)


def inbox(root: Tk, page=1):
    global pages
    global msgs
    global is_inbox
    is_inbox = True
    if page == 1:
        pages = read_mails.open_inbox()
    if pages is None:
        error(root=root, logic=inbox)

    else:
        msgs = read_mails.get_page(page)
        clean_root()
        mail_list_screen.show(root=root, elems=elems, is_inbox=is_inbox, msgs=msgs, page=page,
                              pages=pages, inbox=inbox, sent=sent, send_mail=send_mail, open_mail=open_mail, load=load)


def sent(root: Tk, page=1):
    global pages
    global msgs
    global is_inbox
    is_inbox = False
    if page == 1:
        pages = read_mails.open_sent()
    if pages is None:
        error(root=root, logic=sent)

    else:
        msgs = read_mails.get_page(page)
        clean_root()
        mail_list_screen.show(root=root, elems=elems, is_inbox=is_inbox, msgs=msgs, page=page,
                              pages=pages, inbox=inbox, sent=sent, send_mail=send_mail, open_mail=open_mail, load=load)
    pass


def send_mail(root: Tk):
    clean_root()
    send_mail_screen.work(root=root, load=load, sent=sent, elems=elems)


def open_mail(root: Tk, page_num):
    if is_inbox:
        box = '/inbox'
    else:
        box = '/sent'
    if not os.path.exists('messages{}/{}.html'.format(box, page_num[1]['Id: '])):
        mes = read_mails.get_message(page_num[1]['Id: '])
        if mes is None:
            if is_inbox:
                error(root=root, logic=inbox)
            else:
                error(root=root, logic=sent)
        else:
            parse_mail(mes, page_num[1])

    threading.Thread(target=show_mail, args=(page_num[1]['Id: '],)).start()
    # show_mail(page_num[1]['Id: '])
    clean_root()
    mail_list_screen.show(root=root, elems=elems, is_inbox=is_inbox, msgs=msgs, page=page_num[0],
                          pages=pages, inbox=inbox, sent=sent, send_mail=send_mail, open_mail=open_mail, load=load)


def parse_mail(mes, m_head):
    template = ''.join(open('messages/template.txt', 'r').readlines())
    s = template.replace('{mes_num}', str(m_head['Id: '])) \
        .replace('{from}', m_head['From: '].replace('>', '%>%')
                 .replace('<', '<span><</span>').replace('%>%', '<span>></span>')) \
        .replace('{to}', m_head['To: '].replace('>', '%>%')
                 .replace('<', '<span><</span>').replace('%>%', '<span>></span>')) \
        .replace('{date}', m_head['Date: ']) \
        .replace('{subject}', m_head['Subject: '])
    has_attachment = False
    for part in mes.walk():
        if part.get_content_maintype() in ['application', 'image']:
            has_attachment = True
        if part.get_content_maintype() == 'text':
            if part.get_content_subtype() == 'html':
                if part.get('Content-Transfer-Encoding') == 'quoted-printable':
                    s = s.replace('{content}',
                                  quopri.decodestring(part.get_payload())
                                  .decode(part.get_content_charset()) + '{content}')
                elif part.get('Content-Transfer-Encoding') == 'base64':
                    s = s.replace('{content}', str(base64.b64decode(part.get_payload().encode(part.get_content_charset())), part.get_content_charset()) + '{content}')
                else:  # part.get('Content-Transfer-Encoding') is None:
                    s = s.replace('{content}', part.get_payload() + '{content}')

                if has_attachment:
                    s = s.replace('{has_attachment}', 'Имеются приложения')
                else:
                    s = s.replace('{has_attachment}', 'Приложенных файлов нет')
                s = s.replace('{content}', '')

                if is_inbox:
                    box = 'inbox'
                else:
                    box = 'sent'
                file_html = open('messages/{}/{}.html'.format(box, m_head['Id: ']), 'wb')
                file_html.write(s.encode('utf-8'))
                file_html.close()


def show_mail(mes_num):
    if is_inbox:
        box = 'inbox'
    else:
        box = 'sent'
    get_page('file:///C:/Users/User/Desktop/3%20%D0%BA%D1%83%D1%80%D1%81/PR/Lab2/messages/{}/{}.html'.
             format(box, mes_num))


def get_page(url):
    global driver
    global driver_is_active
    if driver_is_active:
        try:
            if driver.get_log('driver')[-1]['message'] == DISCONNECTED_MSG:
                driver = webdriver.Chrome('chromedriver_win32/chromedriver.exe')
                driver_is_active = True
        except:
            pass
    else:
        driver = webdriver.Chrome('chromedriver_win32/chromedriver.exe')
        driver_is_active = True

    driver.get(url)


if __name__ == '__main__':
    r = Tk()

    single = thread_single.Singleton()
    single.thr = threading.Thread(target=settings, args=(r,))
    single.start()
    mainlooped = True
    r.mainloop()
    mainlooped = False

    if single.thr.is_alive():
        single.thr.join()

    if driver is not None:
        driver.quit()

    read_mails.logout()
