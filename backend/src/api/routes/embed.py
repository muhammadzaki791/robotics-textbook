from fastapi import APIRouter

router = APIRouter(tags=["embedding"])

@router.post("/generate")
async def generate_embeddings():
    return {"message": "Embedding generation endpoint"}