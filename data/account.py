#!/bin/env python3
from html import escape as html_escape


class Acc():

    def __init__(self, crackmes = None, requests_session = None):
        self.crackmes = crackmes                 # Set ASAP | crackmes instance
        self.requests_session = requests_session # Set ASAP | requests instance
        self.logged_in = False
    
    def login(self, username: str, password: str) -> int:
        """
        Login -> username + password -> 0 Something went Wrong, 1 Ok
        """
        print("Logging in...", end=' ', flush=True)
        token = self.crackmes.get_token("https://crackmes.one/login")
        payload = f"name={username}&password={html_escape(password)}&token={token}"
        req = self.requests_session.post("https://crackmes.one/login", data=payload)
        if "Password is incorrect" in req.text:
            print("Username or Password is wrong")
            return 0
        if "Login successful!" in req.text:
            print("[ OK ]")
            return 1
        return 0
    
    def check_login(self) -> int:
        """
        Will be used in later updates\n
        Check if you're really logged in
        """
        req = self.requests_session.get("https://crackmes.one/upload/crackme")
        if "Please provide details in the infos section. You can upload just the executable or an archive containing needed resources." in req.text:
            return 1
        return 0
