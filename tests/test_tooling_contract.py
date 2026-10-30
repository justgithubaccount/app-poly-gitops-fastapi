import json
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_compose_healthcheck_uses_runtime_python() -> None:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    command = compose["services"]["api"]["healthcheck"]["test"]

    assert command[:2] == ["CMD", ".venv/bin/python"]
    assert "urllib.request" in command[3]
    assert "curl" not in command


def test_task_checks_are_non_mutating_and_fix_is_explicit() -> None:
    taskfile = yaml.safe_load((ROOT / "Taskfile.yaml").read_text())
    tasks = taskfile["tasks"]

    assert "--fix" not in tasks["lint"]["cmd"]
    assert "--fix" in tasks["lint:fix"]["cmd"]
    assert tasks["check"]["cmds"][0] == {"task": "lint"}
    assert " --rm " in f" {tasks['docker:run']['cmd']} "


def test_runtime_dependencies_match_direct_imports() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    dependency_entries = project["project"]["dependencies"]
    dependencies = {entry.split(">=", 1)[0].lower() for entry in dependency_entries}
    dev_dependencies = {
        entry.split(">=", 1)[0].lower()
        for entry in project["dependency-groups"]["dev"]
    }

    assert "pyyaml" in dependencies
    assert "sqlalchemy>=2.0.36,<2.1" in dependency_entries
    assert not {
        "alembic",
        "notion-client",
        "python-json-logger",
        "python-multipart",
        "tenacity",
    } & dependencies
    assert "types-requests" not in dev_dependencies


def test_sqlmodel_is_the_only_project_history_store() -> None:
    api_source = (ROOT / "app" / "api.py").read_text()

    assert "ProjectMemory" not in api_source
    assert not (ROOT / "app" / "core" / "project_memory.py").exists()


def test_release_toolchain_uses_supported_node() -> None:
    release_workflow = (ROOT / ".github" / "workflows" / "release.yaml").read_text()

    assert "node-version: '22.22.0'" in release_workflow


def test_release_lock_uses_patched_actions_http_stack() -> None:
    lock = json.loads((ROOT / "package-lock.json").read_text())
    packages = lock["packages"]

    assert packages["node_modules/@actions/http-client"]["version"] == "4.0.1"
    assert (
        packages["node_modules/@actions/http-client/node_modules/undici"]["version"]
        == "6.29.1"
    )
    assert "node_modules/@fastify/busboy" not in packages
