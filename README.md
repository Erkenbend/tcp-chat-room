# TCP Chat Room

Python implementation of a simple chat room using TCP protocol.

**Credit for idea and original code**: [NeuralNine](https://www.youtube.com/channel/UC8wZnXYK_CGKlBcZp-GxYPA)
(see videos on the topic, [basic](https://www.youtube.com/watch?v=3UOyky9sEQY)
and [advanced](https://www.youtube.com/watch?v=F_JDA96AdEI)).

**Disclaimer**: this is not meant to be applicable in any sort of production environment;
it is totally unsecure, utterly unstable, and extremely buggy. But it was fun to make. 

## Requirements

Plain Python 3, nothing more required. Version 3.8+ recommended.

## Usage

Run the server with `python server.py`. Add clients in other terminals with `python client.py`
and start chatting in the command line. If using multiple machines, change server address
accordingly.

On Windows, prefer the CMD as the Git-Bash console does not work well with background
threads.

## Features

### Messaging

Only broadcast messages supported: all other clients in the chat room receive your
messages.

### Commands

Supported commands:
* `/admin` -- become admin
* `/quit` -- quit the chat room
* `/exit` -- same as `/quit`
  
Supported admin commands:
* `/online` -- show online users list
* `/kick abc` -- kick user `abc`
* `/ban abc` -- kick and ban user `abc` (prevent reconnection)
* `/unban abc` -- unban user `abc` (remove from ban list)
* `/banned` -- show banned users list

## Conventions

Commands should start with `/` -- example: `/admin`

Special server instructions should be surrounded by `%` -- example: `%QUIT%`
