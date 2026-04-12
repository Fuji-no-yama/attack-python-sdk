"""ベクトル検索機能のテスト(OPENAI_API_KEYが必要)。"""

import pytest

from attack import Attack
from attack.entities import AttackProcedure, AttackTechnique


@pytest.mark.integration
class TestTechniqueVectorSearch:
    """テクニックのベクトル検索テスト。"""

    def test_search_returns_results(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_technique(query="credential dumping LSASS", top_k=5, filter="both")
        assert isinstance(results, list)
        assert len(results) == 5

    def test_search_results_are_techniques(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_technique(query="credential dumping", top_k=3, filter="both")
        for tec in results:
            assert isinstance(tec, AttackTechnique)
            assert tec.id is not None
            assert tec.name is not None
            assert tec.description is not None

    def test_search_with_parent_filter(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_technique(query="data exfiltration", top_k=3, filter="parent")
        assert len(results) == 3
        for tec in results:
            assert not tec.have_parent

    def test_search_with_child_filter(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_technique(query="data exfiltration", top_k=3, filter="child")
        assert len(results) == 3
        for tec in results:
            assert tec.have_parent


@pytest.mark.integration
class TestProcedureVectorSearch:
    """プロシージャのベクトル検索テスト。"""

    def test_search_returns_results(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="phishing malicious attachments", top_k=3)
        assert isinstance(results, list)
        assert len(results) == 3

    def test_search_results_are_procedures(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="phishing malicious attachments", top_k=3)
        for proc in results:
            assert isinstance(proc, AttackProcedure)
            assert proc.original_id is not None
            assert proc.technique_id is not None
            assert proc.description is not None

    def test_search_with_campaign_filter(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="phishing", top_k=3, filter="campaign")
        assert len(results) == 3
        for proc in results:
            assert proc.parent_type == "campaign"

    def test_search_with_group_filter(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="phishing", top_k=3, filter="group")
        assert len(results) == 3
        for proc in results:
            assert proc.parent_type == "group"

    def test_search_with_software_filter(self, attack_with_vector: Attack) -> None:
        results = attack_with_vector.get_relevant_procedure(query="command execution", top_k=3, filter="software")
        assert len(results) == 3
        for proc in results:
            assert proc.parent_type == "software"
