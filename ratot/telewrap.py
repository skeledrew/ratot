import pdb
import re

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

    def start(self, session='', a_id=0, a_hash='', phone=''):
        self.add_client(session, a_id, a_hash)
        self.connect()
        self.authenticate(phone)
        return

    def handle_update(self, update):
        self._updates.append(update)
        return

    @staticmethod
    def load_config(config_file):
        config = yaml.load(open(config_file))
        clt_cfg = {}
        clt_cfg['a_id'] = config['client']['api_id']
        clt_cfg['a_hash'] = config['client']['api_hash']
        clt_cfg['session'] = config['sessions'][0]['name']
        clt_cfg['phone'] = config['sessions'][0]['phone']
        return clt_cfg


if __name__ == '__main__':
    # testing
    tgcw = TGCWrapper()
    #pdb.set_trace()
    config = TGCWrapper.load_config('ratot.yaml')
    tgcw.start(**config)
    embed(globals(), locals())
