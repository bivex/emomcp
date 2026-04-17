"""Entry point for emomcp server."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import uvicorn
from emomcp.infrastructure.config import load_config
from emomcp.presentation.app import create_app


def main() -> None:
    config = load_config()
    app = create_app(config)
    uvicorn.run(
        app,
        host=config["server"]["host"],
        port=config["server"]["port"],
        log_level=config["logging"]["level"].lower(),
    )


if __name__ == "__main__":
    main()
