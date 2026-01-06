import os
import re
import shutil
from collections.abc import Iterator, Sequence
from contextlib import suppress
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar

import chromadb
import pandas as pd
import polars as pl
import yaml
from chromadb.api.models.Collection import Collection
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
from openai import OpenAI
from platformdirs import user_data_dir

from attack.entities import AttackAbstractMitigation, AttackConcreteMitigation, AttackTactic, AttackTechnique


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
        self.tactic_list: list[AttackTactic] = self.__setup_tactic_list()
        self.mitigation_list: list[AttackAbstractMitigation] = self.__setup_mitigation_list()
        self.technique_list: list[AttackTechnique] = self.__setup_technique_list()

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
                description=description,
                domain=self.domain,
                concrete_mitigation_list=concrete_mitigation_list,
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
                    description=conc_mit_row["mapping description"],
                    domain=self.domain,
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
                description=row["description"],
                domain=self.domain,
                mitigation_list=conc_mit_list,
                have_parent=bool(parent_id),
                parent_id=parent_id,
                tactics=tactic_list if row["ID"] != "" else None,
            )
            technique_list.append(tec)
            for tactic in tactic_list:  # タクティックにテクニックを追加
                self.__add_technique_to_tactic(tactic.name, tec)
        return technique_list

    def get_tactic_by_id(self, tactic_id: str) -> AttackTactic:
        for tactic in self.tactic_list:
            if tactic.id == tactic_id:
                return tactic
        err_msg = f"tactic_id: {tactic_id} は存在しません"
        raise ValueError(err_msg)

    def get_tactic_by_name(self, tactic_name: str) -> AttackTactic:
        for tactic in self.tactic_list:
            if tactic.name == tactic_name:
                return tactic
        err_msg = f"tactic_name: {tactic_name} は存在しません"
        raise ValueError(err_msg)

    def get_mitigation_by_id(self, mitigation_id: str) -> AttackAbstractMitigation:
        for mitigation in self.mitigation_list:
            if mitigation.id == mitigation_id:
                return mitigation
        err_msg = f"mitigation_id: {mitigation_id} は存在しません"
        raise ValueError(err_msg)

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
