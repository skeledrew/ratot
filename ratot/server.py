import pdb

import pexpect  # NB: patch pexpect/__init__.py with `import replwrap`
import rpyc
from rpyc import server  # NB: patch rpyc/__init__.py with `from rpyc.utils import server`


class ShellSessionsService(rpyc.Service):

    def on_connect(self):
        self._bash = pexpect.replwrap.bash()

    def on_disconnect(self):
        pass

    def exposed_repl(self, in_):
        try:
            out_ = self._bash.run_command(in_)
            return out_

        except Exception as e:
            print('Something broke: {}'.format(repr(e)))
            return e

if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(ShellSessionsService, port=18881)
    print('Running Shell sessions server...')
    t.start()
    print('Server terminated')
