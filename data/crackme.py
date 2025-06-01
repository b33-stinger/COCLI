#!/bin/python3
# Imports
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.parse import urljoin
from io import BytesIO

COLOR_SCALE = [120, 154, 190, 178, 166, 88]
COLOR_BRIGHTNESS = {
    120: 180,  # light green
    154: 200,  # lime green
    190: 220,  # yellowish green
    178: 180,  # orange-yellow
    166: 140,  # red-orange
     88:  60,    # dark red
}

class Crackmes():

    def __init__(self, account = None, requests_session = None):
        self.host = "https://crackmes.one/"             # Will be used more often once config manager is finished
        self.zip_pass = ["crackmes.one", "crackmes.de"] # Passwords or the crackmes zip
        self.requests_session = requests_session        # Set ASAP | Requests Instance
        self.acc = account                              # Set ASAP | Account Instance
        self.last_search = {}                           # Save results of last search
        self.download_chunk = 8192                      # Chunk of bytes to download
        self.downloads_folder = "downloads"             # Where the Crackmes are downloaded at
        pass

    def _format_bytes(self, bytes: int) -> str:
        """
        Format bytes sizes
        """
        byte_types = [
            "Bytes",
            "KB",
            "MB",
            "GB", # Unrealistic
            "TB", # Very Unrealistic
            "PB"  # Very Very Unrealistic
        ]
        byte_type = 0
        max_type = len(byte_types)
        while bytes >= 1024:
            byte_type += 1
            bytes /= 1024
            if byte_type >= max_type:
                byte_type = max_type
                break
        return f"{bytes:.2f} {byte_types[byte_type]}"

    def get_token(self, url: str = "https://crackmes.one/") -> str:
        """
        Get the CSRF Token from page X
        """
        req = self.requests_session.get(url)
        return BeautifulSoup(req.text, 'html.parser').find('input', id="token").get('value')
    
    def extract_zip(self, output_folder: str, file: str, embedded: bool = False) -> int:
        """
        Extract the downloaded zip, also extract embedded zip
        """
        print(f'Extracting... {"(Embedded)" if embedded else ""}', end=' ', flush=True)
        pw_try = 0
        for pw in self.zip_pass:
            pw_try += 1
            try:
                print(f'\ntrying: [ {pw} ] {pw_try}/{len(self.zip_pass)} ...', end=' ', flush=True)
                with ZipFile(file) as outer_zip:
                    outer_zip.extractall(path=output_folder, pwd=bytes(pw, 'utf-8'))
                    print('[ OK ]', end=' ', flush=True)
                    names = outer_zip.namelist()
                    print()
                    # If file.zip -> embedded.zip, then embedded.zip -> files
                    if len(names) == 1 and not names[0].lower().endswith('.zip'):
                        return 1
                    return self.extract_zip(output_folder, output_folder + names[0], True)
            except RuntimeError:
                continue
        print("None of the passwords worked!")
        return 1

    def download(self, url: str, path: str) -> int:
        """
        Download crackme from URL
        """
        chunks_done = 0
        with self.requests_session.get(url, stream=True) as req:
            file_size = int(req.headers['Content-length'])
            print(f"Downloading {self._format_bytes(file_size)}")
            if req.status_code != 200:
                print(f"URL {url} not found!! [{req.status_code}]")
                return 0
            with open(path, "wb") as f:
                for chunk in req.iter_content(chunk_size=self.download_chunk):
                    if chunk:
                        f.write(chunk)
                        chunks_done += len(chunk)
                        percent = (chunks_done * 100) / file_size if file_size else 0
                        print(f"download: [ {percent:.2f}% ]", end='\r')
        print()
        return 1
    
    def search(self, name: str = "", author: str = "", difficulty_min: int = 1, difficulty_max: int = 6, quality_min: int = 1, quality_max: int = 6) -> dict:
        """
        Search for specified with settings crackmes and get their details
        """
        token = self.get_token("https://crackmes.one/search")
        payload = f"name={name}&author={author}&difficulty-min={difficulty_min}&difficulty-max={difficulty_max}&quality-min={quality_min}&quality-max={quality_max}&token={token}"
        req = self.requests_session.post("https://crackmes.one/search", data=payload)
        soup = BeautifulSoup(req.text, 'html.parser')
        ret = {
            "crackmes": []
            }
        longest_user = 0
        longest_name = 0
        for tr in soup.find_all('tr', class_='text-center'):
            tds = tr.find_all('td')
            href_0 = tds[0].find('a')["href"]
            file_hash = href_0.replace("/crackme/", "")
            username = tds[1].find('a').get_text(strip=True)
            user_length = len(username)
            name = tds[0].get_text(strip=True)
            name_Length = len(name)
            tmp = {
                "name": name,
                "url": self.host + href_0,
                "download_url": urljoin(self.host, f"/static/crackme/{file_hash}") + ".zip",
                "filename": file_hash + '.zip',
                "filehash": file_hash,
                "user": username,
                "user_url": tds[1].find('a')["href"],
                "language": tds[2].get_text(strip=True),
                "arch": tds[3].get_text(strip=True),
                "difficulty": float(tds[4].get_text(strip=True)),
                "quality": float(tds[5].get_text(strip=True)),
                "os": tds[6].get_text(strip=True),
                "date": tds[7].get_text(strip=True),
                "solutions": int(tds[8].get_text(strip=True)),
                "comments": int(tds[9].get_text(strip=True)),
            }
            longest_user = user_length if user_length > longest_user else longest_user
            longest_name = name_Length if name_Length > longest_name else longest_name
            ret["crackmes"].append(tmp)
        self.last_search = ret
        ret["longest_user"] = longest_user
        ret["longest_name"] = longest_name
        return ret
    
    def get_info(self, url: str) -> dict:
        """
        Get (more) information about a specific crackme
        """
        ret = {
            'name': "",
            'user': "",
            'lang': "",
            'date': "",
            'os': "",
            'arch': "",
            'difficulty': "",
            'quality': ""
        }
        req = self.requests_session.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        container = soup.select_one('.container.grid-lg.wrapper')
        if not container:
            return ret

        h3 = container.find('h3')
        name = ''.join(c for c in h3.children if isinstance(c, str)).strip()[3:] if h3 else ''

        target_div = container.select_one('div.columns.panel-background')
        if not target_div:
            return ret

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

        details = [extract_text(div.find('p'), remove_a=(i in (4, 5))) for i, div in enumerate(filtered_divs)]
        ret = {
            'name': name,
            'user': details[0],
            'lang': details[1],
            'date': details[2],
            'os': details[3],
            'arch': details[6],
            'difficulty': details[4],
            'quality': details[5]
        }
        return ret

    def rating_color(self, rating: int, reverse: bool = False) -> str:
        """
        Turn the rating to a color\n
        1 = Green, 6 = Dark red
        """
        colors = COLOR_SCALE[::-1] if reverse else COLOR_SCALE
        bg_color = colors[rating - 1]
        brightness = COLOR_BRIGHTNESS[bg_color]
        text_color = 16 if brightness > 127 else 231  # black (16) or white (231)

        return f"\033[38;5;{text_color}m\033[48;5;{bg_color}m"