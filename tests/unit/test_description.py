"""description文字列の清掃が正しく行われているかを確認するテスト。"""

import re

from attack import Attack


class TestDescriptionCleaning:
    """descriptionに未清掃の表記が残っていないことを確認する。"""

    def _assert_clean(self, description: str) -> None:
        # Citation表記が残っていないことを確認
        pattern = r"\(Citation: .*?\)"
        match = re.search(pattern, description)
        assert match is None, f"引用表記が残っています: {match.group() if match else ''} in {description[:100]}"

        # 内部参照のマークダウン表記が残っていないことを確認
        pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        match = re.search(pattern, description)
        assert match is None, f"内部参照のマークダウン表記が残っています: {match.group() if match else ''} in {description[:100]}"

    def test_technique_descriptions(self, attack_default: Attack) -> None:
        for tec in attack_default.technique_list:
            self._assert_clean(tec.description)

    def test_mitigation_descriptions(self, attack_default: Attack) -> None:
        for mit in attack_default.mitigation_list:
            self._assert_clean(mit.description)


class TestDescriptionCleaningAllVersions:
    """全バージョンでdescription清掃が正しく行われていることを確認する。"""

    def _assert_clean(self, description: str) -> None:
        pattern = r"\(Citation: .*?\)"
        assert re.search(pattern, description) is None, f"引用表記が残っています: {description[:100]}"

        pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        assert re.search(pattern, description) is None, f"内部参照が残っています: {description[:100]}"

    def test_all_versions(self, all_versions: list[str]) -> None:
        for version in all_versions:
            attack = Attack(version=version)
            for tec in attack.technique_list:
                self._assert_clean(tec.description)
            for mit in attack.mitigation_list:
                self._assert_clean(mit.description)
