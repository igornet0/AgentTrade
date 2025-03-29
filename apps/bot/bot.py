import asyncio
import subprocess, os
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from sys import argv

API_TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=os.getenv('API_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
queue = asyncio.Queue()

admin_id = 880629533

async def run_main():
    print('python', *ARGS)
    process = await asyncio.create_subprocess_exec('python', *ARGS, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    while True:
        stdout, stderr = await process.communicate()
        output = stdout.decode('utf-8') if stdout else "Error"
        await queue.put(output)
        if process.returncode:
            break

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Привет! Я запущу main.py и пришлю тебе результат.")
    asyncio.create_task(run_main())
    asyncio.create_task(process_queue())

async def process_queue():
    while True:
        message = str(await queue.get())
        print(message)
        await bot.send_message(admin_id, message)

async def main() -> None:
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == '__main__':
    skript, *l = argv
    ARGS = l
    print("[INFO] START bot")
    asyncio.run(main())
    print("[INFO] END bot")
