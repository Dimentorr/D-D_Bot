import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, Router


load_dotenv(dotenv_path='.env')

bot = Bot(token=os.getenv('TOKEN'))
router = Router()
dp = Dispatcher()
dp.include_router(router)
