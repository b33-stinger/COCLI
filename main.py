#!/bin/env python3
from requests import Session
from os.path import exists as os_path_exists, splitext as os_path_splitext
from os import makedirs as os_mkdirs, remove as os_remove
from urllib.parse import urljoin, urlparse
from shutil import get_terminal_size
from gc import collect as gc_collect # Just to be sure

from data.terminal import Terminal
from data.crackme import Crackmes
from data.account import Acc


# Globals
__version__ = "0.1.0-alpha"
requests = Session()
requests.headers = {
    "User-Agent": "COCLI/5.0 (X11; Python3 x86_64; rv:0.1.0) COCLI/0.1.0",
    "Content-Type": "application/x-www-form-urlencoded"
}
COMMANDS = ['download', 'search', 'login', 'exit', 'help']
COMMANDS_DETAIL = {
        'download': ['url', 'hash', 'search_id', 'download_folder', 'auto_extract', 'extract_folder'],
        'search': ["name", "author", "difficulty_min", "difficulty_max", "quality_min", "quality_max"],
        'login': ['username', 'password'],
        'exit': [],
        'help': []
}
# Don't save said command in history
history_ignore = ["login"]

acc = Acc(requests_session=requests)
crackmes = Crackmes(account=acc, requests_session=requests)
acc.crackmes = crackmes


def space(size: int) -> str: return " " * size


if __name__ == "__main__":
    print(f"Welcome to\n\033[31mC\033[mrackmes\n\033[31mO\033[0mne\n\033[31mC\033[0mommand\n\033[31mL\033[0mine\n\033[31mI\033[0mnterface\n{__version__}")
    print("type help for help")
    width = get_terminal_size().columns
    term = Terminal(commands=COMMANDS, args_info=COMMANDS_DETAIL, prompt="[ Anon ] # COCLI > ", history_ignore = history_ignore)

    while True:
        line = term.run()
        cmd, args = term.parse_command(line)

        term.clear_previous_hint()
        # If you comment this out the line with the command will be cleared, needs fix maybe
        print('\n')

        match cmd:
            case 'exit':
                print("Goodbye!")
                break

            case 'download':
                url = args.get('url')
                challenge_hash = args.get('hash')
                search_id = args.get('search_id')
                if not url and not challenge_hash and not search_id:
                    print("You need atleast 1 download option!!")
                    continue
                auto_extract = args.get('auto_extract', True)
                auto_extract = str(auto_extract).lower() in ['1', 'true', 'yes']
                if url:
                    download_url = url
                    filehash = urlparse(url).path.rstrip('/').split('/')[-1]
                    zip_file = filehash
                    crackme_page = "https://crackmes.one/crackme/" + os_path_splitext(filehash)[0]
                elif challenge_hash:
                    download_url = urljoin(crackmes.host, f"/static/crackme/{challenge_hash}") + ".zip"
                    zip_file = challenge_hash + '.zip'
                    crackme_page = "https://crackmes.one/crackme/" + challenge_hash
                elif search_id:
                    download_url = crackmes.last_search["crackmes"][int(search_id)]["download_url"]
                    zip_file = crackmes.last_search["crackmes"][int(search_id)]["filename"]
                    crackme_page = "https://crackmes.one/crackme/" + crackmes.last_search["crackmes"][int(search_id)]["filehash"]
                info = crackmes.get_info(crackme_page)
                output_folder = info["user"] + '/' + info["name"].replace(' ', "_")
                output = args.get('download_folder', 'downloads/' + output_folder) + '/'
                if not os_path_exists(output):
                    os_mkdirs(output)
                download_status = crackmes.download(url=download_url, path=output + zip_file)
                if not download_status:
                    os_remove(output)
                if auto_extract:
                    crackmes.extract_zip(output, output + zip_file)

            case 'search':
                found = crackmes.search(
                    args.get("name", ""),
                    args.get("author", ""),
                    difficulty_min=int(args.get("difficulty_min", 1)),
                    difficulty_max=int(args.get("difficulty_max", 6)),
                    quality_min=int(args.get("quality_min", 1)),
                    quality_max=int(args.get("quality_max", 6))
                )
                i = 0
                print(f"{space(5 - len(str(i)))} Username{space(found["longest_user"]+3 - len("Username"))} Name{space(found['longest_name']+2 - len("Name"))} Difficulty{space(8)}Quality{space(11)}Hash".ljust(width))
                for x in found["crackmes"]:
                    if i % 2 == 0:
                        color = "\033[0m"
                    else:
                        color = "\033[48;2;139;8;8m" if (i // 2) % 2 == 0 else "\033[48;2;64;0;64m"

                    dif_calc, qul_calc = int((x["difficulty"] / 6) * 16), int((x["quality"] / 6) * 16)
                    dif, qul = ['#'] * dif_calc + [' '] * (16 - dif_calc), ['#'] * qul_calc + [' '] * (16 - qul_calc)
                    dif[6:10], qul[6:10] = list(str(x['difficulty'])), list(str(x['quality']))
                    dif_color = crackmes.rating_color(int(x["difficulty"]))
                    qul_color = crackmes.rating_color(int(x["quality"]), True)
                    # TODO: Emojis are not parsed as 1 character, duh, but messes up spacing
                    print(color + f"#{i}{space(3 - len(str(i)))} {x["user"]}{space(found["longest_user"]+1 - len(x["user"]))}-> {x["name"]}{space(found['longest_name'] - len(x['name']))} [{dif_color}{''.join(dif)}\033[0m] [{qul_color}{''.join(qul)}\033[0m]{color} {x['filehash']}".ljust(width) + "\033[0m")
                    i += 1

            case 'login':
                if acc.logged_in:
                    print("You're already logged in. use 'logout' to logout first")
                    continue
                name = args.get('username')
                pw = args.get('password')
                if not name:
                    print("No username given")
                    continue
                if not pw:
                    print("No password given")
                    continue
                logged_in = acc.login(name, pw)
                acc.logged_in = logged_in
                if logged_in:
                    term.prompt = f"[ {name} ] # COCLI > "
                del pw # Delete from RAM
            
            case 'help':
                print("Commands:", ', '.join(COMMANDS))
                print("Use arguments as key=value, e.g. search author=John name=CrackMe")

            case '':
                pass

            case _:
                print(f"Unknown command: {cmd}")

        gc_collect()