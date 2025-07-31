import aiosqlite as sql
import json
from multipledispatch import dispatch
from telebot import types

#Used for starting bot, returns message_text
async def start_sql_request(message, database):
    msg_text = 'Choose an option'
    try:
        async with sql.connect(database) as con:
            cur = await con.cursor()
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                chat_id TEXT PRIMARY KEY,
                crns TEXT
                )
            """)
            await con.commit()
            await cur.execute(f"""
            SELECT * FROM users WHERE chat_id ='{message.chat.id}' 
            """)
            if await cur.fetchone() is None:
                msg_text = "Hello, I've already added you to my system.\nI can help to get a free seat at your classes.\n Write /help to get a list of commands."
                await cur.execute(f"""
                INSERT INTO users (chat_id, crns) VALUES ('{message.chat.id}', '')
                """)
                await con.commit()
    except sql.Error as error:
        print(f"SQL Error: {error}")
    return msg_text

async def delete_crns(message, database):
    try:
        async with sql.connect(database) as con:
            cur = await  con.cursor()
            await cur.execute(f"""
                UPDATE users SET 
                crns = ''
                WHERE chat_id = {message.chat.id}
            """)
            await con.commit()
    except sql.Error as error:
        print(f"SQL Error: {error}")


@dispatch(int, str)
async def get_crns(chat_id, database):
    try:
        async with sql.connect(database) as con:
            cur = await con.cursor()
            await cur.execute(f"""
                SELECT crns FROM users WHERE chat_id = {chat_id}
            """)
            crns_json = await cur.fetchone()

            if crns_json and crns_json[0]:  # Check if data exists and isn't empty
                try:
                    crns = json.loads(crns_json[0])

                except json.JSONDecodeError:
                    print("Invalid JSON data in database")
            else:
                crns = []
        return crns
    except sql.Error as error:
        print(f"SQL Error: {error}")

@dispatch(str, str)
async def get_crns(chat_id, database):
    return await get_crns(int(chat_id), database)

@dispatch(types.Message, str)
async def get_crns(message, database):
    return await get_crns(message.chat.id, database)


async def update_crns(message, crns, database):
    try:
        async with sql.connect(database) as con:
            cur = await con.cursor()
            await cur.execute(
                "UPDATE users SET crns = ? WHERE chat_id = ?",
                (crns, message.chat.id)
            )
            await con.commit()
    except sql.Error as error:
        print(f"SQL Error: {error}")


async def get_chat_ids(database):
    try:
        async with sql.connect(database) as con:
            cur = await con.cursor()
            await cur.execute("""
                SELECT chat_id
                FROM users
            """)
            chat_ids = await cur.fetchall()
            return chat_ids
    except sql.Error as error:
        print(f"SQL Error: {error}")