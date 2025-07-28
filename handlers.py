from telebot import types
import sqlite3 as sql
import json
import sql_requests




def setup_handlers(bot):

    async def create_edit_stop_markup():
        markup = types.ReplyKeyboardMarkup()
        edit_list_button = types.KeyboardButton('Edit class list')
        stop_parsing_button = types.KeyboardButton('Stop searching seats')
        markup.add(edit_list_button, stop_parsing_button)
        return markup


    @bot.message_handler(commands=['start'])
    async def start_command(message):
        msg_text = sql_requests.start_sql_request(message)
        await bot.send_message(message.chat.id, msg_text, reply_markup=await create_edit_stop_markup())


    async def create_add_delete_markup():
        markup = types.ReplyKeyboardMarkup()
        add_crn_button = types.KeyboardButton('Add class')
        delete_crn_button = types.KeyboardButton('Delete class')
        markup.add(add_crn_button, delete_crn_button)
    async def edit_crn_list_handler(message):
        await bot.send_message(message.chat.id, 'Choose an option', reply_markup=await create_add_delete_markup()  )

    async def stop_handler(message):
        try:
            with sql.connect('users.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                    UPDATE users SET 
                    crns = ''
                    WHERE chat_id = {message.chat.id}
                """)
                con.commit()
        except sql.Error as error:
            print(f"SQL Error: {error}")



    @bot.message_handler(func=lambda msg: msg.text in ['Edit class list', 'Stop searching seats'])
    async def edit_stop_handler(message):
        match message.text:
            case 'Stop searching seats':
                await stop_handler(message)
            case 'Edit class list':
                await edit_crn_list_handler(message)
            case _:
                pass

    async def get_crns(chat_id):
        try:
            with sql.connect('users.db') as con:
                cur = con.cursor()
                cur.execute(f"""
                    SELECT crns FROM users WHERE chat_id = {chat_id}
                """)
                crns_json = cur.fetchone()
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


    async def update_crns(chat_id, crns):
        try:
            with sql.connect('users.db') as con:
                cur = con.cursor()



        except sql.Error as error:
            print(f"SQL Error: {error}")

    async def add_class_handler(message):
        await bot.send_message(message.chat.id, 'Write CRN of the class')
        await bot.register_next_step(message, adding_class)


    async def adding_class(message):
        crns = get_crns(message.chat.id)
        if message.text in crns:
            message.text =




    @bot.message_handler(func=lambda msg: msg.text in ['Add class', 'Delete class'])
    async def add_delete_class_handler(message):
        match message.text:
            case 'Add class':
                await add_class_handler(message)
            case 'Delete class':
                await delete_class_handler(message)
            case _:
                pass







    return bot

