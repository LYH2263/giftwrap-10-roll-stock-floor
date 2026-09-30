from fastapi import APIRouter, HTTPException
from app.repositories import papers as repo
from app.schemas.paper import PaperUpdate
router = APIRouter()
@router.get("/papers")
def list_papers(): return {"items": repo.list_papers()}
@router.put("/papers/{pid}")
def update_paper(pid: int, body: PaperUpdate):
    if not repo.update_paper(pid, body.roll_width, body.stock_len):
        raise HTTPException(404)
    return repo.get_paper(pid)
