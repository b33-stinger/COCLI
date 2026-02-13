## crackmes.one CLI 0.4.0-alpha

A lightweight and user-friendly CLI client for crackmes.one. You can login, query crackmes and download them. Built for researchers and CTF players that want fast and easy access to crackmes.one

### Download
```bash
git clone https://github.com/b33-stinger/COCLI.git
cd COCLI
chmod +x main.py
```

### Install
pip
```
pip install requests
```
yay
```
yay -S python-requests --needed
```


#### TODO
- [x] config manager
- [ ] extract with command
- [x] logout
- [x] better commands descriptions
- [x] sys arguments
- [ ] add pathlib for path sanitization
- [ ] cache system
- [x] better help
- [ ] Rust version


#### Changelog
```
0.4.0-alpha
[+] get Download count
[+] get File size (before downloading)
[+] handle new website layout/api

0.3.0-alpha
[+] get latest crackmes
[+] history command
[+] config manager
[+] moved commands to commands.py
[+] added sys args
[+] added some error handling
[+] login with saved cookies

0.2.0-alpha
[+] 'download all' command
[+] more OOP based code
[+] Logout command
[+] better commands descriptions

0.1.0-alpha
Basic functionallity
```