#!/bin/env python3
from requests import Session
from urllib.parse import urljoin
from shutil import get_terminal_size
#from argparse import ArgumentParser

from data.terminal import Terminal
from data.crackme import CrackmeManager, rating_color
from data.account import Acc


# Globals
__version__ = '0.2.0-alpha'
requests = Session()
requests.headers = {
    'User-Agent': 'COCLI/5.0 (X11; Python3 x86_64; rv:0.2.0) COCLI/0.2.0',
    'Content-Type': 'application/x-www-form-urlencoded'
}
COMMANDS = [
    {
        'name': 'download',
        'desc': 'Download crackme',
        'args': {
            'all': {'type': 'flag', 'desc': 'Download all crackmes from last search'},
            'url': {'type': 'value', 'desc': 'crackme download URL'},
            'hash': {'type': 'value', 'desc': 'crackme Hash'},
            'search_id': {'type': 'value', 'desc': 'ID from last search'},
            'download_folder': {'type': 'value', 'desc': 'Folder to save downloads'},
            'auto_extract': {'type': 'flag', 'desc': 'Automatically extract archives'},
            'extract_folder': {'type': 'value', 'desc': 'Folder to extract files into'},
        },
    },
    {
        'name': 'search',
        'desc': 'search for crackmes',
        'args': {
            'name': {'type': 'value', 'desc': 'Name of the crackme'},
            'author': {'type': 'value', 'desc': 'Author of the crackme'},
            'difficulty_min': {'type': 'value', 'desc': 'Minimum difficulty'},
            'difficulty_max': {'type': 'value', 'desc': 'Maximum difficulty'},
            'quality_min': {'type': 'value', 'desc': 'Minimum quality'},
            'quality_max': {'type': 'value', 'desc': 'Maximum quality'},
        },
    },
    {
        'name': 'login',
        'desc': 'Log into your account',
        'args': {
            'username': {'type': 'value', 'desc': 'Your username'},
            'password': {'type': 'value', 'desc': 'Your password'},
        },
    },
    {
        'name': 'logout',
        'desc': 'Logout of your account',
        'args': {}
    },
    {
        'name': 'help',
        'desc': 'Show all commands',
        'args': {}
    },
    {
        'name': 'exit',
        'desc': 'Exit the program',
        'args': {},
    },
]

# Don't save said command in history
history_ignore = ['login']

acc = Acc(requests_session=requests)
crackmes = CrackmeManager(requests)
acc.crackmes = crackmes


# Classes
class Helper():
    '''
    don't use as instance
    '''
    # Argument's will be implemented next update
    #def init_arguments() -> any:
    #    parser = ArgumentParser(description=f'COCLI {__version__}')
    #    return parser.parse_args()

    def generate_terminal_prompt(text: str = "[ USERNAME_PAYLOAD ] # COCLI >", username: str = "Anon") -> str:
        '''
        Generate the prompt for the terminal
        '''
        return text.replace("USERNAME_PAYLOAD", username)

    def _add_centered_text(text: str, payload: str) -> str:
        '''
        inject playoad (str) in the middle of text
        '''
        text_list = list(text)
        payload_list = list(payload)
        payload_start = int((len(text) / 2 ) - 2)
        payload_end = int(((len(text) / 2) - 1) + len(payload))
        text_list[payload_start:payload_end] = payload_list
        return ''.join(text_list)

    def download(search_id: int = None, download_url: str = None, challenge_hash: str = None, auto_extract: bool = True) -> int:
        '''
        Download crackme
        '''
        if search_id != None:
            return crackmes.last_search['found'][int(search_id)].download(auto_extract=auto_extract)
        elif url != None:
            crackme_page = urljoin('https://crackmes.one/crackme/', crackmes._extract_hash(download_url))
        elif challenge_hash != None:
            crackme_page = urljoin('https://crackmes.one/crackme/', challenge_hash)
        
        crackme_instance = crackmes.get_info(crackme_page)
        download_status = crackme_instance.download()

        return download_status
    
    def crackme_display(crackme_id: int, user: str, name: str, difficulty: float, quality: float, filehash: str, longest_user: int, longest_name: int) -> str:
        '''
        Generate UI for Crackme
        '''
        if not crackme_id or crackme_id % 2 == 0:
            color = '\033[0m'
        else:
            color = '\033[48;2;139;8;8m' if (crackme_id // 2) % 2 == 0 else '\033[48;2;64;0;64m'

        dif_calc, qul_calc = int((difficulty / 6) * 16), int((quality / 6) * 16)
        dif, qul = Helper._add_centered_text('#' * dif_calc + ' ' * (16 - dif_calc), str(difficulty)), Helper._add_centered_text('#' * qul_calc + ' ' * (16 - qul_calc), str(quality))
        dif_color = rating_color(int(difficulty))
        qul_color = rating_color(int(quality), True)
        # TODO: Emojis are not parsed as 1 character, duh, but messes up spacing
        return color + f'#{crackme_id}{space(3 - len(str(crackme_id)))} {user}{space(longest_user+1 - len(user))}-> {name}{space(longest_name - len(name))} [{dif_color}{''.join(dif)}\033[0m] [{qul_color}{''.join(qul)}\033[0m]{color} {filehash}'.ljust(width) + '\033[0m'
    
    def login(username: str, password: str) -> int:
        '''
        Login to your crackmes account
        '''
        if acc.logged_in:
            print('You\'re already logged in. use \'logout\' to logout first')
            return 1
        
        if not username:
            print('No username given')
            return 0
        
        if not password:
            print('No password given')
            return 0
        
        logged_in = acc.login(username, password)
        acc.logged_in = logged_in
        if logged_in:
            term.prompt = Helper.generate_terminal_prompt(username=username)
        return logged_in
    
    def logout() -> int:
        '''
        Logout from your crackmes account
        '''
        acc.logged_in = acc.check_login()
        if not acc.logged_in:
            print('Already not logged in')
            return 1
        term.prompt = Helper.generate_terminal_prompt()
        return acc.logout()


def space(size: int) -> str: return ' ' * size


if __name__ == '__main__':
    print(f'Welcome to\n\033[31mC\033[mrackmes\n\033[31mO\033[0mne\n\033[31mC\033[0mommand\n\033[31mL\033[0mine\n\033[31mI\033[0mnterface\n{__version__}')
    print('type help for help')
    width = get_terminal_size().columns
    term = Terminal(commands=COMMANDS, prompt=Helper.generate_terminal_prompt(), history_ignore = history_ignore)

    while True:
        line = term.run()
        cmd, args = term.parse_command(line)

        term.clear_previous_hint()
        # If you comment this out the line with the command will be cleared, needs fix maybe
        print('\n')

        match cmd:
            case 'exit':
                print('Goodbye!')
                break

            case 'download':
                url = args.get('url')
                challenge_hash = args.get('hash')
                search_id = args.get('search_id')
                auto_extract = args.get('auto_extract', True)
                auto_extract = str(auto_extract).lower() in ['1', 'true', 'yes']
                if 'all' in args:
                    for i in range(len(crackmes.last_search['found'])):
                        Helper.download(i, None, None)
                    continue
                Helper.download(search_id, url, challenge_hash)
                
            case 'search':
                found = crackmes.search(
                    args.get('name', ''),
                    args.get('author', ''),
                    difficulty_min=int(args.get('difficulty_min', 1)),
                    difficulty_max=int(args.get('difficulty_max', 6)),
                    quality_min=int(args.get('quality_min', 1)),
                    quality_max=int(args.get('quality_max', 6))
                )
                i = 0
                print(f'{space(5 - len(str(i)))} Username{space(found['longest_user']+3 - len('Username'))} Name{space(found['longest_name']+1 - len('Name'))} Difficulty{space(8)}Quality{space(10)}Hash'.ljust(width))
                for x in found['found']:
                    print(Helper.crackme_display(i, x.user, x.name, x.difficulty, x.quality, x.filehash, found['longest_user'], found['longest_name']))
                    i += 1

            case 'login':
                name = args.get('username')
                pw = args.get('password')
                Helper.login(name, pw)

            case 'logout':
                Helper.logout()

            case 'help':
                print('Commands:', ', '.join(x['name'] for x in COMMANDS))
                print('Use arguments as key=value, e.g. search author=John name=CrackMe')

            case '':
                pass

            case _:
                print(f'Unknown command: {cmd}')