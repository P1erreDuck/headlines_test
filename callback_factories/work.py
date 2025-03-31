from typing import Optional, Any
from aiogram.filters.callback_data import CallbackData


class WorkCD(CallbackData, prefix="work"):
    menu: str
    action: Optional[str] = None
    arg: Optional[int] = None
    category_id: int | None = None