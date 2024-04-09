import pyrogram
from pyrogram import Client

import os
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('api_id_pyrogram')
api_hash = os.getenv('api_hash_pyrogram')


def set_privileges(invite=False):
    return pyrogram.types.ChatPrivileges(can_manage_chat=invite,
                                         can_delete_messages=True,
                                         can_manage_video_chats=True,
                                         can_restrict_members=True,
                                         can_promote_members=True,
                                         can_change_info=True,
                                         can_post_messages=True,
                                         can_edit_messages=True,
                                         can_invite_users=invite,
                                         can_pin_messages=True)


async def supergroup_create(title: str, bot_name: str, user_name: str, admin_gm=True):
    app = Client("my_account", api_id, api_hash)
    await app.start()
    result = await app.create_supergroup(title)
    chat_id = result.id
    await app.add_chat_members(chat_id, bot_name)
    await app.add_chat_members(chat_id, f'@{user_name}')
    await app.promote_chat_member(chat_id, bot_name, privileges=set_privileges(invite=True))
    await app.promote_chat_member(chat_id, f'@{user_name}', privileges=set_privileges())
    if not admin_gm:
        await app.leave_chat(chat_id, delete=True)
    await app.stop()
    return chat_id

