"""Guard: the app implements exactly the endpoints of the committed contract."""

import json
from pathlib import Path

from app.main import app

SPEC = json.loads(
    (Path(__file__).resolve().parents[2] / "spec" / "openapi" / "openapi.json").read_text(
        encoding="utf-8"
    )
)


def test_every_contract_operation_is_implemented() -> None:
    implemented = app.openapi()["paths"]
    for path, operations in SPEC["paths"].items():
        assert path in implemented, f"{path} is missing from the app"
        for method in operations:
            assert method in implemented[path], f"{method.upper()} {path} is missing"


def test_app_exposes_no_undocumented_paths() -> None:
    spec_paths = set(SPEC["paths"])
    for path in app.openapi()["paths"]:
        assert path in spec_paths, f"{path} is not part of the contract"
