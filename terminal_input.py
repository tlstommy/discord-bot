# terminal_input.py
import threading
import asyncio
import shlex

def start_terminal_input(bot, channel_id):
    def read_input():
        while True:
            try:
                raw = input("[Terminal Command]>>: ").strip()
                if not raw:
                    continue

                try:
                    parts = shlex.split(raw)
                except ValueError as e:
                    print(f"Error parsing input: {e}")
                    continue

                if parts[0].lower() == "!say":
                    if len(parts) < 2:
                        print("Usage: !say \"your message here\"")
                        continue

                    message = " ".join(parts[1:])
                    asyncio.run_coroutine_threadsafe(
                        send_to_channel(bot, channel_id, message), bot.loop
                    )

                elif parts[0].lower() == "!exit":
                    print("Exiting terminal input loop...")
                    break

                else:
                    print(f"Unknown command: {parts[0]}")
            except (EOFError, KeyboardInterrupt):
                print("Terminal input interrupted. Exiting loop...")
                break

    threading.Thread(target=read_input, daemon=True).start()

async def send_to_channel(bot, channel_id, message):
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            await channel.send(f"{message}")
        except Exception as e:
            print(f"Failed to send message: {e}")
    else:
        print(f"Channel with ID {channel_id} not found.")
