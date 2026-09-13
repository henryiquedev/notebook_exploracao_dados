"""
Funções de validação do pipeline Serendipity-LLM.

Cada função recebe um DataFrame e retorna uma tupla:
  (DataFrame_validado, relatorio)

O relatório é um dicionário com métricas da validação,
permitindo auditoria e logging estruturado.
"""

import logging
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd

from src.config import (
    REQUIRED_ANSWERS_COLS,
    RATING_MIN, RATING_MAX, RATING_STEP,
    S_MIN, S_MAX,
    Q_MIN, Q_MAX,
)


# V1: Campos obrigatórios
def validate_required_columns(
    df: pd.DataFrame,
    required: list,
    logger: logging.Logger,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica se todas as colunas obrigatórias estão presentes."""
    missing = [c for c in required if c not in df.columns]
    report = {
        "validation": "required_columns",
        "missing": missing,
        "passed": len(missing) == 0,
    }
    if missing:
        raise ValueError(f"[V1] Campos obrigatórios ausentes: {missing}")
    logger.info(f"[V1] OK — todas as {len(required)} colunas obrigatórias presentes.")
    return df, report


# V2: Unicidade de (userId, movieId)
def validate_uniqueness(
    df: pd.DataFrame,
    subset: list,
    logger: logging.Logger,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica unicidade da chave composta. Remove duplicatas se houver."""
    dup_mask = df.duplicated(subset=subset, keep=False)
    n_dups = int(dup_mask.sum())
    report = {
        "validation": "uniqueness",
        "subset": subset,
        "duplicates_found": n_dups,
        "passed": n_dups == 0,
    }
    if n_dups > 0:
        logger.warning(f"[V2] {n_dups} duplicatas em {subset} — removendo (mantendo primeira).")
        df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    else:
        logger.info(f"[V2] OK — nenhuma duplicata em {subset}.")
    return df, report


#V3: Faixa de rating
def validate_rating_range(
    df: pd.DataFrame,
    col: str = "rating",
    logger: logging.Logger = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica se ratings estão em [0.5, 5.0] com passo de 0.5."""
    valid = df[col].between(RATING_MIN, RATING_MAX) & \
            (((df[col] / RATING_STEP).round() * RATING_STEP - df[col]).abs() < 1e-9)
    n_invalid = int((~valid).sum())
    report = {
        "validation": "rating_range",
        "column": col,
        "invalid_found": n_invalid,
        "passed": n_invalid == 0,
    }
    if n_invalid > 0:
        logger.warning(f"[V3] {n_invalid} ratings inválidos em '{col}' — removendo.")
        df = df[valid].reset_index(drop=True)
    else:
        logger.info(f"[V3] OK — todos os ratings em [{RATING_MIN}, {RATING_MAX}].")
    return df, report


# V4: Faixa de s1-s8
def validate_s_columns(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica se s1-s8 estão em [1, 5] ou NA. Marca inválidos como NA."""
    s_cols = [f"s{i}" for i in range(1, 9)]
    total_invalid = 0
    for col in s_cols:
        if col not in df.columns:
            continue
        invalid = df[col].notna() & (~df[col].between(S_MIN, S_MAX))
        n = int(invalid.sum())
        if n > 0:
            logger.warning(f"[V4] {n} valores inválidos em '{col}' — marcando como NA.")
            df.loc[invalid, col] = np.nan
            total_invalid += n
    report = {
        "validation": "s_columns_range",
        "columns": s_cols,
        "invalid_marked_na": total_invalid,
        "passed": total_invalid == 0,
    }
    if total_invalid == 0:
        logger.info(f"[V4] OK — todas as respostas s1-s8 em [{S_MIN}, {S_MAX}] ou NA.")
    return df, report


# V5: Faixa de q 
def validate_q_column(
    df: pd.DataFrame,
    col: str = "q",
    logger: logging.Logger = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica se q está em [1, 7] ou NA. Marca inválidos como NA."""
    invalid = df[col].notna() & (~df[col].between(Q_MIN, Q_MAX))
    n_invalid = int(invalid.sum())
    report = {
        "validation": "q_range",
        "column": col,
        "invalid_marked_na": n_invalid,
        "passed": n_invalid == 0,
    }
    if n_invalid > 0:
        logger.warning(f"[V5] {n_invalid} valores inválidos em '{col}' — marcando como NA.")
        df.loc[invalid, col] = np.nan
    else:
        logger.info(f"[V5] OK — todos os valores de q em [{Q_MIN}, {Q_MAX}] ou NA.")
    return df, report


# V6: Cobertura de metadados 
def validate_metadata_coverage(
    df: pd.DataFrame,
    metadata_cols: list,
    logger: logging.Logger,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Verifica se registros têm metadados (não nulos) para os filmes."""
    missing_counts = {col: int(df[col].isna().sum()) for col in metadata_cols if col in df.columns}
    total_missing = sum(missing_counts.values())
    report = {
        "validation": "metadata_coverage",
        "columns": metadata_cols,
        "missing_counts": missing_counts,
        "passed": total_missing == 0,
    }
    if total_missing > 0:
        logger.warning(f"[V6] {total_missing} registros sem metadados: {missing_counts}")
    else:
        logger.info(f"[V6] OK — todos os registros possuem metadados de filme.")
    return df, report


# Runner: executa todas as validações 
def run_all_validations(
    df: pd.DataFrame,
    logger: logging.Logger,
) -> Tuple[pd.DataFrame, list]:
    """Executa todas as validações em sequência e retorna o DataFrame + relatórios."""
    reports = []

    df, r = validate_required_columns(df, REQUIRED_ANSWERS_COLS, logger)
    reports.append(r)

    df, r = validate_uniqueness(df, ["userId", "movieId"], logger)
    reports.append(r)

    df, r = validate_rating_range(df, "rating", logger)
    reports.append(r)

    df, r = validate_s_columns(df, logger)
    reports.append(r)

    df, r = validate_q_column(df, "q", logger)
    reports.append(r)

    return df, reports