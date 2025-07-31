import asyncio
from telebot.async_telebot import AsyncTeleBot
import parsing_info
import sql_requests
from handlers import setup_handlers
# Config
scheduletime = 150
bot_token = '6884375984:AAECZ0NtylET5gjrl5e4NztjEoirsAQVDNo'

bot = setup_handlers(AsyncTeleBot(bot_token))


async def parsing_all_the_info():
    chat_ids = await sql_requests.get_chat_ids('users.db')
    for user_id_tuple in chat_ids:
        user_id = user_id_tuple[0]
        crns = await sql_requests.get_crns(user_id, 'users.db')
        if crns:
            for crn in crns:
                await parsing_info.send_notification(bot, user_id, crn, 3)


async def scheduled_task():
    while True:
        await parsing_all_the_info()
        await asyncio.sleep(scheduletime)


async def main():
    await asyncio.gather(
        bot.polling(non_stop=True),
        scheduled_task()
    )

if __name__ == '__main__':
    asyncio.run(main())