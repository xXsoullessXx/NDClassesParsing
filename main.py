import asyncio
import os
import schedule
import time
import telebot
from telebot.async_telebot import AsyncTeleBot
import sqlite3 as sql
from parsing_info import check_course_status
import json


# Configuration
scheduletime = 150  # seconds
bot_token = '6884375984:AAECZ0NtylET5gjrl5e4NztjEoirsAQVDNo'
bot_chatID = '779703230'

# Initialize async Telegram bot
bot = AsyncTeleBot(bot_token)

@bot.message_handler(commands =['start'])
async def start_command(message):
    await bot.send_message(message.chat.id, "Hello, I've already added you to my system.\nI can help to get a free place at your classes.\n Write /help to get a list of commands.")
    with sql.connect("users.db") as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            crns TEXT
            )
        """)
        con.commit()
        cur.execute(f"""
        SELECT * FROM users WHERE chat_id ='{message.chat.id}' 
        """)
        if cur.fetchone() == None:
            cur.execute(f"""
            INSERT INTO users (chat_id, crns) VALUES ('{message.char.id}', '')
            """)
            con.commit()






async def send_notification():
    course_title, status = await check_course_status()

    if status == 1:
        message = f"🚨 COURSE AVAILABLE! 🚨\n\n{course_title}\n\nGo register now!"
        await bot.send_message(bot_chatID, message)
    elif status == -1:
        error_msg = "⚠️ Error checking course status. Please check the script."
        await bot.send_message('779703230', error_msg)


def run_async_job():
    asyncio.run(send_notification())


# Schedule the job
schedule.every(scheduletime).seconds.do(run_async_job)

# Initial run
run_async_job()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)