"""Handle config data"""


from dotenv import find_dotenv, dotenv_values


__all__ = ['Config', 'config']


class Config():
    """Load from dotenv"""

    def __init__(self, env_name=None):
        env_path = find_dotenv(env_name or '.env')
        if not env_path: raise OSError('Unable to locate dotenv')
        self._env = dotenv_values(env_path)

    def get(self, key):
        """Returns the specified key if found,
           else raises an exception
        """
        if not key in self._env: raise KeyError('{} does not exist in dotenv file'.format(key))
        return self._env[key]

config = Config()
