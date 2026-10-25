import json
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from muninn.library import Store
from muninn.web import create_app
from muninn.workflows import OUTPUTS, App, ProviderError, ProviderResult


class Clock:
    """A controllable store clock."""

    def __init__(self):
        self.now = datetime(2026, 10, 24, 10, 0, tzinfo=UTC)

    def __call__(self):
        return self.now

    def advance(self, **delta):
        self.now += timedelta(**delta)


class ScriptedProvider:
    """Replays saved outputs (dicts) or raises saved failures, in order."""

    model = "scripted-model"

    def __init__(self, *script):
        self.parameters = {"effort": "high"}
        self.script = list(script)
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        if callable(step):
            step = step(request)
        output = OUTPUTS[request.protocol["name"]].model_validate(step)
        return ProviderResult(output=output, raw=json.dumps(step), model=self.model)


class FailIfCalled:
    """A provider that must never be used (restore, migrations, views)."""

    model = "never"

    def __init__(self):
        self.parameters = {}

    def complete(self, request):
        msg = "the model was called"
        raise AssertionError(msg)


def rid():
    return str(uuid.uuid4())


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def make_app(tmp_path, clock):
    opened = []

    def make(*script, path=None):
        store = Store.open(path or tmp_path / "lib.sqlite", clock=clock)
        opened.append(store)
        app = App(store, ScriptedProvider(*script))
        app.recover()
        return app

    yield make
    for store in opened:
        store.close()


def timeout():
    return ProviderError(kind="timeout", detail="no response in time")


HEADERS = {"x-muninn-protocol": "1"}


class Browser:
    def __init__(self, data_dir, provider, clock):
        self.client = TestClient(create_app(data_dir, provider=provider, clock=clock))

    def get(self, path):
        response = self.client.get(f"/api{path}")
        assert response.status_code == 200, response.text
        return response.json()

    def post(self, path, request_id=None, expect=200, **body):
        response = self.client.post(
            f"/api{path}",
            json={"request_id": request_id or str(uuid.uuid4()), **body},
            headers=HEADERS,
        )
        assert response.status_code == expect, response.text
        return response.json()


@pytest.fixture
def browser(tmp_path, clock):
    def open_browser(*script, provider=None):
        return Browser(tmp_path / "data", provider or ScriptedProvider(*script), clock)

    return open_browser
