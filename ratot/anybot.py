import pdb

import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters


class Callback():

    def __init__(self, wrapper, invoke):
        self._wrapper = wrapper
        self._invoke = invoke
        return

    def __call__(self, *args, **kwargs):
        if not hasattr(self._wrapper, self._invoke): raise AttributeError('`{}` not found.'.format(self._invoke))
        return getattr(self._wrapper, self._invoke)(*args, **kwargs)

class AnyBot(Updater):

    def __init__(self, token=None, config=None):
        super().__init__(token or open('{}.token'.format(sys.argv[0])).read().strip())
        self._handlers = {}
        command_cb = Callback(self, 'handle_command')
        self.dispatcher.add_handler(MessageHandler(Filters.command, command_cb))
        text_cb = Callback(self, 'handle_text')
        self.dispatcher.add_handler(MessageHandler(Filters.text, text_cb))
        #self.load_handlers()  # TODO: figure how to make overridable
        return

    def load_handlers(self, handlers=None):

       if not handlers: handlers = globals()
       [self.add_handler(self.make_handler(handlers[h]))for h in handlers if h.startswith('handle_')]

    def add_handler(self, handler):

        try:
            if hasattr(handler, 'command') and handler.command[0] in self._handlers: self.dispatcher.remove_handler(self._handlers[handler.command[0]])
            if handler.filters and str(handler.filters) in self._handlers: self.dispatcher.remove_handler(self._handlers[str(handler.filters)])

        except:
            pass
        self._handlers[handler.command[0] if hasattr(handler, 'command') else str(handler.filters)] = handler
        self.dispatcher.add_handler(handler)
        return

    def make_handler(self, callback):
        pattern = callback()
        if isinstance(pattern, str) and pattern.startswith('/'):
            return CommandHandler(pattern[1:], callback, pass_args=True)
        if pattern and isinstance(pattern, list): return CommandHandler(pattern, callback, pass_args=True)
        if isinstance(pattern, str):
            return MessageHandler(Filters.text, callback)
        return

    def inject_handler(self, handler):
        pass
    def write_log(self, msg):
        open('{}.log'.format(sys.argv[0]), 'a').write(msg + '\n')

    def handle_command(self, bot, update):
        msg = update.message.text
        cmd = '{}_cmd'.format(msg.split()[0][1:])

        if not hasattr(self, cmd):
            bot.send_message(chat_id=update.message.chat_id, text='`{}` is not a valid command.'.format(cmd))
            return
        result = getattr(self, cmd)(bot, update)
        return result

    def handle_text(self, bot, update):
        # process regular text
        msg = update.message.text
        msg = 'Received: {}'.format(update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        bot.send_message(chat_id=update.message.chat_id, text='Override the `handle_text` method with your own to properly process text.')
        return

    def start_cmd(self, bot, update):
        user = update.message.from_user.first_name
        msg = "Hi {}. I'm a generic bot that needs configuration, I think.".format(user)
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        return

    def config_cmd(self, bot, update):
        msg = 'Configuration command not yet implemented.'
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        return

    def help_cmd(self, bot, update):
        msg = 'Help command not yet implemented.'
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
