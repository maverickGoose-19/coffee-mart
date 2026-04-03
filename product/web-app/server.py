from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

from product.backend.app.config import settings


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    port = int(os.environ.get("PORT", str(settings.port)))
    host = os.environ.get("HOST", settings.host)
    reload = os.environ.get("RELOAD", "false").lower() == "true"
    workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
    uvicorn.run(
        "product.backend.app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else max(workers, 1),
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
