# 概要
MITRE ATT&CK についてPythonから気軽にデータを利用できるようにすることを目的としたライブラリです。

# インストール方法
## pipの場合
- インストール方法: `pip install git+https://github.com/Fuji-no-yama/attack-python-sdk@1.1.0`
- アップグレード方法: `pip install -U git+https://github.com/Fuji-no-yama/attack-python-sdk@1.1.0`
- 削除方法: `pip uninstall attack`

## uvの場合
- インストール・アップグレード方法: `uv add git+https://github.com/Fuji-no-yama/attack-python-sdk --tag 1.1.0`
- 削除方法: `uv remove attack`

# 使い方
## インスタンスの作成方法
基本的なインスタンスの作成方法は以下のとおりです。(versionは指定しない場合は最新のものになります)
```python
from attack import Attack
attack = Attack(version="18.1", domain="enterprise")
```
初回実行時には自動でローカルにベクトルDBを作成します。ただし、その後にembeddingモデルを変えたい・もう一度ベクトルDBを初期化したいなどの場合には以下の方法で初期化を行えます。  
(embedding modelはtext-embeddingのsmallとlargeを選択できます。)
```python
from attack import Attack
attack = Attack(version="18.1", domain="enterprise", emb_model="text-embedding-3-small", initialize_vector=True)
```

## MITRE ATLAS SDKとの差分
大きく分けて以下2点の差分があります。
1. **domainの存在**  
    インスタンスとして作成する際に、ATT&CKのデータ構造に基づいてdomain("enterprise", "ics", "mobile")を選択する必要があります。

2. **各objectのdescriptionの違い**  
    ATT&CKでは参考文献が非常に充実して構造化されているため、各オブジェクトに`reference_list`として専用オブジェクトが格納されています。そのため、descriptionはデフォルトでは以下の例のような形式になっています。
    ```plain text
    [0] has used phishing with malicious attachments for initial access to victim environments.[1]
    ```
    そのため、参考文献が入った状態でdescriptionを取得したい場合(LLMに渡したい場合など)は各オブジェクトの`get_description_include_references`関数を用いてください。以下の形式でのdescriptionが取得できます。
    ```
    [0] has used phishing with malicious attachments for initial access to victim environments.[1]

    Reference:
    - [0] "CURIUM" https://attack.mitre.org/groups/G1012
    - [1] "PWC Yellow Liderc 2023" https://www.pwc.com/gx/en/issues/cybersecurity/cyber-threat-intelligence/yellow-liderc-ships-its-scripts-delivers-imaploader-malware.html
    ```

3. **Mitigation, Procedureのデータ構造の違い**  
    ATT&CKでは、MitigationやProcedureのデータ構造として、各テクニックに紐づく記述は、それら本体の記述とは異なる専用の記述となります。そのため、以下の通りに本ライブラリでは表現しています。
    ```
    AbstractMitigation (<-これ専用の記述も存在)
    ├─ ConcreteMitigation1 (専用の記述を保持・テクニックに1対1対応)
    └─ ConcreteMitigation2 (専用の記述を保持・テクニックに1対1対応)

    Cmpaign・Group・Software (<-これ専用の記述も存在)
    ├─ Procedure1 (専用の記述を保持・テクニックに1対1対応)
    └─ Procedure2 (専用の記述を保持・テクニックに1対1対応)
    ```

## ユースケース

### 1. RAGのためのプロシージャ検索
RAGのために、1つの記述からプロシージャを検索し、それと同じCampaign・Software・Groupに属するプロシージャすべてを取得するためのPythonコード
``` python
attack = Attack()
query = "ここにRAG検索用のクエリを記載"

procedure_list = attack.get_relevant_procedure(
    query=query,
    top_k=5,
    filter="all",
)  # ここでは"all"を指定し、Campaign・Software・Groupのすべてを検索対象とする

relevant_procedure_list = []  # 検索されたプロシージャと同じ所属のプロシージャの記述すべてを格納するリスト
for proc in procedure_list:
    if proc.parent_type == "campaign":
        parent = attack.get_campaign_by_id(proc.parent_id)
    elif proc.parent_type == "group":
        parent = attack.get_group_by_id(proc.parent_id)
    else:  # software
        parent = attack.get_software_by_id(proc.parent_id)

    relevant_procedure_list.append(proc.get_description_include_references())
    for related_proc in parent.procedure_list:
        relevant_procedure_list.append(related_proc.get_description_include_references())

# この後に、LLMなどに取得した情報を渡して生成する
```

## 機能一覧

### ATT&CK テクニック オブジェクト (AttackTechnique)

#### 保有情報
- name(str) : テクニック名
- id(str) : id名 (例 T1059.001)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- have_parent(bool) : 親がいるかどうか(サブテクニックかどうか)
- parent_id(str | None) : 親のid名 (例 T1059) (親がいない場合はNone)
- tactics(list[AttackTactic]) : 所属するtacticオブジェクトのリスト
- mitigation_list(list[AttackConcreteMitigation]) : テクニックに紐づく具体緩和策オブジェクトのリスト
- procedure_list(list[AttackProcedure]) : テクニックに紐づくプロシージャオブジェクトのリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# リストから検索
for tec in attack.technique_list:
    if tec.id == "T1059.001":
        print("found!!", tec.name)

# get_technique_by_idを使用
tec = attack.get_technique_by_id(technique_id="T1059.001")
print("検索結果", tec.id, tec.name)
```

### ATT&CK タクティック オブジェクト (AttackTactic)

#### 保有情報
- name(str) : タクティック名
- id(str) : id名 (例 TA0001)
- description(str) : 記述内容
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- technique_list(list[AttackTechnique]) : タクティックに紐づくテクニックオブジェクトのリスト

#### 使用例
```python
# リストから検索してテクニック一覧を表示
for tac in attack.tactic_list:
    if tac.id == "TA0001":
        for tec in tac.technique_list:
            print(tec.id)

# get_tactic_by_name / get_tactic_by_idを使用
tac = attack.get_tactic_by_name(tactic_name="Initial Access")
print("検索結果", tac.id)

tac = attack.get_tactic_by_id(tactic_id="TA0001")
print("検索結果", tac.name)
```

### ATT&CK 緩和策 オブジェクト

#### 抽象緩和策 (AttackAbstractMitigation)
抽象緩和策は、一般的な緩和策の概要を表すオブジェクトです。

##### 保有情報
- name(str) : 緩和策名
- id(str) : id名 (例 M1013)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- concrete_mitigation_list(list[AttackConcreteMitigation]) : この抽象緩和策に紐づく具体緩和策のリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

##### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 具体緩和策 (AttackConcreteMitigation)
具体緩和策は、特定のテクニックに対する具体的な緩和方法を表すオブジェクトです。

##### 保有情報
- abstract_mitigation_id(str) : 紐づく抽象緩和策のid (例 M1013)
- abstract_mitigation_name(str) : 紐づく抽象緩和策の名前
- technique_id(str) : 対象テクニックのid
- description(str) : テクニック固有の具体的な緩和策の記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

##### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# 抽象緩和策から具体緩和策を表示
for mit in attack.mitigation_list:
    if mit.id == "M1013":
        print(f"緩和策名: {mit.name}")
        for concrete_mit in mit.concrete_mitigation_list:
            print(f"- {concrete_mit.technique_id}: {concrete_mit.description}")

# get_mitigation_by_idを使用
mit = attack.get_mitigation_by_id(mitigation_id="M1013")
print("検索結果", mit.id, mit.name)

# 特定テクニックに対する緩和策を取得
concrete_mits = attack.get_concrete_mitigation_by_technique_id(technique_id="T1059.001")
for cm in concrete_mits:
    print(f"{cm.abstract_mitigation_name}: {cm.description}")
```

### ATT&CK キャンペーン オブジェクト (AttackCampaign)

キャンペーンは、攻撃者グループによる一連の攻撃活動を表すオブジェクトです。

#### 保有情報
- name(str) : キャンペーン名
- id(str) : id名 (例 C0001)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- procedure_list(list[AttackProcedure]) : キャンペーンで使用されたプロシージャのリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# リストから検索
for campaign in attack.campaign_list:
    print(f"{campaign.id}: {campaign.name}")
    for proc in campaign.procedure_list:
        print(f"  - {proc.technique_id}: {proc.description[:50]}...")

# get_campaign_by_idを使用
campaign = attack.get_campaign_by_id(campaign_id="C0001")
print("検索結果", campaign.name)
```

### ATT&CK グループ オブジェクト (AttackGroup)

グループは、攻撃者グループの情報を表すオブジェクトです。

#### 保有情報
- name(str) : グループ名
- id(str) : id名 (例 G0001)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- procedure_list(list[AttackProcedure]) : グループが使用したプロシージャのリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# リストから検索
for group in attack.group_list:
    print(f"{group.id}: {group.name}")

# get_group_by_idを使用
group = attack.get_group_by_id(group_id="G0001")
print("検索結果", group.name)
```

### ATT&CK ソフトウェア オブジェクト (AttackSoftware)

ソフトウェアは、攻撃者が使用するマルウェアやツールの情報を表すオブジェクトです。

#### 保有情報
- name(str) : ソフトウェア名
- id(str) : id名 (例 S0001)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- procedure_list(list[AttackProcedure]) : ソフトウェアが使用するプロシージャのリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# リストから検索
for software in attack.software_list:
    print(f"{software.id}: {software.name}")

# get_software_by_idを使用
software = attack.get_software_by_id(software_id="S0001")
print("検索結果", software.name)
```

### ATT&CK プロシージャ オブジェクト (AttackProcedure)

プロシージャは、キャンペーン・グループ・ソフトウェアが特定のテクニックをどのように使用したかを表すオブジェクトです。

#### 保有情報
- original_id(str) : プロシージャの一意なID (例 P0001)
- parent_id(str) : 親となるキャンペーン/グループ/ソフトウェアのID
- parent_name(str) : 親の名前
- parent_type(str) : 親のタイプ ("campaign", "group", "software"のいずれか)
- technique_id(str) : 使用されたテクニックのID
- description(str) : プロシージャの具体的な記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### メソッド
- `get_description_include_references()` : 参考資料を含む完全な説明文を取得

#### 使用例
```python
# 特定テクニックに関連するプロシージャを取得
procedures = attack.get_procedure_by_technique_id(technique_id="T1059.001")
for proc in procedures:
    print(f"{proc.parent_name} ({proc.parent_type}): {proc.description[:50]}...")

# IDでプロシージャを取得
proc = attack.get_procedure_by_id(procedure_id="P0001")
print(f"{proc.parent_name}が{proc.technique_id}を使用: {proc.description}")
```

### ATT&CK 参考資料 オブジェクト

#### 外部参考資料 (AttackExternalReference)
外部の論文やブログ記事などの参考資料を表すオブジェクトです。

##### 保有情報
- id(int) : 参考資料の一意なID
- name(str) : 引用名 (例 "Microsoft Local Accounts Feb 2019")
- url(str) : 参考資料のURL
- description(str) : 引用の詳細情報

#### 内部参考資料 (AttackInternalReference)
ATT&CK内の他のオブジェクトへの参照を表すオブジェクトです。

##### 保有情報
- id(str) : 参照先のMITRE ID (例 "T1552.004")
- url(str) : 参照先のURL

#### 使用例
```python
# 外部参考資料を名前で検索
ref = attack.get_external_reference_by_name(name="Microsoft Local Accounts Feb 2019")
print("検索結果", ref.url)

# リストから検索
for ref in attack.external_reference_list:
    print(f"{ref.name}: {ref.url}")
```

### 検索関数一覧

本ライブラリでは、以下の検索関数を使用できます。

#### 1. テクニックID検索
```python
tec = attack.get_technique_by_id(technique_id="T1059.001")
print("検索結果", tec.name)
```

#### 2. タクティックID検索
```python
tac = attack.get_tactic_by_id(tactic_id="TA0001")
print("検索結果", tac.name)
```

#### 3. タクティック名検索
```python
tac = attack.get_tactic_by_name(tactic_name="Initial Access")
print("検索結果", tac.id)
```

#### 4. 緩和策ID検索
```python
mit = attack.get_mitigation_by_id(mitigation_id="M1013")
print("検索結果", mit.name)
```

#### 5. テクニックIDから具体緩和策を取得
```python
concrete_mits = attack.get_concrete_mitigation_by_technique_id(technique_id="T1059.001")
for cm in concrete_mits:
    print(f"{cm.abstract_mitigation_name}: {cm.description}")
```

#### 6. キャンペーンID検索
```python
campaign = attack.get_campaign_by_id(campaign_id="C0001")
print("検索結果", campaign.name)
```

#### 7. グループID検索
```python
group = attack.get_group_by_id(group_id="G0001")
print("検索結果", group.name)
```

#### 8. ソフトウェアID検索
```python
software = attack.get_software_by_id(software_id="S0001")
print("検索結果", software.name)
```

#### 9. テクニックIDからプロシージャを取得
```python
procedures = attack.get_procedure_by_technique_id(technique_id="T1059.001")
for proc in procedures:
    print(f"{proc.parent_name}: {proc.description}")
```

#### 10. プロシージャID検索
```python
proc = attack.get_procedure_by_id(procedure_id="P0001")
print("検索結果", proc.description)
```

#### 11. 外部参考資料名検索
```python
ref = attack.get_external_reference_by_name(name="Microsoft Local Accounts Feb 2019")
print("検索結果", ref.url)
```

#### 12. クエリからのテクニックベクトル検索
記述に類似する内容からベクトル検索を行うことができます。
- query引数: 自由記述のクエリを入力できます。
- top_k引数: 上位何件を取得するかを選択できます。
- filter引数: "child"(子テクニックのみ)、"parent"(親テクニックのみ)、"both"(全テクニック) の3種類から選択できます。

```python
test_query = "Please search techniques about credential dumping"
searched_tec_list = attack.get_relevant_technique(query=test_query, top_k=5, filter="both")
print("検索結果", [tec.id for tec in searched_tec_list])
```

#### 13. クエリからのプロシージャベクトル検索
プロシージャの記述に類似する内容からベクトル検索を行うことができます。
- query引数: 自由記述のクエリを入力できます。
- top_k引数: 上位何件を取得するかを選択できます。
- filter引数: "campaign"、"group"、"software"、"all"(全プロシージャ) の4種類から選択できます。

```python
test_query = "phishing attack using malicious attachments"
searched_proc_list = attack.get_relevant_procedure(query=test_query, top_k=5, filter="all")
for proc in searched_proc_list:
    print(f"{proc.parent_name} ({proc.parent_type}): {proc.description[:100]}...")
```

#### 14. 利用可能なバージョン一覧取得
```python
versions = attack.get_available_versions()
print("利用可能なバージョン:", versions)
```