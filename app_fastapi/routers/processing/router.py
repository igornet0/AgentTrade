from fastapi import APIRouter

router = APIRouter(prefix="/process", tags=["Processing"])

@router.get("/")
async def get_users():
    return {"message": "All users list"}

@router.post("/create")
async def create_user():
    return {"message": "User created"}