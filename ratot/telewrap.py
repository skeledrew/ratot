#! /usr/bin/env python3


import pdb
import re
from time import sleep

import yaml
from telethon import TelegramClient as TGC
from ptpython.repl import embed


class Callback():

    def __init__(self, wrapper):
        # get the wrapper instance
        self._wrapper = wrapper
        return

    def __call__(self, update):
        # pass update to instance method
        return self._wrapper.handle_update(update)

class TGCWrapper():

    def __init__(self):
        self._clients = {}
        self._current = None  # current session
        self._updates = []
        return

    def __call__(self, clt_method, args=None, kwargs=None):
        clt = self.get_client(self._current)
        invokable = getattr(clt, clt_method, None)
        if not invokable: return Exception('Invalid method name `{}`'.format(clt_method))
        return invokable() if not (args or kwargs) else invokable(*args, **kwargs) if args and kwargs else invokable(*args) if not kwargs else invokable(**kwargs)

    def add_client(self, session, api_id, api_hash, workers=4):
        clt = TGC(session, api_id, api_hash)
        clt.updates.workers = workers
        clt.add_update_handler(Callback(self))
        self._clients[session] = {'client': clt}
        self._current = session
        return

    def get_client(self, session=None):
        if not session: session = self._current
        clt = self._clients[session]['client']
        return clt

    def connect(self, session=None):
        if not session: session = self._current
        try:
            self.get_client(session).connect()

        except Exception as e:
            msg = 'Connect attempt failed: {}'.format(repr(e))
            print(msg)
            return e
        return True

    def authenticate(self, phone, session=None):
        if not session: session = self._current
        clt = self.get_client(session)
        if clt._phone and phone == clt._phone: return True
        if not re.match('^\+\d+$', phone): return ValueError('Invalid phone number format. Re-enter as `+12345678901`')
        if clt.is_user_authorized(): return True
        try:
            clt.send_code_request(phone)
            clt.sign_in(phone, input('Enter code: '))
            self._clients[session]['me'] = clt.get_me()
            self._clients[session]['phone'] = phone

        except Exception as e:
            msg = 'User authentication failed: {}'.format(repr(e))
            print(msg)
            return e
        return True

    def get_dialogs(self, amt=10):
        clt = self.get_client(self._current)
        dialogs = clt.get_dialogs(amt)
        return dialogs

    def get_peers(self, amt=None, dialogs=None):
        if not dialogs: dialogs = self.get_dialogs(amt)
        clt = self.get_client(self._current)
        peers = []

        for d in dialogs:
            try:
                peers.append(clt.get_entity(d.dialog.peer))

            except:
                pass
        p_names = [p.title if hasattr(p, 'title') and p.title else '{} {}'.format(p.first_name or '', p.last_name or '').strip() if p.first_name or p.last_name else p.username if p.username else p.phone if p.phone else 'DELETED' if p.deleted else str(p) for p in peers]
        return {p_name: peer for p_name, peer in zip(p_names, peers)}

    def get_peer(self, name, peers=None):
        if not peers: peers = self.get_peers()
        if name in peers: return peers[name]
        matches = []

        for peer in list(peers.keys()):
            # TODO: try several matching methods
            if re.match(name, peer): return peers[peer]
            if name.lower() in peer.lower(): return peers[peer]
        return None

    def get_sender(self, message):
        try:
            return self.get_client().get_entity(message.from_id)

        except Exception as e:
            msg = 'Failed to get message sender: {}'.format(repr(e))
            return e

    def get_recvr(self, message):
        try:
            return self.get_client().get_entity(message.to_id)

        except Exception as e:
            msg = 'Failed to get message recipient: {}'.format(repr(e))
            return e

    def start(self, session='', a_id=0, a_hash='', phone=''):
        self.add_client(session, a_id, a_hash)
        self.connect()
        self.authenticate(phone)
        return

    def handle_update(self, update):
        self._updates.append(update)
        return

    @staticmethod
    def load_config(config_file, session=0):
        config = yaml.load(open(config_file))
        clt_cfg = {}
        clt_cfg['a_id'] = config['client']['api_id']
        clt_cfg['a_hash'] = config['client']['api_hash']
        clt_cfg['session'] = config['sessions'][session]['name']
        clt_cfg['phone'] = config['sessions'][session]['phone']
        return clt_cfg

class CommandsInterface(TGCWrapper):

    def __init__(self):
        super().__init__()
        self._commands = []
        self.get_commands()
        self._current_peer = None
        self._blocking = False
        self.__dbg = False  # help debug updates
        return

    def __call__(self, line):
        cmd = '{}_cmd'.format(line.split()[0])
        if not hasattr(self, cmd): raise AttributeError('`{}` is not a valid command'.format(cmd))
        result = getattr(self, cmd)(line)
        return result

    def get_commands(self):
        commands = [getattr(self, m) for m in dir(self) if m.endswith('_cmd')]
        self._commands = commands
        return commands

    def config_repl(self, options):
        pass

    def repl(self, options=None):
        self.config_repl(options)

        while True:
            in_ = input('_ ')
            if in_ in ['-exit-', '-quit-']: break
            if not in_.strip(): continue
            result = self(in_)
            self._blocking = True

            while self._blocking:
                # wait for response
                sleep(1)
        return

    def handle_update(self, update):
        super().handle_update(update)
        if not hasattr(update, 'message'): return
        #if not update.message.from_id == self._current_peer.id and update.message.to_id == myself.id: return
        if not hasattr(update, 'user_id') or not update.user_id == self._current_peer.id: return
        pfn = self._current_peer.first_name
        pln = self._current_peer.last_name
        pun = self._current_peer.username
        name = '{} {}'.format(pfn, pln or '').strip() if pfn else '@{}'.format(pun) if pun else '???'
        text = update.message
        print('{} said: {}'.format(name, text))
        if self._blocking: self._blocking = False
        return

    def msg_cmd(self, cmd):
        peer = self.get_peer(cmd.split()[1])
        text = ' '.join(cmd.split()[2:])
        result = super().__call__('send_message', [peer, text])
        self._current_peer = peer
        return

    def chat_with(self, cmd):
        pass

if __name__ == '__main__':
    # testing
    #tgcw = TGCWrapper()
    ci = CommandsInterface()
    config = TGCWrapper.load_config('ratot.yaml')
    ci.start(**config)
    ci.repl()
    #embed(globals(), locals())
