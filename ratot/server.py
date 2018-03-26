#! /usr/bin/env python3

import pdb
import re
import logging
import sys

import pexpect  # NB: patch pexpect/__init__.py with `from . import replwrap`
import rpyc
from rpyc import server  # NB: patch rpyc/__init__.py with `from rpyc.utils import server`

from config import config


logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s', filename='{}.log'.format(sys.argv[0]), level=logging.DEBUG)


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

    def exposed_a_repl(self, in_, cb=None, args=[], kwargs={}, log=None):
        out_ = None
        logging.debug('Inside async repl')

        try:
            out_ = clean_ansi(self._bash.run_command(in_))
            logging.debug('Command complete!')

        except Exception as e:
            out_ = 'Something broke. Check the logs if you have permission, or report to the admin.'
            err = 'Something broke on the server: {}'.format(repr(e))
            if err and logging: logging.exception(err)
        kwargs['text'] = out_
        logging.debug('Running callback {} in async with results:\n{}'.format(str(cb), out_))
        cb(chat_id=kwargs['chat_id'], text=out_)
        return out_


def clean_ansi(text):
    # remove ANSI control codes
    ANSI_CLEANER = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
    clean_text = ANSI_CLEANER.sub("", text)
    return clean_text


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(ShellSessionsService, port=int(config.get('PORT')))
    print('Running Shell sessions server...')
    t.start()
    print('Server terminated')
