#! /usr/bin/env python3

import pdb

import sys
import time
import os
from threading import Timer

import rpyc
import yaml

sys.path.append(os.path.dirname(__file__))  # put in __init__.py?
from anybot import AnyBot, Callback
from config import config


class RouterBot(AnyBot):

    def __init__(self, token):
        super().__init__(token, {})
        self._host = config.get('HOST')
        self._port = int(config.get('PORT'))
        self.commands = ['new']
        self._sessions = {}
        self._async_ops = []
        self._clean_interval = 5
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
        uname = update.message.from_user.username
        user = '{} {} ({})'.format(update.message.from_user.first_name, update.message.from_user.last_name or '_', uname)
        self.log.info('{} sent `{}`'.format(user, in_))
        if not uname in config.get('ADMINS').split(config.get('SEPARATOR')):
            msg = "You don't have permissions for this."
            bot.send_message(chat_id=update.message.chat_id, text=msg)
            return
        self.call_repl(uname, in_, bot.send_message, [], {'chat_id': update.message.chat_id})
        return

    def call_repl(self, user, in_, cb=None, cb_args=[], cb_kwargs={}):
        if not user in self._sessions: self._sessions[user] = {}
        uss = self._sessions[user]

        try:
            if not 'default' in uss: uss['default'] = uss['__current__'] = rpyc.connect(self._host, self._port)
            c = uss['__current__']
            a_repl = rpyc.async(c.root.a_repl)
            a_op = a_repl(in_, cb, cb_args, cb_kwargs, self.log)
            self._async_ops.append(a_op)
            Timer(1, self._force_wait, [a_op]).start()  # hacky; raise issue
            self._clean_timer()

        except Exception as e:
            msg = 'Something broke en route: {}'.format(repr(e))
            self.log.exception(msg)
            return msg

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

    def _clean_timer(self):
        if not self._async_ops: return
        self.log.info('Cleaning ready async ops')

        for ao in self._async_ops:
            if ao.ready: self._async_ops.remove(ao)
        Timer(self._clean_interval, self._clean_timer).start()
        return

    def _force_wait(self, ao):
        # attempt to fix that bug where async op only completes if value is called
        res = ao.value
        return res

def time_stamp():
    return time.asctime()



if __name__ == '__main__':
    # testing purposes
    rbot = RouterBot(token=config.get('TOKEN'))
    rbot.start_polling()
    print('RouterBot is running...')
    rbot.idle()
    rbot.stop()
    print('RouterBot terminated')
