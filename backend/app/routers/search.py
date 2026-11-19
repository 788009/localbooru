from fastapi import APIRouter, Query
from app.indexer import indexer
from app.schemas import AutocompleteItem, SearchRequest, SearchResponse

router = APIRouter(prefix="/api/search", tags=["search"])

@router.get("/autocomplete", response_model=list[AutocompleteItem])
def autocomplete(q: str = Query(..., min_length=1)):
    return indexer.autocomplete(q)

@router.post("", response_model=SearchResponse)
def search(req: SearchRequest):
    pos_tags = []
    neg_tags = []
    
    for t in req.tags:
        if t.startswith("-"):
            if len(t) > 1:
                neg_tags.append(t[1:])
        else:
            pos_tags.append(t)

    return indexer.search(pos_tags, neg_tags, req.directories, req.skip, req.limit)
