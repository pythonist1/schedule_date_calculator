from fastapi import APIRouter
from pydantic import BaseModel

from src.date_calculator import Calculator


class EntryParams(BaseModel):
    entry_date: str
    scheduler_params: str


router = APIRouter()


@router.post("/calculate_date/")
def calculate_date(entry_params: EntryParams):
    calculator = Calculator()
    return calculator.calculate_date(entry_params.entry_date, entry_params.scheduler_params)
