import os
import re
import shutil
from contextlib import suppress
from importlib.resources import files
from pathlib import Path
from typing import Literal

import chromadb
import pandas as pd
from chromadb.api.models.Collection import Collection
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
from platformdirs import user_data_dir

from attack.config import settings
from attack.entities import (
    AttackAbstractMitigation,
    AttackConcreteMitigation,
    AttackExternalReference,
    AttackInternalReference,
    AttackTactic,
    AttackTechnique,
)


class Attack:
    version: str
    domain: Literal["enterprise", "mobile", "ics"]
    technique_list: list[AttackTechnique]
    tactic_list: list[AttackTactic]
    mitigation_list: list[AttackAbstractMitigation]

    def __init__(
        self,
        *,  # 以下をキーワード引数に
        domain: Literal["enterprise", "mobile", "ics"] = "enterprise",
        version: Literal["17.1", "18.1"] = "18.1",
        emb_model: Literal["text-embedding-3-small", "text-embedding-3-large"] = "text-embedding-3-large",
        initialize_vector: bool = False,
    ) -> None:
        self.domain: Literal["enterprise", "mobile", "ics"] = domain
        self.version = f"v{version}"  # ディレクトリ名はv17.1のような形式であるため、バージョンをv{version}の形式に変換
        self.data_dir_path = files("attack.data").joinpath(f"{self.version}")  # パッケージ内のdataディレクトリ
        self.user_data_dir_path: Path = Path(user_data_dir("attack")) / self.version  # ユーザ側dataディレクトリ
        self.user_data_dir_path.mkdir(parents=True, exist_ok=True)  # 念の為作成
        self.external_reference_list: list[AttackExternalReference] = self.__setup_external_reference_list()
        self.tactic_list: list[AttackTactic] = self.__setup_tactic_list()
        self.mitigation_list: list[AttackAbstractMitigation] = self.__setup_mitigation_list()
        self.technique_list: list[AttackTechnique] = self.__setup_technique_list()

        if not os.path.isdir(str(self.user_data_dir_path.joinpath("chroma"))):  # ユーザ側のバージョンディレクトリにDBが存在しない場合
            print("ベクトルDBの設定がありません。初期化し作成します...")
            initialize_vector = True  # 初期実行時なので初期化を行う
        self.chroma_client = chromadb.PersistentClient(str(self.user_data_dir_path.joinpath("chroma")))
        if initialize_vector:
            # 初期化が選択されている or 指定バージョンのvector DBが存在しない場合
            self.__initialize_vector(model=emb_model)
        self.technique_chroma_collection: Collection = self.__get_technique_chroma_collection(model=emb_model)

    def __setup_external_reference_list(self) -> list[AttackExternalReference]:
        mitigation_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-mitigations.xlsx",
            sheet_name="citations",
        )
        technique_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-techniques.xlsx",
            sheet_name="citations",
        )
        reference_df: pd.DataFrame = pd.concat([mitigation_df, technique_df]).drop_duplicates().reset_index(drop=True)
        ret_list: list[AttackExternalReference] = []
        for i, (_, row) in enumerate(reference_df.iterrows()):
            ref = AttackExternalReference(
                reference_id=i,
                name=row["reference"],
                url=row["url"],
                description=row["citation"],
            )
            ret_list.append(ref)
        return ret_list

    def __setup_tactic_list(self) -> list[AttackTactic]:
        tactic_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-tactics.xlsx",
            sheet_name="tactics",
        )
        tactic_list: list[AttackTactic] = []
        for _, row in tactic_df.iterrows():
            tactic_id: str = row["ID"]
            name: str = row["name"]
            description: str = row["description"]
            tactic = AttackTactic(
                tactic_id=tactic_id,
                name=name,
                domain=self.domain,
                description=description,
                tec_lis=[],
            )
            tactic_list.append(tactic)
        return tactic_list

    def __setup_mitigation_list(self) -> list[AttackAbstractMitigation]:
        mitigation_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-mitigations.xlsx",
            sheet_name="mitigations",
        )
        mitigation_list: list[AttackAbstractMitigation] = []
        for _, row in mitigation_df.iterrows():
            mitigation_id: str = row["ID"]
            description: str = row["description"]
            concrete_mitigation_list: list[AttackConcreteMitigation] = []
            mitigation = AttackAbstractMitigation(
                mitigation_id=mitigation_id,
                description=self.__clean_description(description),
                domain=self.domain,
                concrete_mitigation_list=concrete_mitigation_list,
                reference_list=self.__create_reference_list(description),
            )
            mitigation_list.append(mitigation)
        return mitigation_list

    def __setup_technique_list(self) -> list[AttackTechnique]:
        tech_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-techniques.xlsx",
            sheet_name="techniques",
        )
        conc_mit_df: pd.DataFrame = pd.read_excel(
            self.data_dir_path / f"{self.domain}-attack-{self.version}-techniques.xlsx",
            sheet_name="associated mitigations",
        )
        technique_list: list[AttackTechnique] = []
        for _, row in tech_df.iterrows():
            tec_id: str = row["ID"]
            conc_mit_list: list[AttackConcreteMitigation] = []
            conc_mit_df: pd.DataFrame = conc_mit_df[conc_mit_df["target ID"] == tec_id]
            for _, conc_mit_row in conc_mit_df.iterrows():  # 具体緩和策を抽出
                conc_mit = AttackConcreteMitigation(
                    abstract_mitigation_id=conc_mit_row["source ID"],
                    description=self.__clean_description(conc_mit_row["mapping description"]),
                    domain=self.domain,
                    reference_list=self.__create_reference_list(conc_mit_row["mapping description"]),
                )
                conc_mit_list.append(conc_mit)
                self.__add_concrete_mitigation_to_aabstract_mitigation(  # 先に作成した抽象緩和策クラスに追加
                    abstract_mitigation_id=conc_mit_row["source ID"],
                    concrete_mitigation=conc_mit,
                )
            tactic_list: list[AttackTactic] = [self.get_tactic_by_name(n) for n in row["tactics"].split(", ")]
            parent_id: str | None = (
                re.findall(r"(T\d{4}).\d{4}", tec_id)[0] if re.search(r"T\d{4}.\d{4}", tec_id) else None
            )  # テクニックIDがTで始まる場合
            tec = AttackTechnique(
                name=row["name"],
                technique_id=tec_id,
                description=self.__clean_description(row["description"]),
                domain=self.domain,
                mitigation_list=conc_mit_list,
                have_parent=bool(parent_id),
                parent_id=parent_id,
                tactics=tactic_list if row["ID"] != "" else [],
                reference_list=self.__create_reference_list(row["description"]),
            )
            technique_list.append(tec)
            for tactic in tactic_list:  # タクティックにテクニックを追加
                self.__add_technique_to_tactic(tactic.name, tec)
        return technique_list

    def __initialize_vector(self, model: Literal["text-embedding-3-small", "text-embedding-3-large"]) -> None:
        try:
            self.__initialize_technique_vector(model=model)  # テクニックのベクトルDBを初期化
            print("ベクトルDBの初期化が完了しました。")  # 初期化完了のメッセージ
        except Exception:
            shutil.rmtree(str(self.user_data_dir_path.joinpath("chroma")))  # 初期化失敗時は変に残らないように削除
            raise

    def __initialize_technique_vector(self, model: Literal["text-embedding-3-small", "text-embedding-3-large"]) -> None:
        # ベクトルdb(chroma)とavroファイルの両方を初期化する関数
        # ベクトルavroファイルの初期化
        id_list: list[str] = []
        desc_list: list[str] = []
        metadata_list: list[dict[str, bool]] = []  # {"is_parent":bool}の形を保持した辞書
        for tec in self.technique_list:
            id_list.append(tec.id)
            desc_list.append(tec.description)
            metadata_list.append({"is_parent": not tec.have_parent})
        # ベクトルDB(chroma)の初期化
        with suppress(NotFoundError):
            self.chroma_client.delete_collection(name="attack_technique")  # 存在する場合は一度削除してリセット
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(  # ベクトル化関数
            api_key=settings.openai_api_key,
            model_name=model,
        )
        collection: Collection = self.chroma_client.get_or_create_collection(
            name="attack_technique",
            metadata={"hnsw:space": "cosine"},
            embedding_function=openai_ef,  # ty:ignore[invalid-argument-type]
        )
        collection.add(documents=desc_list, ids=id_list, metadatas=metadata_list)  # コレクションに追加  # ty:ignore[invalid-argument-type]

    def __get_technique_chroma_collection(
        self,
        model: Literal["text-embedding-3-small", "text-embedding-3-large"],
    ) -> Collection:  # chromaDBを起動する関数
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=model,
        )
        collection: Collection = self.chroma_client.get_collection(name="attack_technique", embedding_function=openai_ef)  # ty:ignore[invalid-argument-type]
        return collection

    def __add_concrete_mitigation_to_aabstract_mitigation(
        self,
        abstract_mitigation_id: str,
        concrete_mitigation: AttackConcreteMitigation,
    ) -> None:
        """
        抽象緩和策に具体緩和策を追加する
        """
        self.get_mitigation_by_id(abstract_mitigation_id).concrete_mitigation_list.append(concrete_mitigation)

    def __add_technique_to_tactic(
        self,
        tactic_name: str,
        technique: AttackTechnique,
    ) -> None:
        """
        タクティックにテクニックを追加する
        """
        tactic = self.get_tactic_by_name(tactic_name)
        if tactic is not None:
            tactic.technique_list.append(technique)
        else:
            err_msg = f"tactic_name: {tactic_name} は存在しません"
            raise ValueError(err_msg)

    def __create_reference_list(self, desc: str) -> list[AttackExternalReference | AttackInternalReference]:
        """
        referenceオブジェクトのリストをdescから各テクニック、緩和策ごとに作成する
        """
        ret_list: list[AttackExternalReference | AttackInternalReference] = []
        ref_list: list[str] = list(dict.fromkeys(re.findall(r"\(Citation: (.*?)\)|\[.*?\]\((https://attack.mitre.org/.*?)\)", desc)))
        for match_tuple in ref_list:
            if match_tuple[0] != "":  # 外部参照の場合
                ref: AttackExternalReference = self.get_external_reference_by_name(match_tuple[0])
                ret_list.append(ref)
            elif match_tuple[1] != "":  # 内部参照の場合
                id_match = re.search(r"(T\d{4}.*)", match_tuple[1])
                if id_match:
                    mitre_id: str = id_match.group(1).replace("/", ".")
                    internal_ref = AttackInternalReference(
                        mitre_id=mitre_id,
                        url=match_tuple[1],
                    )
                    ret_list.append(internal_ref)
        return ret_list

    def __clean_description(self, desc: str) -> str:
        """
        descから引用を引用マーク([0], [1]など)に順番に変換する
        同じ引用には同じ番号を割り当てる
        """
        external_pattern = r"\(Citation: .*?\)"
        internal_pattern = r"\[.*?\]\(https://attack.mitre.org/.*?\)"
        combined_pattern = f"{external_pattern}|{internal_pattern}"

        ref_to_number: dict[str, int] = {}  # 引用文字列 -> 番号のマッピング
        counter = 0

        def replace_with_counter(match: re.Match[str]) -> str:
            nonlocal counter
            matched_text = match.group()
            if matched_text not in ref_to_number:
                ref_to_number[matched_text] = counter
                counter += 1
            return f"[{ref_to_number[matched_text]}]"

        result: str = re.sub(combined_pattern, replace_with_counter, desc)
        return result

    def get_tactic_by_id(self, tactic_id: str) -> AttackTactic:
        """
        idからタクティックオブジェクトを取得する

        Args:
            tactic_id (str): タクティックID (例: TA0001)

        Returns:
            AttackTactic: タクティックオブジェクト

        Raises:
            ValueError: 指定したIDのタクティックが存在しない場合
        """
        for tactic in self.tactic_list:
            if tactic.id == tactic_id:
                return tactic
        err_msg = f"tactic_id: {tactic_id} は存在しません"
        raise ValueError(err_msg)

    def get_tactic_by_name(self, tactic_name: str) -> AttackTactic:
        """
        タクティック名からタクティックオブジェクトを取得する

        Args:
            tactic_name (str): タクティック名 (例: Initial Access)

        Returns:
            AttackTactic: タクティックオブジェクト

        Raises:
            ValueError: 指定した名前のタクティックが存在しない場合
        """
        for tactic in self.tactic_list:
            if tactic.name == tactic_name:
                return tactic
        err_msg = f"tactic_name: {tactic_name} は存在しません"
        raise ValueError(err_msg)

    def get_mitigation_by_id(self, mitigation_id: str) -> AttackAbstractMitigation:
        """
        緩和策idから緩和策オブジェクトを取得する

        Args:
            mitigation_id (str): 緩和策ID (例: M1010)

        Returns:
            AttackAbstractMitigation: 緩和策オブジェクト

        Raises:
            ValueError: 指定したIDの緩和策が存在しない場合
        """
        for mitigation in self.mitigation_list:
            if mitigation.id == mitigation_id:
                return mitigation
        err_msg = f"mitigation_id: {mitigation_id} は存在しません"
        raise ValueError(err_msg)

    def get_external_reference_by_name(self, name: str) -> AttackExternalReference:
        """
        外部参照の引用名から外部参照オブジェクトを取得する

        Args:
            name (str): 引用名 (例: ADSecurity Kerberos and KRBTGT)

        Returns:
            AttackExternalReference: 外部参照オブジェクト

        Raises:
            ValueError: 指定した名前の外部参照が存在しない場合
        """
        for ref in self.external_reference_list:
            if ref.name == name:
                return ref
        err_msg = f"外部参考資料: {name} は存在しません"
        raise ValueError(err_msg)

    def get_technique_by_id(self, technique_id: str) -> AttackTechnique:
        """
        テクニックidからテクニックオブジェクトを取得する

        Args:
            technique_id (str): テクニックID (例: T1059.001)

        Returns:
            AttackTechnique: テクニックオブジェクト

        Raises:
            ValueError: 指定したIDのテクニックが存在しない場合
        """
        for tec in self.technique_list:
            if tec.id == technique_id:
                return tec
        err_msg = f"technique_id: {technique_id} は存在しません"
        raise ValueError(err_msg)

    def get_relevant_technique(
        self,
        query: str,
        top_k: int,
        *,
        filter: Literal["parent", "child", "both"] = "both",  # noqa: A002
    ) -> list[AttackTechnique]:
        """
        クエリを元にベクトルDBを検索する関数

        Args:
            query (str): 検索文言
            top_k (int): 上位何件を取得するか
            filter (str): 親のみ, 子のみ, 両方 の3種類でフィルターをかける

        Returns:
            list[AttackTechnique]: top_kで指定された個数分上位の結果をテクニックオブジェクト
        """
        if filter == "parent":
            result = self.technique_chroma_collection.query(query_texts=[query], n_results=top_k, where={"is_parent": True})
        elif filter == "child":
            result = self.technique_chroma_collection.query(query_texts=[query], n_results=top_k, where={"is_parent": False})
        elif filter == "both":
            result = self.technique_chroma_collection.query(query_texts=[query], n_results=top_k)
        ret: list[AttackTechnique] = [self.get_technique_by_id(technique_id=tec_id) for tec_id in result["ids"][0]]
        return ret
