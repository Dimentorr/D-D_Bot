from pyrogram import Client, filters
from Tools.JsonTools import CatalogJson

env = CatalogJson(name='file/json/environment.json')

api_id = env.read_json_data('api_id_pyrogram')
api_hash = env.read_json_data('api_hash_pyrogram')


def supergroup_create():
    # ids = [users_id]  # Айди пользователей, которые будут добавлены
    # app.create_group("имя группы2", users=ids)
    app.create_supergroup("имя группы2")


with Client("my_account", api_id, api_hash) as app:
    app.send_message("me", "Greetings from --Pyrogram--!")
    # supergroup_create()

