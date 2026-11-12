import asyncio, sys

HOST = sys.argv[1] if len(sys.argv)>1 else "127.0.0.1"
PORT = int(sys.argv[2] if len(sys.argv)>2 else 9000)

async def receive(reader: asyncio.StreamReader):
    while True:
        line = await reader.readline()
        if not line:
            print("Disconnected from server.")
            return
        print(line.decode().rstrip())

async def main():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    recv_task = asyncio.create_task(receive(reader))
    loop = asyncio.get_running_loop()

    try:
        while not recv_task.done():
            text = await loop.run_in_executor(None, sys.stdin.readline)
            if not text:
                break
            writer.write(text.encode())
            await writer.drain()
            if text.strip() == "/quit":
                break
    finally:
        recv_task.cancel()
        writer.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, ConnectionRefusedError):
        pass