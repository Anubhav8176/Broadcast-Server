import asyncio

HOST = "0.0.0.0"
PORT = 9000

clients: dict[str, asyncio.StreamWriter] = {}

async def send(writer: asyncio.StreamWriter, text: str)->None:
    try:
        writer.write((text+"\n").encode())
        await writer.drain()
    except (ConnectionError, OSError):
        pass

async def broadcast(text: str, exclude: str | None = None) -> None:
    targets = [w for name, w in clients.items() if name != exclude]
    await asyncio.gather(*(send(w, text) for w in targets))

# This function handles both clients(Reader: Incoming bytes, Writer: Outgoing bytes)
async def handle_clients(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    name = None
    try:
        await send(writer, "Enter your username: ")
        while True:
            line = await reader.readline()
            if not line:
                return
            candidate = line.decode().strip()
            if not candidate:
                await send(writer, "Username can't be empty. Try again!")
            elif candidate is clients:
                await send(writer, "Username taken. Try again!!")
            else:
                name = candidate
                break

        clients[name] = writer
        print(f"[*] {name} connected from {addr}")

        await send(writer, f"Welcome, {name}! Online: {','.join(clients)}")
        await send(writer, "Type /users to list users, /quit to leave.")
        await broadcast(f"* {name} joined the chat", exclude = name)

        while True:
            line = await reader.readline()
            if not line:
                break
            msg = line.decode().strip()
            if not msg:
                continue
            if msg == "/quit":
                break
            if msg == "/users":
                await send(writer, f"Online ({len(clients)}): {','.join(clients)}")
                continue
            await broadcast(f"{name}: {msg}", exclude=name)

    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    finally:
        if name and clients.get(name) is writer:
            del clients[name]
            print(f"[-] {name} disconnected")
            await broadcast(f" {name} left the chat")

        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass


# It is the main entry point of the entire program
async def main():
    server = await asyncio.start_server(client_connected_cb=handle_clients, host=HOST, port=PORT)
    print(f"\nServer is listening with hosts: {HOST} and on port {PORT}.")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")