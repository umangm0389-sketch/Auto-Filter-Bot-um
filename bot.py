import sys
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
import time
import asyncio
from datetime import date, datetime
import pytz
from aiohttp import web
from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium 
from Lucia.Bot import SilentX
# from Lucia.util.keepalive import ping_server
from Lucia.Bot.clients import initialize_clients
import pyrogram.utils
from PIL import Image
from logging_helper import LOGGER

botStartTime = time.time()

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

# def ping_loop():
#     while True:
#         try:
#             r = requests.get(URL, timeout=10)
#             if r.status_code == 200:
#                 pass
#             else:
#                 LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
#         except Exception as e:
#             LOGGER.error(f"❌ Exception During Ping: {e}")
#             time.sleep(120)

# if URL:
#     threading.Thread(target=ping_loop, daemon=True).start()

async def SilentXBotz_start():
    LOGGER.info('Initializing Your Bot!')
    await SilentX.start()
    bot_info = await SilentX.get_me()
    SilentX.username = bot_info.username
    await initialize_clients()
    if 0 in SilentX.dispatcher.groups:
        all_handlers = list(SilentX.dispatcher.groups[0])
        for i, handler in enumerate(all_handlers):
            SilentX.dispatcher.remove_handler(handler, group=0)
            SilentX.dispatcher.add_handler(handler, group=i)
    if ON_HEROKU:
        asyncio.create_task(ping_server()) 
    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
    except Exception as e:
        LOGGER.error(f"Error fetching banned users/chats: {e}")

    if MULTIPLE_DB and not DATABASE_URI2:
        print("Error: DATABASE_URI2 Is Not Provided But MULTIPLE_DB Is Set To True. Please Fill The DATABASE_URI2 Ver !")
        sys.exit(1)
        
    try:
        await Media.ensure_indexes()
        if MULTIPLE_DB:
            await Media2.ensure_indexes()
            LOGGER.info("Multiple Database Mode On. Now Files Will Be Save In Second DB If First DB Is Full")
        else:
            LOGGER.info("Single DB Mode On ! Files Will Be Save In First Database")
    except Exception as e:
        LOGGER.error(f"Error ensuring indexes: {e}")
    me = await SilentX.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    SilentX.username = '@' + me.username
    SilentX.loop.create_task(check_expired_premium(SilentX))
    LOGGER.info(f"{me.first_name} with Pyrofork v{__version__} (Layer {layer}) started on {me.username}.")
    LOGGER.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    try:
        await SilentX.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time_str))
    except Exception as e:
        LOGGER.error(f"Error Sending Restart Log: {e}")
        pass
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(SilentXBotz_start())
    except KeyboardInterrupt:
        LOGGER.info('Service Stopped Bye 👋')
