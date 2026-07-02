import pytest

from attack import Attack
from attack.config import settings


@pytest.fixture(autouse=True)
def _unset_openai_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """unitテスト実行時はsettings.openai_api_keyを空にしてベクトルDB初期化をスキップする。"""
    monkeypatch.setattr(settings, "openai_api_key", "")


@pytest.fixture(scope="module")
def attack_default() -> Attack:
    """デフォルト設定のAttackインスタンス(ベクトルDBなし)。"""
    original = settings.openai_api_key
    settings.openai_api_key = ""
    try:
        return Attack()
    finally:
        settings.openai_api_key = original


@pytest.fixture(scope="module")
def attack_enterprise_v18() -> Attack:
    """Enterprise v18.1のAttackインスタンス(ベクトルDBなし)。"""
    original = settings.openai_api_key
    settings.openai_api_key = ""
    try:
        return Attack(domain="enterprise", version="18.1")
    finally:
        settings.openai_api_key = original


@pytest.fixture(scope="module")
def attack_mobile() -> Attack:
    """Mobileドメインのアタックインスタンス(ベクトルDBなし)。"""
    original = settings.openai_api_key
    settings.openai_api_key = ""
    try:
        return Attack(domain="mobile")
    finally:
        settings.openai_api_key = original


@pytest.fixture(scope="module")
def attack_ics() -> Attack:
    """ICSドメインのアタックインスタンス(ベクトルDBなし)。"""
    original = settings.openai_api_key
    settings.openai_api_key = ""
    try:
        return Attack(domain="ics")
    finally:
        settings.openai_api_key = original


@pytest.fixture(scope="module")
def all_versions() -> list[str]:
    """利用可能な全バージョンのリスト。"""
    original = settings.openai_api_key
    settings.openai_api_key = ""
    try:
        return Attack().get_available_versions()
    finally:
        settings.openai_api_key = original
