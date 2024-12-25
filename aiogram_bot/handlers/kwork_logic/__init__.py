from aiogram import Router
from .kwork_settings_callback import kwork_settings_router

kwork_logic_router = Router()

kwork_logic_router.include_router(kwork_settings_router)
