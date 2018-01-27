#! /usr/bin/env python3

import pdb

import sys
import os

import hangups
from hangups.ui.utils import get_conv_name


class HangupsDisconnected(Exception):
    pass

class HangoutsClient():

    def __init__(self, config={}):
        self._conv_list = None
        self._user_list = None
        refresh_token_path = config.get('refresh_token_path', None) or os.path.join(os.path.dirname(__file__), 'hangouts.token')
        #if not refresh_token_path: refresh_token_path =

        try:
            cookies = hangups.auth.get_auth_stdin(refresh_token_path)

        except hangups.GoogleAuthError as e:
            sys.exit('Login failed ({})'.format(repr(e)))
        self._client = hangups.Client(cookies)
        self._client.on_connect.add_observer(self._on_connect)

    async def _connect(self):
        await self._client.connect()
        #raise HangupsDisconnected()

    async def _on_connect(self):
        #
        self._user_list, self._conv_list = (
            await hangups.build_user_conversation_list(self._client)
        )

        self._conv_list.on_event.add_observer(self._on_event)

    def _on_event(self, conv_event):
        conv = self._conv_list.get(conv_event.conversation_id)
        user = conv.get_user(conv_event.user_id)
        show_notification = all((
            isinstance(conv_event, hangups.ChatMessageEvent),
            not user.is_self,
            not conv.is_quiet,
        ))


if __name__ == '__main__':
    # setup a REPL
    hc = HangoutsClient()
    pdb.set_trace()
