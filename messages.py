from smtplib import SMTP
import os

USERNAME = os.environ.get('email')
PASSWORD = os.environ.get('password')


class Messages:

    def __init__(self):
        pass

    def send_mail(self, address, message):
        with SMTP('smtp.gmail.com', port=587) as connect:
            connect.starttls()
            connect.login(user=USERNAME, password=PASSWORD)
            connect.sendmail(from_addr=address, to_addrs=USERNAME, msg=message)
