#!/bin/env python3
class Acc():

    def __init__(self, crackmes = None, requests_session = None):
        self.crackmes = crackmes                 # Set ASAP | crackmes instance
        self.requests_session = requests_session # Set ASAP | requests instance
        self.logged_in = False
    
    def login(self, username: str, password: str) -> int:
        '''
        Login -> username + password -> 0 Something went Wrong, 1 Ok
        '''
        print('Logging in...', end=' ', flush=True)
        token = self.crackmes.get_token('https://crackmes.one/login')
        payload = {
            'name': username,
            'password': password,
            'token': token
        }
        req = self.requests_session.post('https://crackmes.one/login', data=payload)
        if 'Password is incorrect' in req.text and self.check_login():
            print('Username or Password is wrong')
            return 0
        if 'Login successful!' in req.text:
            print('[ OK ]')
            return 1
        return 0
    
    def logout(self) -> int:
        '''
        Logout -> 1 logged out, 0 something went wrong
        '''
        print('Logging out...', end=' ', flush=True)
        req = self.requests_session.get('https://crackmes.one/logout')
        if 'Goodbye!' in req.text or not self.check_login():
            print('[ OK ]')
            return 1
        print('[ Something went wrong ]')
        return 0
    
    def check_login(self) -> int:
        '''
        Will be used in later updates\n
        Check if you're really logged in
        '''
        req = self.requests_session.get('https://crackmes.one/upload/crackme')
        if 'Please provide details in the infos section. You can upload just the executable or an archive containing needed resources.' in req.text:
            return 1
        return 0
