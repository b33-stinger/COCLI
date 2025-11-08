# Imports
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.parse import urljoin, urlparse
import os

# Constants
COLOR_SCALE = [120, 154, 190, 178, 166, 88]
COLOR_BRIGHTNESS = {
    120: 180, 154: 200, 190: 220,
    178: 180, 166: 140, 88: 60
}

# Functions
def format_bytes(size: int) -> str:
    '''
    format bytes to human readable
    '''
    units = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f'{size:.2f} {units[i]}'

def rating_color(rating: int, reverse: bool = False) -> str:
    '''
    turn a rating to a color\n
    1 = Green\n
    6 = Blood Red
    '''
    colors = COLOR_SCALE[::-1] if reverse else COLOR_SCALE
    bg_color = colors[rating - 1]
    brightness = COLOR_BRIGHTNESS[bg_color]
    text_color = 16 if brightness > 127 else 231
    return f'\033[38;5;{text_color}m\033[48;5;{bg_color}m'

def get_biggest(x: int, y: int) -> int:
    '''
    Return is the biggest number from x and y
    '''
    return x if x > y else y

# Classes
class CrackmeManager:
    def __init__(self, requests_session, config_manager):
        self.config = config_manager
        self.requests = requests_session
        self.last_search = {}
        self.zip_pw = ['crackmes.one', 'crackmes.de']

    def _extract_hash(self, download_url: str) -> str:
        '''
        get the crackme's hash by it's url
        '''
        return urlparse(download_url).path.split('/')[-1]

    def get_token(self, url = 'https://crackmes.one/') -> str:
        '''
        Get the CSRF Token of page X
        '''
        req = self.requests.get(url)
        return BeautifulSoup(req.text, 'html.parser').find('input', id='token').get('value', '')
    
    def _parse_search(self, raw_html: str) -> list:
        '''
        Parse the html from crackme search
        '''
        soup = BeautifulSoup(raw_html, 'html.parser')
        crackmes = {
            'found': []
        }
        longest_user = 0
        longest_name = 0
        for tr in soup.find_all('tr', class_='text-center'):
            tds = tr.find_all('td')
            href_0 = tds[0].find('a')['href']
            file_hash = self._extract_hash(href_0)
            username = tds[1].find('a').get_text(strip=True)
            name = tds[0].get_text(strip=True)

            crackme_info = {
                'name': name,
                'url': urljoin(self.config.get('host'), href_0),
                'download_url': urljoin(self.config.get('host'), f'/static/crackme/{file_hash}.zip'),
                'filename': f'{file_hash}.zip',
                'filehash': file_hash,
                'user': username,
                'user_url': tds[1].find('a')['href'],
                'language': tds[2].get_text(strip=True),
                'arch': tds[3].get_text(strip=True),
                'difficulty': max(1.0, min(float(tds[4].get_text(strip=True)), 6.0)), # older crackmes might have > 6 rating
                'quality': max(1.0, min(float(tds[5].get_text(strip=True)), 6.0)), # older crackmes might have > 6 rating
                'os': tds[6].get_text(strip=True),
                'date': tds[7].get_text(strip=True),
                'solutions': int(tds[8].get_text(strip=True)),
                'comments': int(tds[9].get_text(strip=True)),
            }
            longest_user = get_biggest(len(username), longest_user)
            longest_name = get_biggest(len(name), longest_name)

            crackmes['found'].append(Crackme(crackme_info, self))
        crackmes['longest_user'] = longest_user
        crackmes['longest_name'] = longest_name
        return crackmes

    def get_latest(self, page: int = 1) -> dict:
        '''
        Get the latest crackmes from Page page
        '''
        req = self.requests.get(urljoin(self.config.get('latest_base'),  str(page)))
        crackmes = self._parse_search(req.text)
        self.last_search = crackmes
        return crackmes

    def search(self, name: str = '', author: str = '', difficulty_min: int = 1, difficulty_max: int = 6, quality_min: int = 1, quality_max: int = 6, lang: str = None, arch: str = None, platform: str = None) -> dict:
        '''
        Search for a crackme
        '''
        token = self.get_token(self.config.get('host') + 'search')
        payload = {
            'name': name,
            'author': author,
            'difficulty-min': difficulty_min,
            'difficulty-max': difficulty_max,
            'quality-min': quality_min,
            'quality-max': quality_max,
            'token': token
        }
        if lang:
            payload['lang'] = lang
        if arch:
            payload['arch'] = arch
        if platform:
            payload['platform'] = platform
        req = self.requests.post(self.config.get('search'), data=payload)
        crackmes = self._parse_search(req.text)
        self.last_search = crackmes
        return crackmes
    
    def _parse_info(self, raw_html: str, url: str) -> dict:
        '''
        Parse the html from a specific crackme
        '''
        soup = BeautifulSoup(raw_html, 'html.parser')
        container = soup.select_one('.container.grid-lg.wrapper')
        if not container:
            return info

        h3 = container.find('h3')
        name = ''.join(c for c in h3.children if isinstance(c, str)).strip()[3:] if h3 else ''

        target_div = container.select_one('div.columns.panel-background')
        if not target_div:
            return info

        divs = target_div.find_all('div', recursive=False)[:9]
        filtered_divs = [d for i, d in enumerate(divs) if i not in (3, 4)]

        def extract_text(p, remove_a=False):
            if not p:
                return ''
            br = p.find('br')
            if not br:
                return ''
            if remove_a:
                for a in p.find_all('a'):
                    a.decompose()
            return ' '.join(
                sib.get_text(strip=True) if hasattr(sib, 'get_text') else sib.strip()
                for sib in br.next_siblings
                if (sib.strip() if isinstance(sib, str) else True)
            ).strip()

        details = [extract_text(div.find('p'), remove_a=(i == 4)) for i, div in enumerate(filtered_divs)]

        user_div = divs[0]
        user_url = urljoin(self.config.get('host'), user_div.find('a')['href'])
        download_div = divs[4]
        download_url = urljoin(self.config.get('host'), download_div.find('a')['href'])

        filehash = self._extract_hash(download_url)
        info = {
            'url': url,
            'user_url': user_url,
            'name': name,
            'filehash': filehash,
            'filename': filehash + '.zip',
            'download_url': download_url,
            'user': details[0],
            'language': details[1],
            'date': details[2],
            'os': details[3],
            'arch': details[6],
            'difficulty': details[4],
            'quality': details[5]
        }
        return Crackme(info, self)
    
    def get_info(self, url: str) -> 'Crackme':
        '''
        Get information about a specific crackme
        '''
        req = self.requests.get(url)
        return self._parse_info(req.text, url)

    def extract_zip(self, file: str, output_folder: str, passwords: list, embedded=False) -> int:
        '''
        Extract the downloaded crackme zip file
        '''
        print(f'Extracting... {'(Embedded)' if embedded else ''}', end=' ', flush=True)
        for idx, pw in enumerate(passwords):
            try:
                print(f'\ntrying: [ {pw} ] {idx+1}/{len(passwords)} ...', end=' ', flush=True)
                with ZipFile(file) as zf:
                    zf.extractall(path=output_folder, pwd=bytes(pw, 'utf-8'))
                    print('[ OK ]', end=' ', flush=True)
                    names = zf.namelist()
                    print()
                    if len(names) != 1 or not names[0].lower().endswith('.zip'):
                        return 1
                    return self.extract_zip(os.path.join(output_folder, names[0]), output_folder, passwords, True)
            except RuntimeError:
                continue
            except Exception as e:
                print(f'[ ERROR ] {e}')
        print('Failed to extract with provided passwords.')
        return 0

    def download(self, download_url: str, dest_folder: str = 'downloads', name: str = '', filename: str = '', chunk_size: int = 8192, auto_extract: bool = True) -> int:
        '''
        Download crackme
        '''
        chunks_done = 0
        os.makedirs(dest_folder, exist_ok=True)
        local_path = os.path.join(dest_folder, filename)
        with self.requests.get(download_url, stream=True) as req:
            if req.status_code != 200:
                print(f'Failed to download: {req.status_code}')
                return 0
            file_size = int(req.headers.get('Content-length', 0))
            print(f'Downloading {name}: {format_bytes(file_size)}')
            with open(local_path, 'wb') as f:
                for chunk in req.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        chunks_done += len(chunk)
                        percent = (chunks_done * 100) / file_size if file_size else 0
                        print(f'download: [ {percent:.2f}% ]', end='\r')
        print()
        if auto_extract:
            zip_path = os.path.join(dest_folder, filename)
            self.extract_zip(zip_path, dest_folder, self.zip_pw)
        return 1

class Crackme():

    def __init__(self, info: dict, crackme_manager):
        self.name = info.get('name')
        self.url = info.get('url')
        self.download_url = info.get('download_url')
        self.filename = info.get('filename')
        self.filehash = info.get('filehash')
        self.user = info.get('user')
        self.user_url = info.get('user_url')
        self.language = info.get('language')
        self.arch = info.get('arch')
        self.difficulty = float(info.get('difficulty'))
        self.quality = float(info.get('quality'))
        self.os = info.get('os')
        self.date = info.get('date')
        self.solutions = info.get('solutions')
        self.comments = info.get('comments')
        self.manager = crackme_manager
    
    def download(self, dest_folder: str = 'downloads', chunk_size: int = 8192, auto_extract: bool = True) -> int:
        '''
        Download this crackme
        '''
        return self.manager.download(self.download_url, os.path.join(dest_folder, self.user, self.name.replace(' ', '_')), self.name, self.filename, chunk_size, auto_extract)

    def extract(self, passwords: list = [], dest_folder='downloads') -> int:
        '''
        Extract this crackme
        '''
        if not len(passwords):
            passwords = self.zip_pw
        zip_path = os.path.join(dest_folder, self.filename)
        return self.manager.extract_zip(zip_path, dest_folder, passwords)
