from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup as MarkupKeyboard,
    InlineKeyboardButton as ButtonKeyboard,
)
from core.bot import Bot
from core.clients import user
from configs import config
from database.chat_database import ChatDB
from functions.decorators import authorized_only


def check_cmd(message: Message):
    return message.command[1].lower() if len(message.command) > 1 else ""


@Client.on_message(filters.new_chat_members)
async def new_member_(client: Client, message: Message):
    assistant_username = (await user.get_me()).username
    bot_id = (await client.get_me()).id
    for member in message.new_chat_members:
        if member.id == bot_id:
            ChatDB().add_chat(message.chat.id)
            return await message.reply(
                "𝐇𝐈,𝐈'𝐌 𝐀 𝐁𝐎𝐓 𝐌𝐔𝐒𝐈𝐂 .\n"
                "𝐌𝐀𝐊𝐄 𝐌𝐄 𝐀𝐒 𝐀𝐃𝐌𝐈𝐍 𝐈𝐍 𝐇𝐄𝐑𝐄 𝐖𝐈𝐓𝐇 𝐀𝐋𝐋 𝐏𝐄𝐑𝐌𝐈𝐒𝐒𝐈𝐎𝐍𝐒 𝐄𝐗𝐂𝐄𝐏𝐓 𝐀𝐍𝐎𝐍𝐘𝐌𝐎𝐔𝐒 𝐀𝐃𝐌𝐈𝐍 \n"
                "𝐓𝐎 𝐔𝐒𝐄 𝐌𝐄, 𝐏𝐋𝐄𝐀𝐒𝐄 𝐔𝐒𝐄 /𝐮𝐬𝐞𝐫𝐛𝐨𝐭𝐣𝐨𝐢𝐧 𝐂𝐎𝐌𝐀𝐍𝐃.\n"
                "𝐓𝐇𝐀𝐍𝐊𝐒 𝐅𝐎𝐑 𝐈𝐍𝐕𝐈𝐓𝐈𝐍𝐆 𝐌𝐄 𝐓𝐎 𝐇𝐄𝐑𝐄.\n" 
                "𝐃𝐎𝐍'𝐓 𝐅𝐎𝐑𝐆𝐄𝐓 𝐓𝐎 𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋",   
                
                reply_markup=MarkupKeyboard(
                    [
                        [
                            ButtonKeyboard("Channel", url=config.CHANNEL_LINK),
                            ButtonKeyboard("Support", url=config.GROUP_LINK),
                        ],
                        [
                            ButtonKeyboard(
                                "Assistant", url=f"https://t.me/{assistant_username}"
                            ButtonKeyboard("Owner", url=f"https://t.me/{owner_username}
                            )
                        ],
                    ]
                ),
            )


@Client.on_message(filters.command("addchat"))
@authorized_only
async def add_chat_(_, message: Message):
    try:
        lang = (await message.chat.get_member(message.from_user.id)).user.language_code
    except (AttributeError, ValueError):
        lang = "en"
    if cmds := message.command[1:]:
        for chat_id in cmds:
            ChatDB().add_chat(int(chat_id), lang)
        return await Bot().send_message(message.chat.id, "success_add_chats")
    add_status = ChatDB().add_chat(message.chat.id, lang)
    return await Bot().send_message(message.chat.id, add_status)


@Client.on_message(filters.command("delchat"))
@authorized_only
async def del_chat_(_, message: Message):
    if cmds := message.command[1:]:
        for chat_id in cmds:
            ChatDB().del_chat(int(chat_id))
        return await Bot().send_message(message.chat.id, "success_delete_chats")
    del_status = ChatDB().del_chat(message.chat.id)
    return await Bot().send_message(message.chat.id, del_status)


@Client.on_message(filters.command("setadmin"))
@authorized_only
async def set_admin_(_, message: Message):
    cmd = check_cmd(message)
    if cmd not in ["yes", "true", "on", "no", "false", "off"]:
        return await Bot().send_message(message.chat.id, "invalid_command_selection")
    only_admin = bool(cmd in ["yes", "true", "on"])
    admin_set = ChatDB().set_admin(message.chat.id, only_admin)
    return await Bot().send_message(message.chat.id, admin_set)


@Client.on_message(filters.command("setquality"))
@authorized_only
async def set_quality_(_, message: Message):
    if cmd := check_cmd(message):
        if cmd not in ["low", "medium", "high"]:
            return await Bot().send_message(
                message.chat.id, "invalid_quality_selection"
            )
        key = ChatDB().set_quality(message.chat.id, cmd)
        return await Bot().send_message(message.chat.id, key, cmd)


@Client.on_message(filters.command("delcmd"))
@authorized_only
async def set_del_cmd_(_, message: Message):
    cmd = check_cmd(message)
    if cmd not in ["on", "yes", "true", "off", "no", "false"]:
        return await Bot().send_message(
            message.chat.id, "invalid_command_selection"
        )
    del_cmd = bool(cmd in ["on", "yes", "true"])
    key = ChatDB().set_del_cmd(message.chat.id, del_cmd)
    return await Bot().send_message(message.chat.id, key, cmd)


@Client.on_message(filters.command("reloaddb") & filters.user(config.OWNER_ID))
async def reload_db_(_, message: Message):
    ChatDB().reload_data()
    return await Bot().send_message(message.chat.id, "db_reloaded")


@Client.on_message(filters.command("player") & filters.group)
@authorized_only
async def set_player_mode(_, message: Message):
    chat_id = message.chat.id
    cmd = check_cmd(message)
    set_play_mode = bool(cmd in ["on", "yes", "true"])
    key = ChatDB().set_player_mode(chat_id, set_play_mode)
    return await Bot().send_message(chat_id, key, cmd)


@Client.on_message(filters.command("setduration") & filters.group)
@authorized_only
async def set_duration_limit(_, m: Message):
    chat_id = m.chat.id
    duration = int(m.command[1])
    key = ChatDB().set_duration_limit(chat_id, duration)
    return await Bot().send_message(chat_id, key, str(duration))

__cmds__ = [
    "addchat",
    "delchat",
    "setadmin",
    "setquality",
    "delcmd",
    "reloaddb",
    "player",
    "setduration"
]
__help__ = {
    "addchat": "help_addchat",
    "delchat": "help_delchat",
    "setadmin": "help_setadmin",
    "setquality": "help_setquality",
    "delcmd": "help_delcmd",
    "reloaddb": "help_reloaddb",
    "player": "help_player",
    "setduration": "help_setduration"
}
