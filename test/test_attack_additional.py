"""
Atlasクラスの応用テスト(APIキーの使用)
"""

import os
import re

import pytest

from attack import Attack
from attack.entities import AttackTechnique


class TestAtlas:
    def test_atlas_with_api_key(self) -> None:
        """
        全体のAtlasインスタンスをテストする
        """
        if os.environ.get("ATLAS_TEST_FLAG") == "True":
            pytest.skip("APIキーを用いたテストはスキップされます。")
        if "ATLAS_TEST_FLAG" not in os.environ:
            pytest.skip("ATLAS_TEST_FLAGが設定されていないため、APIキーを用いたテストはスキップされます。")
        attack = Attack(initialize_vector=True)  # 最新版, enterpriseのみについてテスト
        self.check_attack(attack)

    def check_attack(self, attack: Attack) -> None:
        """
        Attackインスタンスの基本プロパティを確認
        """
        self.check_properties(attack)
        self.check_description(attack)
        self.check_search(attack)

    def check_properties(self, attack: Attack) -> None:
        """
        Attackの基本プロパティを確認
        """
        assert attack.version is not None
        assert attack.version != ""
        assert attack.technique_list is not None
        assert isinstance(attack.technique_list, list)
        assert len(attack.technique_list) > 0
        assert attack.mitigation_list is not None
        assert isinstance(attack.mitigation_list, list)
        assert len(attack.mitigation_list) > 0

    def check_description(self, attack: Attack) -> None:
        """
        descriptionのフィールドに清掃できていない文字列がないかを確認する
        """
        for tech in attack.technique_list:
            self.check_one_description(tech.description)
        for mit in attack.mitigation_list:
            self.check_one_description(mit.description)

    def check_one_description(self, description: str) -> None:
        """
        1つのdescription文字列に清掃できていない文字列がないかを確認する
        """
        pattern = r"\(Citation: .*?\)"
        match = re.search(pattern, description)
        assert match is None, f"引用表記が残っています: {match.group() if match else ''} in {description[:100]}"

        pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        match = re.search(pattern, description)
        assert match is None, f"内部参照のマークダウン表記が残っています: {match.group() if match else ''} in {description[:100]}"

    def check_search(self, attack: Attack) -> None:
        """
        検索機能が動作するかを確認する
        """
        n = 5
        query = "phishing LLM cloud"
        results = attack.get_relevant_technique(query, top_k=n)
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == n
        for tech in results:
            assert isinstance(tech, AttackTechnique)
            assert tech.id is not None
            assert tech.name is not None
            assert tech.description is not None
