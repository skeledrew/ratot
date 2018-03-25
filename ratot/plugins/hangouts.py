#! /usr/bin/env python3

import pdb

import sys
import os
import asyncio
from threading import Timer
import logging

import hangups
from hangups.ui.utils import get_conv_name


class HangupsDisconnected(Exception):
    pass

class HangoutsClient():

    def __init__(self, config={}):
        self._conv_list = None
        self._user_list = None
        refresh_token_path = config.get('refresh_token_path', None) or os.path.join(os.path.dirname(__file__), 'hangouts.token')

        try:
            cookies = hangups.auth.get_auth_stdin(refresh_token_path)

        except hangups.GoogleAuthError as e:
            sys.exit('Login failed ({})'.format(repr(e)))
        self._client = hangups.Client(cookies)
        self._client.on_connect.add_observer(self._on_connect)
        self._connected = False
        logging.basicConfig(level=logging.DEBUG)
        self.log = logging
        self._event_loop = None

    async def _connect(self):
        await self._client.connect()
        #raise HangupsDisconnected()

    async def _on_connect(self):
        #
        self._user_list, self._conv_list = (
            await hangups.build_user_conversation_list(self._client)
        )

        self._conv_list.on_event.add_observer(self._on_event)
        return

    def _on_event(self, conv_event):
        conv = self._conv_list.get(conv_event.conversation_id)
        user = conv.get_user(conv_event.user_id)
        show_notification = all((
            isinstance(conv_event, hangups.ChatMessageEvent),
            not user.is_self,
            not conv.is_quiet,
        ))
        return

    def _run_event_loop(self, task):
        loop = asyncio.get_event_loop()
        self._event_loop = loop
        #if task:
        #loop.close()
        return

    def run_event_loop(self, task=None):
        # run loop in a different thread
        self._loop_wrap_timer = Timer(0, self._run_event_loop, [task]).start()
        return

    async def _disconnect(self):
        await self._client.disconnect()
        return

    async def _list_coro(self, client):
        user_list, conversation_list = (
        await hangups.build_user_conversation_list(client)
)
        all_users = user_list.get_all()
        all_conversations = conversation_list.get_all(include_archived=True)

        print('{} known users'.format(len(all_users)))
        for user in all_users:
            print('    {}: {}'.format(user.full_name, user.id_.gaia_id))
        print('{} known conversations'.format(len(all_conversations)))
        return

    def list_cmd(self):
        self.run_it(self._list_coro)
        return

    def run_it(self, coro):
         task = asyncio.ensure_future(self._async_main(coro, self._client),
loop=self._event_loop)
         if not self._connected:
             self.log.warning('Client not yet connected to server.')
             return
         self._event_loop.run_until_complete(task)

    async def _async_main(self, coro, client):

        if not self._connected:
            task = asyncio.ensure_future(client.connect())
            on_connect = asyncio.Future()
            client.on_connect.add_observer(lambda: on_connect.set_result(None))
            done, _ = await asyncio.wait(
                (on_connect, task),
                return_when=asyncio.FIRST_COMPLETED
            )
            await asyncio.gather(*done)

        try:
            await coro(client)

        except Exception as e:
            self.log.exception('Something broke: {}'.format(repr(e)))
        return


class HC():

    def __init__(self):
        self._futures = []
        self._client = None

    async def _async_main(self, coro, client, args):
        """Run the coroutine."""
        # Spawn a task for hangups to run in parallel with the example coroutine.
        if not self._client:
            task = asyncio.ensure_future(client.connect())

            # Wait for hangups to either finish connecting or raise an exception.
            on_connect = asyncio.Future()
            client.on_connect.add_observer(lambda: on_connect.set_result(None))
            done, _ = await asyncio.wait(
                (on_connect, task), return_when=asyncio.FIRST_COMPLETED
            )
            await asyncio.gather(*done)
            self._client = client

        # Run the example coroutine. Afterwards, disconnect hangups gracefully and
        # yield the hangups task to handle any exceptions.
        try:
            await coro(client, args)
        except asyncio.CancelledError:
            pass
        #finally:
        #    await client.disconnect()
        #    await task
        return

    def run_coro(self, coro, *extra_args):
        """Run a hangups coroutine.
        Args:
            coro (coroutine): Coroutine to run with a connected
                hangups client and arguments namespace as arguments.
            extra_args (str): Any extra command line arguments required by the
                example.
        """
        args = []
        logging.basicConfig(level=logging.INFO)
        # Obtain hangups authentication cookies, prompting for credentials from
        # standard input if necessary.
        cookies = hangups.auth.get_auth_stdin('hangouts.token')
        client = hangups.Client(cookies)
        self._event_loop = asyncio.get_event_loop()
        self.run_event_loop()
        coro = self._async_main(coro, client, args)
        future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)
        self._futures.append(future)

    def _run_event_loop(self, loop):
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            #task.cancel()
            #loop.run_until_complete(task)
            pass
        finally:
            loop.close()
        return

    def run_event_loop(self):
        Timer(0, self._run_event_loop, [self._event_loop]).start()
        return

    async def sync_recent_convos(self, client, _):
        user_list, conversation_list = (
            await hangups.build_user_conversation_list(client)
        )
        self._all_users = list(user_list.get_all())
        self._all_convos = conversation_list.get_all(include_archived=True)
        self._all_convos.on_event.add_observer(self.on_event)

        print('{} known users'.format(len(self._all_users)))
        #for user in all_users:
        #    print('    {}: {}'.format(user.full_name, user.id_.gaia_id))

        print('{} known convos'.format(len(self._all_convos)))
        #for conversation in all_conversations:
        #    if conversation.name:
        #        name = conversation.name
        #    else:
        #        name = 'Unnamed conversation ({})'.format(conversation.id_)
        #        print('    {}'.format(name))
        return

    def start_cmd(self):
        self.run_coro(self.sync_recent_convos)
        return

    def on_event(self, conv_event):
        if isinstance(conv_event, hangups.ChatMessageEvent):
            print('received chat message: {!r}'.format(conv_event.text))
        return

    async def send_message(self, client, args):
        request = hangups.hangouts_pb2.SendChatMessageRequest(
            request_header=client.get_request_header(),
            event_request_header=hangups.hangouts_pb2.EventRequestHeader(
                conversation_id=hangups.hangouts_pb2.ConversationId(
                    id=args['conversation_id']
                ),
                client_generated_id=client.get_client_generated_id(),
            ),
            message_content=hangups.hangouts_pb2.MessageContent(
                segment=[
                    hangups.ChatMessageSegment(args['message_text']).serialize()
                ],
            ),
        )
        await client.send_chat_message(request)
        return

    def send_cmd(self, text):
        if not text: return
        uid = self.get_user(text.split()[0])
        text = ' '.join(text.split()[1:])
        self.run_coro(self.send_message, uid, text)
        return


if __name__ == '__main__':
    # setup a REPL
    #hc = HangoutsClient()
    #HC.run_it(HC.sync_recent_convos)
    hc = HC()
    hc.start_cmd()
    pdb.set_trace()
