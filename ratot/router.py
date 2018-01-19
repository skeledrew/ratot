import pdb
import sys
import time
import os

import rpyc

sys.path.append(os.path.dirname(__file__))  # put in __init__?
from anybot import AnyBot


class RouterBot(AnyBot):

    def __init__(self, token):
        super().__init__(token)
        setattr(self.bot, 'wrapper', self)
        #pdb.set_trace()
        self._host = 'localhost'
        self._port = 18881
        self.commands = ['new']
        self.load_handlers(rb_handlers())
        self._sessions = {}
        return

    def process_command(self, update):
        # handle all commands
        user = update.message.from_user.username
        chat = update.message.chat_id
        text = update.message.text
        if text.startswith('/new'): return self.new_session({'user': user, 'text': text})
        update.message.reply_text('Received command: {}'.format(text))
        return

    def new_session(self, **data):
        text = text.split()
        name = text[1] if len(text) > 1 else 'default'
        try:
            c = rpyc.connect(self._host, self._port)
        except Exception as e:
            return e
        name = '{}_{}'.format(user, name)
        self._sessions[name] = c
        return


def rb_handlers():
    # hack handlers into loader
    return {'handle_start': handle_start, 'handle_text': handle_text, 'handle_ping': handle_ping, 'handle_new': handle_new}

def handle_text(bot=None, update=None, args=None):
    if not update: return '.+'
    in_ = update.message.text
    #pdb.set_trace()
    user = '{} {} ({})'.format(update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username)
    bot.wrapper.write_log('{}: {} sent `{}`'.format(time_stamp(), user, in_))
    if not update.message.from_user.username in ['skeledrew']:
        msg = "You don't have permissions for this."
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        return
    c = rpyc.connect('localhost', 18881)
    out_ = c.root.repl(in_)

    bot.send_message(chat_id=update.message.chat_id, text=out_)
    return

def handle_start(bot=None, update=None, args=None):
    if not update: return '/start'
    user = update.message.from_user.first_name
    msg = "Hi {}. This bot allows you to access a shell remotely, if you have permission.".format(user)
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def handle_ping(bot=None, update=None, args=None):
    if not update: return '/ping'
    msg = 'pong!'
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def handle_command(bot=None, update=None, args=None):
    # catch all
    if not update: return ['new']
    bot.wrapper.process_command(update)
    return

def handle_new(bot=None, update=None, args=None):
    if not update: return '/new'
    if bot == 'help': return 'Create a new session: `/new [session_name] [shell_type]`'
    bot.wrapper.process_command(update)
    return
def time_stamp():
    return time.asctime()


if __name__ == '__main__':
    # testing purposes
    rbot = RouterBot(token=open('anybot.py.token').read().strip())
    rbot.start_polling()
    print('RouterBot is running...')
    rbot.idle()
    rbot.stop()
    print('RouterBot terminated')
