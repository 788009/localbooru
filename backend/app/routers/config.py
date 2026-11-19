from fastapi import APIRouter
from app.indexer import indexer
from app.schemas import ConfigResponse, DirectoryInfo

router = APIRouter(prefix="/api/config", tags=["config"])

@router.get("", response_model=ConfigResponse)
def get_config():
    cfg = indexer.config
    dirs = []
    for d in cfg.storage.directories:
        dirs.append(DirectoryInfo(
            path=d,
            name=indexer.dir_names.get(d, d),
            default=(d in cfg.storage.default_selected)
        ))
    return ConfigResponse(
        directories=dirs,
        default_page_size=cfg.ui.default_page_size
    )
