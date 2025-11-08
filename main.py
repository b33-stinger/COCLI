#!/usr/bin/env python3
from requests import Session
from urllib.parse import urljoin
from shutil import get_terminal_size
from argparse import ArgumentParser

from data.terminal import Terminal
from data.crackme import CrackmeManager, rating_color, get_biggest
from data.account import Acc
from data.config import ConfigManager
from data.commands import COMMANDS


# Classes
class Helper():
    '''
    don't use as instance
    '''
    def init_arguments() -> any:
        parser = ArgumentParser(description=f'COCLI {__version__}')

        parser.add_argument('-d', '--download', type=str, nargs='+', help='download crackme\n hash=HASH\n url=Download-URL')
        parser.add_argument('-a', '--auto-extract', action='store_true', help='automatically extract downloaded crackmes')
        parser.add_argument('-s', '--search', type=str, nargs='+', help='search for crackmes name=Crackme-Name author=Crackme-author difficulty_max=Max-difficulty\
             difficulty_min=Min-difficulty quality_max=Max-quality quality_min=Min-quality')
        parser.add_argument('-l', '--latest', type=str, nargs='+', help='get the latest crackmes page=Page all=(is flag)')
        parser.add_argument('-i', '--history', type=str, nargs='+', help='manage your history ignore=Command,Command2 unignore=Command,Command2 nuke=(is flag)')
        parser.add_argument('-c', '--continue', action='store_true', help='spawn shell after finishing')

        return parser.parse_args()

    def generate_terminal_prompt(text: str = '[ USERNAME_PAYLOAD ] # COCLI >', username: str = 'Anon') -> str:
        '''
        Generate the prompt for the terminal
        '''
        return text.replace('USERNAME_PAYLOAD', username)

    def _add_centered_text(text: str, payload: str) -> str:
        '''
        inject playoad (str) in the middle of text
        '''
        mid = len(text) // 2
        return text[:mid] + payload + text[mid:]


    def download(search_id: int = None, download_url: str = None, challenge_hash: str = None, auto_extract: bool = True) -> int:
        '''
        Download crackme
        '''
        if search_id != None:
            return crackmes.last_search['found'][int(search_id)].download(auto_extract=auto_extract)
        elif download_url != None:
            crackme_page = urljoin(config.get('crackme_base'), crackmes._extract_hash(download_url))
        elif challenge_hash != None:
            crackme_page = urljoin(config.get('crackme_base'), challenge_hash)
        else:
            print('atleast 1 option is required')
            return 0
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
    
    def login(use_cookie: bool, username: str, password: str, save: bool = False) -> int:
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
        
        logged_in = acc.login(use_cookie, username, password, save)
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


# Globals
__version__ = '0.3.0-alpha'
requests = Session()
requests.headers = {
    'User-Agent': f'COCLI/5.0 (X11; Python3 x86_64; rv:0.3.0) COCLI/{__version__}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

config = ConfigManager('data/config.json')
acc = Acc(requests_session=requests, config_manager=config)
crackmes = CrackmeManager(requests, config)
acc.crackmes = crackmes

# Don't save said command in history
history_ignore = config.get('history_ignore', [])

width = get_terminal_size().columns
term = Terminal(commands=COMMANDS, prompt=Helper.generate_terminal_prompt(), history_ignore = history_ignore)


def space(size: int) -> str: return ' ' * size

def handle_command(cmd: str, args: dict) -> int:
    match cmd:
        case 'exit':
            print('Goodbye!')
            exit()

        case 'download':
            url = args.get('url', '')
            challenge_hash = args.get('hash', '')
            search_id = args.get('search_id', '')
            auto_extract = args.get('auto_extract', True)
            auto_extract = str(auto_extract).lower() in ['1', 'true', 'yes']
            if 'all' in args:
                for i in range(len(crackmes.last_search['found'])):
                    Helper.download(i, None, None)
                return
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
            print(f'{space(5 - len(str(i)))} Username{space(found['longest_user']+3 - len('Username'))} Name{space(found['longest_name']+1 - len('Name'))} Difficulty{space(12)}Quality{space(14)}Hash'.ljust(width))
            for x in found['found']:
                print(Helper.crackme_display(i, x.user, x.name, x.difficulty, x.quality, x.filehash, found['longest_user'], found['longest_name']))
                i += 1

        case 'latest':
            get_all = args.get('all', False)
            page = int(args.get('page', 1))
            found = {
                'longest_user': 0,
                'longest_name': 0,
                'found': []
            }
            if get_all:
                cur = page
                while True:
                    print(f'Getting page {cur}', end='\r')
                    tmp = crackmes.get_latest(cur)
                    if tmp['found'] == []:
                        break
                    found.setdefault('found', []).extend(tmp['found'])
                    found['longest_name'] = get_biggest(found['longest_name'], tmp['longest_name'])
                    found['longest_user'] = get_biggest(found['longest_user'], tmp['longest_user'])
                    cur += 1
                crackmes.last_search = found
            else:
                found = crackmes.get_latest(page)
            i = 0
            print(f'{space(5 - len(str(i)))} Username{space(found['longest_user']+3 - len('Username'))} Name{space(found['longest_name']+1 - len('Name'))} Difficulty{space(12)}Quality{space(14)}Hash'.ljust(width))
            for x in found['found']:
                print(Helper.crackme_display(i, x.user, x.name, x.difficulty, x.quality, x.filehash, found['longest_user'], found['longest_name']))
                i += 1

        case 'login':
            use_cookie = args.get('use_cookie')
            name = args.get('username')
            pw = args.get('password')
            save = args.get('save_session')
            #save = 
            Helper.login(use_cookie, name, pw, save)

        case 'logout':
            Helper.logout()

        case 'history':
            nuke = args.get('nuke', True)
            nuke = str(nuke).lower() in ['1', 'true', 'yes']
            if nuke:
                term.history = []
                term.history_file(3, '')
                
            unignore = args.get('unignore', '')
            if unignore:
                term.history_ignore = [x for x in term.history_ignore if x not in unignore]
                    
            ignore = args.get('ignore', '')
            if ignore:
                term.history_ignore.extend(ignore.split(','))
                
            config.update('history_ignore', term.history_ignore)
            config.save_config()

        case 'help':
            print('Commands:', ', '.join(x['name'] for x in COMMANDS))
            print('Use arguments as key=value, e.g. search author=John name=CrackMe')

        case '':
            pass

        case _:
            print(f'Unknown command: {cmd}')
    return 1

def main() -> int:
    print(f'Welcome to\n\033[31mC\033[mrackmes\n\033[31mO\033[0mne\n\033[31mC\033[0mommand\n\033[31mL\033[0mine\n\033[31mI\033[0mnterface\n{__version__}')
    print('type help for help')

    while True:
        line = term.run()
        cmd, args = term.parse_command(line)

        term.clear_previous_hint()
        # If you comment this out the line with the command will be cleared, needs fix maybe
        print('\n')

        handle_command(cmd, args)

    return 1

if __name__ == '__main__':
    args_raw = vars(Helper.init_arguments())
    args = {
        k: (
            {item.split('=', 1)[0]: item.split('=', 1)[1] if '=' in item else True for item in v} if isinstance(v, list)
            else {item.split('=', 1)[0]: item.split('=', 1)[1] for item in v.split()} if isinstance(v, str) and '=' in v
            else v
        )
        for k, v in args_raw.items()
    }
    for command, arguments in args.items():
        if command in ['continue', 'auto_extract', 'nuke'] or arguments == None:
            continue
        handle_command(command, arguments)

    if args['continue']:
        main()