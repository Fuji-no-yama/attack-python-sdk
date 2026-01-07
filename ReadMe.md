# 概要
MITRE ATT&CK についてPythonから気軽にデータを利用できるようにすることを目的としたライブラリです。

# インストール方法
## pipの場合
- インストール方法: `pip install git+https://github.com/Fuji-no-yama/attack-python-sdk@1.0.0`
- アップグレード方法: `pip install -U git+https://github.com/Fuji-no-yama/attack-python-sdk@1.0.0`
- 削除方法: `pip uninstall attack`

## uvの場合
- インストール・アップグレード方法: `uv add git+https://github.com/Fuji-no-yama/attack-python-sdk --tag 1.0.0`
- 削除方法: `uv remove attack`

# 使い方
## インスタンスの作成方法
基本的なインスタンスの作成方法は以下のとおりです。(versionは指定しない場合は最新のものになります)
```python
from attack import Attack
attack = Attack(version="18.1")
```
初回実行時には自動でローカルにベクトルDBを作成します。ただし、その後にembeddingモデルを変えたい・もう一度ベクトルDBを初期化したいなどの場合には以下の方法で初期化を行えます。  
(embedding modelはtext-embeddingのsmallとlargeを選択できます。)
```python
from attack import Attack
attack = Attack(version="18.1", emb_model="text-embedding-3-small", initialize_vector=True)
```
## 機能一覧

### ATT&CK テクニック オブジェクト

#### 保有情報
- name(str) : テクニック名
- id(str) : id名 (例 T1059.001)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- have_parent(bool) : 親がいるかどうか(サブテクニックかどうか)
- parent_id(str) : 親のid名 (例 T1059) (親がいない場合はNone)
- tactics(list[AttackTactic]) : 所属するtacticオブジェクトのリスト
- mitigation_list(list[AttackConcreteMitigation]) : テクニックに紐づく具体緩和策オブジェクトのリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### 使用例
attackテクニックオブジェクトを順番に確認しidがT1059.001のものを取得したい場合
```python
for tec in attack.technique_list:
    if tec.id == "T1059.001":
        print("found!!")
```

### ATT&CK タクティック オブジェクト

#### 保有情報
- name(str) : タクティック名
- id(str) : id名 (例 TA0001)
- description(str) : 記述内容
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- technique_list(list[AttackTechnique]) : タクティックに紐づくテクニックオブジェクトのリスト

#### 使用例
attackタクティックオブジェクトを順番に確認しidがTA0001について紐づいているテクニックのid一覧を表示したい場合
```python
for tac in attack.tactic_list:
    if tac.id == "TA0001":
        for tec in tac.technique_list:
            print(tec.id)
```

### ATT&CK 緩和策 オブジェクト

#### 抽象緩和策 (AttackAbstractMitigation)
抽象緩和策は、一般的な緩和策の概要を表すオブジェクトです。

##### 保有情報
- id(str) : id名 (例 M1013)
- description(str) : 記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- concrete_mitigation_list(list[AttackConcreteMitigation]) : この抽象緩和策に紐づく具体緩和策のリスト
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### 具体緩和策 (AttackConcreteMitigation)
具体緩和策は、特定のテクニックに対する具体的な緩和方法を表すオブジェクトです。

##### 保有情報
- abstract_mitigation_id(str) : 紐づく抽象緩和策のid (例 M1013)
- description(str) : テクニック固有の具体的な緩和策の記述内容(引用を番号に変換し整形済み)
- domain(str) : ドメイン ("enterprise", "mobile", "ics"のいずれか)
- reference_list(list[AttackExternalReference | AttackInternalReference]) : 引用参考資料のリスト

#### 使用例
attack抽象緩和策オブジェクトを順番に確認しidがM1013について紐づいている具体緩和策の記述内容を表示したい場合
```python
for mit in attack.mitigation_list:
    if mit.id == "M1013":
        for concrete_mit in mit.concrete_mitigation_list:
            print(concrete_mit.description)
```

### ATT&CK 参考資料 オブジェクト

#### 外部参考資料 (AttackExternalReference)
外部の論文やブログ記事などの参考資料を表すオブジェクトです。

##### 保有情報
- reference_id(int) : 参考資料の一意なID
- name(str) : 引用名 (例 "Microsoft Local Accounts Feb 2019")
- url(str) : 参考資料のURL
- description(str) : 引用の詳細情報

#### 内部参考資料 (AttackInternalReference)
ATT&CK内の他のテクニックへの参照を表すオブジェクトです。

##### 保有情報
- mitre_id(str) : 参照先のテクニックID (例 "T1552.004")
- url(str) : 参照先のURL

### 各種検索

5種類の検索関数を使用することができます。

#### テクニックid検索
idを元にテクニックを検索することができます。(idが存在しない場合はValueErrorをraiseします)
```python
tec = attack.get_technique_by_id(technique_id="T1059.001")
print("検索結果", tec.id)
```

#### タクティック名検索
タクティック名を元にタクティックオブジェクトを検索することができます。(名前が存在しない場合はValueErrorをraiseします)
```python
tac = attack.get_tactic_by_name(tactic_name="Initial Access")
print("検索結果", tac.id)
```

#### クエリからのテクニックベクトル検索
記述に類似する内容からベクトル検索を行うことができます。
- query引数: 自由記述のクエリを入力できます。
- top_k引数: 上位何件を取得するかを選択できます。
- filter引数: 子テクニックのみ・親テクニックのみ・両方(全テクニック) の3種類から選択できます。
```python
test_query = "Please search techniques about credential dumping"
searched_tec_list = attack.get_relevant_technique(query=test_query, top_k=5, filter="both")
print("検索結果", [tec.id for tec in searched_tec_list])
```

#### 緩和策id検索
idを元に抽象緩和策を検索することができます。(idが存在しない場合はValueErrorをraiseします)
```python
mit = attack.get_mitigation_by_id(mitigation_id="M1013")
print("検索結果", mit.id)
```

#### 外部参考資料名検索
引用名を元に外部参考資料を検索することができます。(名前が存在しない場合はValueErrorをraiseします)
```python
ref = attack.get_external_reference_by_name(name="Microsoft Local Accounts Feb 2019")
print("検索結果", ref.url)
```