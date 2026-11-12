# Broadcast Server

A simple multi-client broadcast chat server built with Python's `asyncio`. Clients connect over TCP, pick a username, and every message one client sends is broadcast to all the other connected clients. The server also keeps a live list of connected users.

## Project background

This project is a solution to the [Broadcast Server](https://roadmap.sh/projects/broadcast-server) project from [roadmap.sh](https://roadmap.sh), which is about understanding how real-time features such as chat apps and live scoreboards work. The goals of that project are:

- a server that tracks connected clients and broadcasts each client's message to all of them
- handling multiple clients joining and leaving smoothly
- error handling and graceful shutdown

This implementation uses plain TCP sockets with `asyncio` rather than WebSockets, and it is started with `python server.py` and `python client.py` rather than a `broadcast-server start` / `connect` CLI.

## Features

- Handles many clients at once on a single event loop (no threads, no locks)
- Broadcasts each message to every other connected client
- Maintains a list of connected users, available on demand with `/users`
- Unique usernames (duplicates and empty names are rejected)
- Join and leave notifications
- Clean handling of disconnects, including abrupt ones
- Standard library only, with no dependencies

## Requirements

- Python 3.10 or newer

## Project structure

```
Broadcast-Server/
├── server.py   # asyncio TCP server: accepts clients and broadcasts messages
└── client.py   # terminal client: sends input and prints incoming messages
```

## Getting started

Clone the repository:

```bash
git clone https://github.com/Anubhav8176/Broadcast-Server.git
cd Broadcast-Server
```

### 1. Start the server

```bash
python server.py
```

You should see:

```
Broadcast server listening on 0.0.0.0:9000
```

### 2. Connect clients

Open one terminal per client and run:

```bash
python client.py
```

Enter a username when prompted, then start typing. To connect to a server on another machine:

```bash
python client.py <server-ip> 9000
```

On macOS and Linux you may need `python3` instead of `python`.

## Usage

| Input        | Effect                                           |
|--------------|--------------------------------------------------|
| any text     | Sent to all other connected clients              |
| `/users`     | Shows the list of users currently online         |
| `/quit`      | Disconnects from the server                      |

### Example session

**Terminal 1 (alice)**
```
Enter your username:
alice
Welcome, alice! Online: alice
* bob joined the chat
hello everyone
bob: hi alice!
```

**Terminal 2 (bob)**
```
Enter your username:
bob
Welcome, bob! Online: alice, bob
alice: hello everyone
hi alice!
```

## How it works

1. The server listens on a TCP port using `asyncio.start_server`.
2. Each new connection runs in its own coroutine, `handle_client`.
3. The client sends a username, which is registered in a shared `clients` dictionary (`username -> writer`).
4. Every line the client sends afterward is either a command (`/users`, `/quit`) or a chat message.
5. Chat messages are written to every other writer in the dictionary using `asyncio.gather`, so a slow client doesn't block the rest.
6. When a client quits or drops, a `finally` block removes it from the dictionary and notifies the others.

```
Client A ──┐                      ┌── Client B
Client C ──┼──► Broadcast Server ─┼── Client D
Client E ──┘     clients = {…}    └── …
```

## Configuration

Edit the constants at the top of `server.py`:

```python
HOST = "0.0.0.0"   # use "127.0.0.1" to accept local connections only
PORT = 9000
```

If other devices can't connect, allow the port through your firewall.

## Troubleshooting

- **`Address already in use`**: another process is using the port. Stop it or change `PORT`.
- **`Connection refused`**: the server isn't running, or the host or port is wrong.
- **`getaddrinfo failed`**: `HOST` is not a valid address. It should be just an IP or hostname, with no port or `http://`.
- **`coroutine 'start_server' was never awaited`**: add `await` before `asyncio.start_server(...)`.

## Limitations and ideas for improvement

- No authentication, so anyone can choose any free username
- No message history or persistence
- Plain-text, unencrypted traffic (TLS could be added with `ssl`)
- Possible extensions: private messages (`/msg user text`), chat rooms, WebSocket support for browser clients, and a separate backend layer for chat logic

## License

Add a license of your choice (for example, MIT).
