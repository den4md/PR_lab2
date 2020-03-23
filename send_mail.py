import yagmail
import keyring


def send(to: list, subj: str, content: str) -> bool:
    try:
        yag = yagmail.SMTP('denisstarr@gmail.com', keyring.get_password('gmail', 'denisstarr@gmail.com'))
        yag.send(to=to, subject=subj, contents=content)
    except Exception as e:
        print('>Some problem with sending mail\n' + e.__str__())
        return False
    else:
        print('>Mail sent succesful')
        return True
