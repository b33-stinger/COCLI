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
            'lang': {'type': 'value', 'desc': 'Binary Language'}
        },
    },
    {
        'name': 'latest',
        'desc': 'Get the latest crackmes',
        'args': {
            'page': {'type': 'value', 'desc': 'Which page'},
            'all': {'type': 'flag', 'desc': 'Get all'}
        }
    },
    {
        'name': 'login',
        'desc': 'Log into your account',
        'args': {
            'use_cookie': {'type': 'flag', 'desc': 'Use your saved session cookie instead'},
            'username': {'type': 'value', 'desc': 'Your username'},
            'password': {'type': 'value', 'desc': 'Your password'},
            'save_session': {'type': 'flag', 'desc': 'Your your login cookie?'}
        },
    },
    {
        'name': 'logout',
        'desc': 'Logout of your account',
        'args': {}
    },
    {
        'name': 'history',
        'desc': 'manager your history',
        'args': {
            'nuke': {'type': 'flag', 'desc': 'wipe history'},
            'ignore': {'type': 'value', 'desc': 'add commands to ignore. Seperate with comma,'},
            'unignore': {'type': 'value', 'desc': 'remove commands from ignore list. Seperate with comma,'}
        }
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