import asyncio
import sqlite3 as sql
from telebot.async_telebot import AsyncTeleBot
from parsing_info import check_course_status
from handlers import setup_handlers
# Config
scheduletime = 150  # seconds
bot_token = '6884375984:AAECZ0NtylET5gjrl5e4NztjEoirsAQVDNo'

bot = setup_handlers(AsyncTeleBot(bot_token))


async def send_notification(chat_id, crn, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            course_title, status = await check_course_status(crn)
            if status == 1:
                message = f"🚨 COURSE AVAILABLE! 🚨\n\n{course_title}\n\nGo register now!"
                await bot.send_message(chat_id, message)
                break
            elif status == -1:
                error_msg = "⚠️ Error checking course status."
                await bot.send_message(chat_id, error_msg)
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"Failed after {max_attempts} attempts: {e}")
            await asyncio.sleep(2)

async def scheduled_task():
    while True:
        await send_notification('779703230', '10929')
        await asyncio.sleep(scheduletime)

async def main():
    await asyncio.gather(
        bot.polling(non_stop=True),
        scheduled_task()
    )

if __name__ == '__main__':
    asyncio.run(main())