"""""""""""""""""""
PROJECT OVERVIEW
"""""""""""""""""""

This is the app for emulating any kind of connectivity protocols over UDP/TCP layer. Useful for prototyping, for example, drivers or creating testing software.


:Key features:

- cross-platform PyQt-based app (Win, -nix, tested on Win 10 and Xubuntu);
- creation of your own logical/network level packets;
- support of TCP-server, TCP-client, and UDP modes (raw-socket mode planned) and on-the-fly switching between them;
- automatic receipting;
- support of your own custom control sum algorithms;
- programming emulator’s behavior: creating conditions (e.g. receiving one or few messages, passing specified amount of time since app’s start) and assigning actions to them (responding with one or few messages, switching to different behavior mode with different set of actions applied to conditions, etc).


:Unfinished:

- logger functionality: turning off parsing, changing fonts and colors, search, separate log for key messages;
- conditions: time passed after receiving, time passed after sending;
- raw-socket mode support – never been tested;
- grouping fields (some fields can be grouped together and repeated one or more times in one message; feature for older systems) – used to work, but after some major changes was never brought up to speed;
- setting up maximum message length and splitting up messages of greater length at sending (feature for older systems);
- localization and translation not completed.


:Code notes:

- no QtDesigner and .pro files used; all graphics programmed for better compatibility;
- camel case notation was used instead of Pythonic snake notation (to keep code in line with “camel cased” Qt library. Probably a mistake in hindsight);
- inconsistent decisions – this is my first Python app, so some code decisions may seem too C-like. In some places it was fixed, and Python-style decisions were applied, in some it wasn’t.


:Known issues:

- when there are no clients connected but there is an attempt to send a message, no resending is attempted;
- bug when creating new message types (see docs).

:Credits:

- UI icons by Flaticon: https://www.flaticon.com/uicons
- I really don’t want to get sued. Great icons. Seemingly free. Didn’t read fine print.
