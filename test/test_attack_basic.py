"""
Attackクラスの基本的なテスト
"""

import re

from attack import Attack


class TestAttack:
    def test_attack(self) -> None:
        """
        全体のAttackインスタンスをテストする
        """
        attack = Attack(initialize_vector=True)
        domains = ["enterprise", "mobile", "ics"]
        for version in attack.get_available_versions():
            for domain in domains:
                attack = Attack(initialize_vector=True, version=version, domain=domain)
                self.check_attack(attack)

    def check_attack(self, attack: Attack) -> None:
        """
        Attackインスタンスの基本プロパティを確認
        """
        self.check_properties(attack)
        self.check_description(attack)

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
