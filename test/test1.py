# 簡単な動作確認テスト

from attack import Attack

if __name__ == "__main__":
    attack = Attack(domain="enterprise", version="18.1")
    print(f"テクニック数: {len(attack.technique_list)}")
    print(f"タクティック数: {len(attack.tactic_list)}")
    print(f"緩和策数: {len(attack.mitigation_list)}")

    # 最初のテクニックの詳細を表示
    first_technique = attack.technique_list[0]
    print(f"最初のテクニック名: {first_technique.name}")
    print(f"最初のテクニックID: {first_technique.id}")
    print(f"最初のテクニック説明: {first_technique.description}")
    print(f"最初のテクニックに関連するタクティック数: {len(first_technique.tactics) if first_technique.tactics else 0}")
    print(f"最初のテクニックに関連する緩和策数: {len(first_technique.mitigation_list)}")
