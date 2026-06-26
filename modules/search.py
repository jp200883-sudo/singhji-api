from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def search_home():
    return {"module": "search", "status": "ok"}

@router.get("/query")
def search_query(q: str = ""):
    return {
        "query": q,
        "results": [
            {"title": f"Result 1 for {q}", "url": "https://example.com/1"},
            {"title": f"Result 2 for {q}", "url": "https://example.com/2"},
            {"title": f"Result 3 for {q}", "url": "https://example.com/3"}
        ],
        "source": "mock"
    }
