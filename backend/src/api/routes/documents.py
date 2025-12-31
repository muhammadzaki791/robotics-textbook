from fastapi import APIRouter

router = APIRouter(tags=["documents"])

@router.get("/")
async def get_documents():
    return {"message": "Documents endpoint"}