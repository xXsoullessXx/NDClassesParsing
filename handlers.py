from telebot import types
import json
import sql_requests


def setup_handlers(bot):
    user_states = {}
    possible_states = {
        'crn to add into notification list',
        'crn to delete from notification list'
        }

    async def create_edit_stop_markup():
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
        edit_list_button = types.KeyboardButton('Edit class list')
        stop_parsing_button = types.KeyboardButton('Stop (delete CRNs)')
        markup.add(edit_list_button, stop_parsing_button)
        return markup

    @bot.message_handler(commands=['start'])
    async def start_command(message):
        msg_text = await sql_requests.start_sql_request(message, 'users.db')
        await bot.send_message(message.chat.id, msg_text, reply_markup=await create_edit_stop_markup())

    async def create_add_delete_markup():
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
        markup.add(
            types.KeyboardButton('Add class'),
            types.KeyboardButton('Delete class'),
            types.KeyboardButton('Your class list'),
            row_width=2  # Ensures buttons appear side-by-side
        )
        return markup

    async def edit_crn_list_handler(message):
        await bot.send_message(message.chat.id, 'Choose an option', reply_markup=await create_add_delete_markup())

    async def stop_handler(message):
        await sql_requests.delete_crns(message, 'users.db')
        await bot.send_message(message.chat.id, 'stopped', reply_markup=await create_edit_stop_markup())

    @bot.message_handler(func=lambda msg: msg.text in ['Edit class list', 'Stop searching seats (delete CRNs)'])
    async def edit_stop_handler(message):
        match message.text:
            case 'Stop searching seats (delete CRNs)':
                await stop_handler(message)
            case 'Edit class list':
                await edit_crn_list_handler(message)
            case _:
                pass

    async def get_list_of_crns(message, database):
        return await sql_requests.get_crns(message, database)

    async def update_crns(message, crns):
        crns_json = json.dumps(crns)
        await sql_requests.update_crns(message, crns_json, 'users.db')

    async def add_class_handler(message):
        await bot.send_message(message.chat.id, 'Write CRN of the class')
        user_states[message.chat.id] = 'crn to add into notification list'

    async def delete_class_handler(message):
        await bot.send_message(message.chat.id, 'Write CRN of the class')
        user_states[message.chat.id] = 'crn to delete from notification list'

    async def adding_class(message, database):
        crns = await get_list_of_crns(message, database)
        if message.text in crns:
            msg_txt = 'You\'ve already added this class'

        else:
            crns.append(message.text)
            await update_crns(message, crns)
            msg_txt = 'I\'ve added this class.'
        await bot.send_message(message.chat.id, msg_txt, reply_markup=await create_add_delete_markup())

    async def deleting_class(message, database):
        crns = await get_list_of_crns(message, database)
        if message.text not in crns:
            msg_txt = 'You haven\'t got this class in the list'
        else:
            crns.remove(message.text)
            await update_crns(message, crns)
            msg_txt = 'I\'ve deleted this class.'
        await bot.send_message(message.chat.id, msg_txt, reply_markup=await create_add_delete_markup())

    async def show_class_list_handler(message, database):
        try:
            # Get CRNs with error handling
            crns = await sql_requests.get_crns(message.chat.id, database)  # Note: Changed to message.chat.id
            if not crns:
                await bot.send_message(
                    message.chat.id,
                    "Your notification list is empty",
                    reply_markup=await create_add_delete_markup()
                )
                return

            # Build message text efficiently
            msg_text = "\n".join(str(crn) for crn in crns)

            # Split long messages (Telegram has 4096 character limit)
            max_length = 3000  # Safe margin below Telegram's limit
            if len(msg_text) > max_length:
                chunks = [msg_text[i:i + max_length] for i in range(0, len(msg_text), max_length)]
                for chunk in chunks:
                    await bot.send_message(message.chat.id, chunk)
                # Send markup only with last message
                await bot.send_message(
                    message.chat.id,
                    f"Showing {len(crns)} tracked courses",
                    reply_markup=await create_add_delete_markup()
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    f"Your tracked courses:\n{msg_text}",
                    reply_markup=await create_add_delete_markup()
                )

        except Exception as e:
            error_msg = f"Failed to show class list: {str(e)}"
            print(error_msg)
            await bot.send_message(
                message.chat.id,
                "⚠️ Couldn't retrieve your course list. Please try again later."
            )

    @bot.message_handler(func=lambda msg: msg.text in ['Add class', 'Delete class', 'Your class list'])
    async def add_delete_class_handler(message):
        match message.text:
            case 'Add class':
                await add_class_handler(message)
            case 'Delete class':
                await delete_class_handler(message)
            case 'Your class list':
                await show_class_list_handler(message, 'users.db')
            case _:
                pass

    @bot.message_handler(func=lambda msg: user_states[msg.chat.id] in possible_states)
    async def awaited_messages_handling(message):

        match user_states[message.chat.id]:
            case 'crn to add into notification list':
                await adding_class(message, 'users.db')
            case 'crn to delete from notification list':
                await deleting_class(message, 'users.db')
            case _:
                pass



    return bot

