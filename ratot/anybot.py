#! /usr/bin/env python3

import pdb

import sys
import logging

from telegram.ext import Updater, MessageHandler
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

    def __init__(self, token=None, config={}):
        super().__init__(token or open('{}.token'.format(sys.argv[0])).read().strip())  # TODO: read from config
        #self._handlers = {}
        command_cb = Callback(self, 'handle_command')
        self.dispatcher.add_handler(MessageHandler(Filters.command, command_cb))
        text_cb = Callback(self, 'handle_text')
        self.dispatcher.add_handler(MessageHandler(Filters.text, text_cb))
        default_log = {'filename': '{}.log'.format(sys.argv[0]), 'level': 'DEBUG'}
        log_cfg = config.get('log', default_log)
        log_cfg['level'] = log_cfg.get('level', 'INFO').upper()
        logging.basicConfig(format='%(asctime)s (%(levelname)s): %(message)s', **log_cfg)
        self.log = logging
        return

    def inject_handler(self, handler, name=''):
        if not name: name = 'nameless_cmd'  # TODO: get name from handler itself
        setattr(self, name, handler)

    def handle_command(self, bot, update):
        msg = update.message.text
        cmd = '{}_cmd'.format(msg.split()[0][1:])

        if not hasattr(self, cmd):
            self.log.warning('Invalid command `{}` received and ignored.'.format(cmd))
            bot.send_message(chat_id=update.message.chat_id, text='`{}` is not a valid command.'.format(cmd))
            return
        result = getattr(self, cmd)(bot, update)
        return result

    def handle_text(self, bot, update):
        # process regular text
        msg = update.message.text
        msg = 'Received: {}'.format(update.message.text)
        self.log.info('{} from chat_id {}'.format(msg, update.message.chat_id))
        bot.send_message(chat_id=update.message.chat_id, text=msg)
        bot.send_message(chat_id=update.message.chat_id, text='Override the `handle_text` method with your own to properly process text.')
        return

    def handle_file(self, bot, update):
        pass

    def start_cmd(self, bot, update):
        user = update.message.from_user.first_name
        self.log.info('{} ({}) started the bot.'.format(user, update.message.from_user.username))
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
