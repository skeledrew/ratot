=====
Ratot
=====


.. image:: https://img.shields.io/pypi/v/ratot.svg
        :target: https://pypi.python.org/pypi/ratot

.. image:: https://img.shields.io/travis/skeledrew/ratot.svg
        :target: https://travis-ci.org/skeledrew/ratot

.. image:: https://readthedocs.org/projects/ratot/badge/?version=latest
        :target: https://ratot.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/skeledrew/ratot/shield.svg
     :target: https://pyup.io/repos/github/skeledrew/ratot/
     :alt: Updates


Remote Access Tool Over Telegram


* Free software: GNU General Public License v3
* Documentation: https://ratot.readthedocs.io.


Description
-----------

Have you ever wanted to remotedly access your personal computer or server? Have you ever wanted to do it without setting up port forwarding or otherwise making your accessible to the world? How about without using a solution such as Teamviewer (of which I've been a faithful user for years), which only provides a graphical interface, and so is suseptible to bad connections?

Enter RAToT, a tool to allow access to Bash (and eventually other command line oriented apps) using a Telegram messenger app. Written in Python, it leverages the Telegram bot platform to bridge the gap between a remote machine, and whatever device you have at hand that can run a Telegram client. Just use as if you're chatting with someone.

And now for a totally random and unnecessary statment: This is only possible because Telegram is the best messaging service out there!


Features
--------

* Allows remote control of Bash on a system from Telegram.

* Built on Linux in Python3, tested on Mac. Windows is not an option (unless someone contributes).


Installation
------------

1) Fork this project if you would like to contribute.

2) Clone from this repo or your own fork.

3) Setup and activate a virtualenv for the project. The author recommends `pyenv`.

4) Install the requirements (and optionally requirements_dev).

5) Patch the following files in your Python's site-packages folder:

  a) In pexpect/__init__.py add ``import replwrap`` (issue possibly already fixed in latest pexpect version)

  b) In rpyc/__init__.py add ``from rpyc.utils import server``

6) Copy the .env.template file to .env

7) Visit the BotFather in your Telegram, create a bot and copy the token.

8) Add the bot token and other information to your .env:

  * ``$ dotenv set TOKEN your-bot-token``

  * ``$ dotenv set ADMINS your-telegram-username`` (set one if needed in your profile)

  * You may also change the HOST and PORT if you wish and know what you're doing.

9) Start the server and router bot on your machine:

  a) ``$ cd ratot``

  b) ``$ ./server.py``

  c) ``$ ./router.py``

10) Find your bot in Telegram by the username you gave to the BotFather, and /start it. If all goes well you should get a welcome message and can now start sending commands to your machine.

11) Setup the "telewrap" client (alpha, optional):

  a) Go to telegram.org, sign in and create an app.

  b) Grap the API ID and API hash.

  c) Add to the .env as API_ID and API_HASH.

  d) Add your registered phone numer as PHONE; format `+1234567890`.

  e) Optionally change the default SESSION_NAME.

  f) Run client with ``$ ./telewrap.py`` (ACTUALLY DON'T DO THIS; CURRENTLY INCOMPLETE & BROKEN)

  g) Wait for fix or contribute one [see f].


TODO
----

* Bring client to working state

* Fix broken repo things

* Make a patcher

* Implement file transfer and syncing

* Implement multiple session handling

* Work on docs

* Support more shells and interpreters (Python, xonsh, etc)


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

