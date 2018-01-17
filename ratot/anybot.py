import pdb

import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters


class AnyBot(Updater):

    def __init__(self, token=None, config=None):
        #pdb.set_trace()
        super().__init__(token or open('{}.token'.format(sys.argv[0])).read().strip())
        self.load_handlers()

    def load_handlers(self, handlers=None):

       if not handlers:  [self.add_handler(self.make_handler(globals()[h]))for h in globals() if h.startswith('handle_')]

    def add_handler(self, handler):
        self.dispatcher.add_handler(handler)
        return

    def make_handler(self, callback):
        pattern = callback()
        if isinstance(pattern, str) and pattern.startswith('/'):
            return CommandHandler(pattern[1:], callback)

        if isinstance(pattern, str):
            return MessageHandler(Filters.text, callback)
        return


def handle_start(bot=None, update=None):
    if not update: return '/start'
    user = update.message.from_user.first_name
    msg = "Hi {}. I'm a generic bot that needs configuration, I think.".format(user)
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def handle_config(bot=None, update=None):
    if not update: return '/config'
    msg = 'Configuration command not yet implemented.'
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def handle_help(bot=None, update=None):
    if not update: return '/help'
    msg = 'Help command not yet implemented.'
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return

def handle_text(bot=None, update=None):
    # process regular text
    if not update: return '.+'
    msg = 'Received: {}'.format(update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text=msg)
    return


if __name__ == '__main__':
    # mainly for testing
    anybot = AnyBot()
    anybot.start_polling()
    print('AnyBot is running...')
    anybot.idle()
    anybot.stop()
    print('AnyBot terminated')
