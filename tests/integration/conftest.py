import pytest
from dotenv import dotenv_values

from attack import Attack

_env = dotenv_values(".env.dev")


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """integrationテスト実行前にOPENAI_API_KEYを設定する。"""
    api_key = _env.get("OPENAI_API_KEY") or ""
    monkeypatch.setenv("OPENAI_API_KEY", api_key)


@pytest.fixture(scope="session")
def attack_with_vector() -> Attack:
    """ベクトルDB付きのAttackインスタンス(最新版)。全integrationテストで共有。"""
    return Attack(initialize_vector=True)
