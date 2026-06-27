from fastapi import APIRouter

router = APIRouter()

# Import all routes from voice_cmd module
from . import voice_cmd
