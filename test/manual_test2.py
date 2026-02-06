from attack import Attack

if __name__ == "__main__":
    attack = Attack(domain="enterprise", version="18.1")

    query = """
    Phishing is a type of cyber attack that exploits social engineering techniques to deceive users into disclosing sensitive information such as credentials or financial data.
    Modern phishing attacks often combine multiple technologies, including spoofed email protocols, malicious URLs, cloned websites, and malware delivery mechanisms.
    Recently, attackers have increasingly leveraged automation, machine learning, and large language models (LLMs) to generate highly convincing phishing messages at scale, making detection more challenging.
    """  # noqa: E501

    print("=== 関連テクニック検索結果 ===")
    tec_list = attack.get_relevant_technique(query=query, top_k=5, filter="both")
    for tec in tec_list:
        print(tec.name)
        print(tec.id)
        print("raw description:")
        print(tec.description)
        print("description with references:")
        print(tec.get_description_include_references())
        print("==============================")

    print("=== 関連procedure検索結果 ===")
    proc_list = attack.get_relevant_procedure(query=query, top_k=5, filter="all")
    for proc in proc_list:
        if proc.parent_type == "campaign":
            parent_name = attack.get_campaign_by_id(proc.parent_id).name
        elif proc.parent_type == "group":
            parent_name = attack.get_group_by_id(proc.parent_id).name
        else:  # software
            parent_name = attack.get_software_by_id(proc.parent_id).name
        print(parent_name)
        print(proc.parent_id)
        print(proc.technique_id)
        print("raw description:")
        print(proc.description)
        print("description with references:")
        print(proc.get_description_include_references())
        print("==============================")

    print()
