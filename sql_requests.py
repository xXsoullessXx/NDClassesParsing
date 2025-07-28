import aiosqlite as sql

#Used for starting bot, returns message_text
async def start_sql_request(message):
    msg_text = 'Choose an option'
    try:
        async with sql.connect("users.db") as con:
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
            if cur.fetchone() is None:
                msg_text = "Hello, I've already added you to my system.\nI can help to get a free seat at your classes.\n Write /help to get a list of commands."
                await cur.execute(f"""
                INSERT INTO users (chat_id, crns) VALUES ('{message.chat.id}', '')
                """)
                await con.commit()
    except sql.Error as error:
        print(f"SQL Error: {error}")
    return msg_text