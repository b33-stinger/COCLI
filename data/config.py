# Imports
from json import loads as json_loads, dump as json_dump
from os.path import isfile


# Classes
class ConfigManager():
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config(self.config_file)

    def load_config(self, config_file: str = None, create: bool = True) -> dict:
        '''
        Load your current config from config_file\n
        If not existing, create and return empty config
        '''
        config_file = config_file or self.config_file

        if not isfile(config_file):
            self.save_config({}, config_file)
            return {}

        with open(config_file, 'r') as f:
            return json_loads(f.read())


    def save_config(self, config_file: str = None, config: dict = None) -> int:
        '''
        Dump your current config into config_file
        '''
        config_file = config_file or self.config_file
        config = config or self.config
        
        with open(config_file, 'w') as f:
            json_dump(config, f, indent=4)
        return 1

    def update(self, key: str, value: any) -> int:
        '''
        Set key to value
        '''
        self.config[key] = value
        return 1

    def get(self, key: any, default: any = None) -> any:
        '''
        Get value of key
        '''
        return self.config.get(key, default)