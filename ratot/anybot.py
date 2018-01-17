import pdb

import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters


class AnyBot(Updater):

    def __init__(self, token=None, config=None):
        super().__init__(token or open('{}.token'.format(sys.argv[0])).read().strip())
        self._handlers = {}
        #self.load_handlers()  # TODO: figure how to make overridable

    def load_handlers(self, handlers=None):

       if not handlers: handlers = globals()
       [self.add_handler(self.make_handler(handlers[h]))for h in handlers if h.startswith('handle_')]

    def add_handler(self, handler):

        try:
            if hasattr(handler, 'command') and handler.command[0] in self._handlers: self.dispatcher.remove_handler(self._handlers[handler.command[0]])
            if handler.filters and str(handler.filters) in self._handlers: self.dispatcher.remove_handler(self._handlers['mh'])

        except:
            pass
        self._handlers[handler.command[0] if hasattr(handler, 'command') else str(handler.filters)] = handler
        self.dispatcher.add_handler(handler)
        return

    def make_handler(self, callback):
        pattern = callback()
        if isinstance(pattern, str) and pattern.startswith('/'):
            return CommandHandler(pattern[1:], callback)

        if isinstance(pattern, str):
            return MessageHandler(Filters.text, callback)
        return

    def write_log(self, msg):
        open('{}.log'.format(sys.argv[0]), 'a').write(msg + '\n')

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
