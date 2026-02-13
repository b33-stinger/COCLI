class Acc():

    def __init__(self, crackmes = None, requests_session = None, config_manager = None):
        self.crackmes = crackmes                 # Set ASAP | crackmes instance
        self.requests_session = requests_session # Set ASAP | requests instance
        self.config = config_manager             # Set ASAP | config instance
        self.logged_in = False
        self.username = None
    
    def login(self, use_cookie: bool, username: str, password: str, save_cookie: bool) -> int:
        '''
        Login -> username + password -> 0 Something went Wrong, 1 Ok
        '''
        print('Logging in...', end=' ', flush=True)
        if use_cookie:
            self.requests_session.cookies.update({'crackmesone': self.config.get('crackmesone')})
            req = self.requests_session.get(self.config.get('host'))

        csrf_token = self.crackmes.get_csrf_token(self.config.get('login'))
        payload = {
            'name': username,
            'password': password,
            'csrf_token': csrf_token
        }
        req = self.requests_session.post(self.config.get('login'), data=payload, headers=self.requests_session.headers.update(self.config.get('login_headers')))
        status = 0
        if 'Password is incorrect' in req.text and self.check_login():
            print('Username or Password is wrong')
            status = 0
        if 'Login successful!' in req.text:
            print('[ OK ]')
            status = 1
        if save_cookie and status == 1:
            self.config.update('crackmesone', req.cookies['crackmesone'])
        return status
    
    def logout(self) -> int:
        '''
        Logout -> 1 logged out, 0 something went wrong
        '''
        print('Logging out...', end=' ', flush=True)
        req = self.requests_session.get(self.config.get('logout'))
        if 'Goodbye!' in req.text or not self.check_login():
            print('[ OK ]')
            return 1
        print('[ Something went wrong ]')
        return 0
    
    def check_login(self) -> int:
        '''
        Check if you're really logged in
        '''
        req = self.requests_session.get(self.config.get('upload'))
        if 'Please provide details in the infos section. You can upload just the executable or an archive containing needed resources.' in req.text:
            return 1
        return 0

    def get_username(self) -> str:
        '''
        Get your username
        '''
        if not self.logged_in:
            print('[ Please login first ]')
            return ''
        req = requests.get(self.config['host'])