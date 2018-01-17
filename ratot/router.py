import pdb
import sys
import time

import rpyc

sys.path.append('/home/skeledrew/Projects/Telegram/ratot/ratot')  # dirty hack
from anybot import AnyBot


class RouterBot(AnyBot):

    def __init__(self, token):
        super().__init__(token)
        setattr(self.bot, 'wrapper', self)
        #pdb.set_trace()
        self.load_handlers(rb_handlers())


def rb_handlers():
    return {'handle_start': handle_start, 'handle_text': handle_text}

def handle_text(bot=None, update=None):
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

def handle_start(bot=None, update=None):
    if not update: return '/start'
    user = update.message.from_user.first_name
    msg = "Hi {}. This bot allows you to access a shell remotely.".format(user)
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def time_stamp():
    return time.asctime(time.localtime(time.time()))


if __name__ == '__main__':
    rbot = RouterBot(token=open('anybot.py.token').read().strip())
    rbot.start_polling()
    print('RouterBot is running...')
    rbot.idle()
    rbot.stop()
    print('RouterBot terminated')
