# ベクトルDB動作確認テスト

from attack import Attack

if __name__ == "__main__":
    attack = Attack(domain="enterprise", version="18.1")

    query = """
    Phishing is a type of cyber attack that exploits social engineering techniques to deceive users into disclosing sensitive information such as credentials or financial data.
    Modern phishing attacks often combine multiple technologies, including spoofed email protocols, malicious URLs, cloned websites, and malware delivery mechanisms.
    Recently, attackers have increasingly leveraged automation, machine learning, and large language models (LLMs) to generate highly convincing phishing messages at scale, making detection more challenging.
    """  # noqa: E501

    tec_list = attack.get_relevant_technique(query=query, top_k=5, filter="both")
    for tec in tec_list:
        print(tec.name)
        print(tec.id)
        print(tec.description)
        print("==============================")

    print()
