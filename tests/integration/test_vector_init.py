"""ベクトルDB初期化のテスト(OPENAI_API_KEYが必要)。最新バージョンのみ。"""

import pytest

from attack import Attack


@pytest.mark.integration
class TestVectorDbInitialization:
    """ベクトルDBの初期化が正常に完了し、検索可能な状態になることを確認する。"""

    def test_collections_exist(self, attack_with_vector: Attack) -> None:
        assert attack_with_vector.technique_chroma_collection is not None
        assert attack_with_vector.procedure_chroma_collection is not None

    def test_technique_search_works(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_technique(query="credential dumping", top_k=3, filter="both")
        assert len(results) == 3

    def test_procedure_search_works(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="phishing attack", top_k=3)
        assert len(results) == 3
