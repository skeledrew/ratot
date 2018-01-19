import pdb
import re

import pexpect  # NB: patch pexpect/__init__.py with `import replwrap`
import rpyc
from rpyc import server  # NB: patch rpyc/__init__.py with `from rpyc.utils import server`


class ShellSessionsService(rpyc.Service):

    def on_connect(self):
        self._bash = pexpect.replwrap.bash()

    def on_disconnect(self):
        self._bash.run_command('exit')
        del self._bash

    def exposed_repl(self, in_):
        try:
            out_ = clean_ansi(self._bash.run_command(in_))
            return out_

        except Exception as e:
            print('Something broke: {}'.format(repr(e)))
            return e


def clean_ansi(text):
    # remove ANSI control codes
    ANSI_CLEANER = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
    clean_text = ANSI_CLEANER.sub("", text)
    return clean_text


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(ShellSessionsService, port=18881)
    print('Running Shell sessions server...')
    t.start()
    print('Server terminated')
