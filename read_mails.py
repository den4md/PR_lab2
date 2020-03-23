from dateutil.parser import parse as parse_datetime
from imaplib import IMAP4_SSL
import email
import keyring
import base64
import quopri
import math


sent = '[Gmail]/&BB4EQgQ,BEAEMAQyBDsENQQ9BD0ESwQ1-'
inbox = 'INBOX'
mail_box = None
num_of_mails = 0    # Total mails in current mailbox
N = 10  # Mails on page


def login():
    try:
        global mail_box
        mail_box = IMAP4_SSL('imap.gmail.com', 993)
        mail_box.login('denisstarr@gmail.com', keyring.get_password('gmail', 'denisstarr@gmail.com'))
    except Exception as e:
        print('>Logging in failed\r\n\t' + e.__str__())
        return None
    else:
        print('>Logged in')
        return mail_box


def logout():
    try:
        if mail_box is not None:
            mail_box.logout()
            print('>Logged out')
    except Exception as e:
        print('>Logging out failed\r\n\t' + e.__str__())


def open_box(boxname: str):
    try:
        global num_of_mails
        typ, num_of_mails = mail_box.select(boxname)
        if typ != 'OK':
            raise Exception('Access to ' + boxname + ' denied')
        num_of_mails = int(num_of_mails[0].decode('utf-8'))

    except Exception as e:
        print('>Opening ' + boxname + ' failed\r\n\t' + e.__str__())
        return None
    else:
        print('>Opened ' + boxname + ' (Refreshed)')
        return int(math.ceil(num_of_mails / N))


def open_inbox():   # Opens inbox & returns number of pages
    return open_box(boxname=inbox)


def open_sent():    # Opens sent & returns number of pages
    return open_box(boxname=sent)


def get_page(i: int):
    mesges = []
    try:
        for j in range(1 + (i-1)*N, min(i*N, num_of_mails)+1):
            mes_id = num_of_mails - j + 1
            typ, mes = mail_box.fetch(bytearray(str(mes_id), 'utf-8'), '(BODY.PEEK[HEADER.FIELDS (DATE '
                                                                       'FROM TO SUBJECT)])')
            # '(RFC822)' -> '(BODY.PEEK[HEADER.FIELDS (DATE FROM TO SUBJECT)])'
            if typ == 'OK':
                a = str(mes[0][1], 'utf-8').split('\r\n')
                last_head = None
                head = {'Date: ': '', 'From: ': '', 'To: ': '', 'Subject: ': ''}
                for k in a:
                    if k != '':
                        y_flag = False
                        for h in head:
                            if k.lower().find(h.lower()) == 0:
                                last_head = h
                                y_flag = True
                                head[h] += k[k.find(':')+2:]
                                break
                        if not y_flag:
                            head[last_head] += '\r\n' + k
                if head['Subject: '] == '':
                    head['Subject: '] = '(без темы)'
                head['Date: '] = parse_datetime(head['Date: ']).strftime('%d-%b-%Y, %H:%M')
                for h in head:
                    if has_encode(head[h]):
                        pr = head[h].split('\r\n')
                        head[h] = ''
                        for p in pr:
                            if has_encode(p):
                                head[h] += decode_header(p)

                    range_correct(h, head)
                head['Id: '] = mes_id
                mesges.append(head)
            else:
                raise Exception('Internet is Ok, failed in fetch()')
    except Exception as e:
        print('>Getting page №' + str(i) + ' failed\r\n\t' + e.__str__())
        return None
    else:
        print('>Got page №' + str(i))
    finally:
        return mesges


def get_message(msg_id):
    try:
        typ, msg = mail_box.fetch(bytearray(str(msg_id), 'utf-8'), '(RFC822)')
        if typ != 'OK':
            raise Exception('Internet is Ok, failed in fetch()')
        msg = email.message_from_bytes(msg[0][1])
    except Exception as e:
        print('>Getting mail №' + str(msg_id) + ' failed\r\n\t' + e.__str__())
        return None
    else:
        print('>Got mail №' + str(msg_id))
        return msg


def range_correct(h, head):
    char_list = [head[h][i] for i in range(len(head[h])) if ord(head[h][i]) in range(65536)]
    normalstr = ''
    for k in char_list:
        normalstr = normalstr + k
    head[h] = normalstr


def has_encode(s: str):
    return (s.lower().find('utf-8') != -1) | (s.lower().find('koi8-r') != -1)


def decode_header(p):
    p_arr = p.split('?')
    enc = p_arr[1].lower()
    if p_arr[2].lower() == 'b':
        s = str(base64.b64decode(p_arr[3].encode(enc)), enc) \
                   + p.split('=')[-1]
    else:
        s = quopri.decodestring(p_arr[3]).decode(enc) \
                   + p.split('=')[-1]
    return clean_str(s)


def clean_str(s):
    my_s = s
    while my_s[0] in ['\r', '\t', '\n', ' ']:
        my_s = my_s[1:]
    while my_s[-1] in ['\r', '\t', '\n', ' ']:
        my_s = my_s[:-1]
    return my_s
