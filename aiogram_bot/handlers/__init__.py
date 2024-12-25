from aiogram import Router
from .start_handler import start_router
from .kwork_logic import kwork_logic_router

handler_router = Router()

handler_router.include_router(start_router)
handler_router.include_router(kwork_logic_router)
