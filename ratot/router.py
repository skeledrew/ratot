import pdb
import sys
import time
import os

import rpyc

sys.path.append(os.path.dirname(__file__))  # put in __init__?
from anybot import AnyBot, Callback


class RouterBot(AnyBot):

    def __init__(self, token):
        super().__init__(token)
        self._host = 'localhost'
        self._port = 18881
        self.commands = ['new']
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

    def handle_text(self, bot, update):
        in_ = update.message.text
        #pdb.set_trace()
        user = '{} {} ({})'.format(update.message.from_user.first_name, update.message.from_user.last_name, update.message.from_user.username)
        self.write_log('{}: {} sent `{}`'.format(time_stamp(), user, in_))
        if not update.message.from_user.username in ['skeledrew']:
            msg = "You don't have permissions for this."
            bot.send_message(chat_id=update.message.chat_id, text=msg)
            return
        c = rpyc.connect('localhost', 18881)
        out_ = c.root.repl(in_)

        bot.send_message(chat_id=update.message.chat_id, text=out_)
        return

    def start_cmd(self, bot, update):
        user = update.message.from_user.first_name
        msg = "Hi {}. This bot allows you to access a shell remotely, if you have permission.".format(user)
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        return

    def ping_cmd(self, bot, update):
        msg = 'pong!'
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        return

    def new_cmd(self, bot, update):
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
