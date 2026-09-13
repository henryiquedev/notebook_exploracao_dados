"""
Pipeline de dados do projeto Serendipity-LLM.
Transforma o dataset Serendipity-2018 em um dataset estruturado
pronto para avaliação com LLMs como juízes.

Este módulo orquestra as etapas; as configurações ficam em config.py
e as validações em validators.py.
"""

import json
import logging
from typing import Tuple

import numpy as np
import pandas as pd

from src.config import (
    RAW_DIR, PROCESSED_DIR, LOG_DIR, CACHE_DIR,
    TOP_K_TAGS, CHUNK_SIZE, DEV_MODE, DEV_SAMPLE_SIZE,
    REQUIRED_MOVIES_COLS, REQUIRED_GENOME_COLS,
    OUTPUT_CSV, OUTPUT_JSON, CACHE_GENOME, LOG_FILE,
)
from src.validators import (
    run_all_validations,
    validate_metadata_coverage,
)


# ---------- Logging ----------
def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("pipeline")


# ---------- Etapa 1: Leitura ----------
def load_answers_and_movies(logger: logging.Logger) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("Lendo answers.csv e movies.csv...")

    answers = pd.read_csv(RAW_DIR / "answers.csv", encoding="utf-8")

    # movies.csv tem problemas de escape em algumas linhas
    # Usamos engine="python" + on_bad_lines="skip" para tolerância
    movies = pd.read_csv(
        RAW_DIR / "movies.csv",
        encoding="utf-8",
        engine="python",
        on_bad_lines="skip",
    )

    logger.info(f"answers.csv: {len(answers)} registros")
    logger.info(f"movies.csv: {len(movies)} registros")
    return answers, movies


def load_tag_genome(movie_ids: set, logger: logging.Logger) -> pd.DataFrame:
    """Carrega o tag genome, filtrando por filmes de interesse e usando cache."""
    cache_path = CACHE_DIR / CACHE_GENOME

    if cache_path.exists():
        logger.info(f"Carregando tag genome do cache: {cache_path}")
        return pd.read_parquet(cache_path)

    if DEV_MODE:
        logger.info(f"MODO DEV: carregando apenas {DEV_SAMPLE_SIZE} linhas do tag genome")
        genome = pd.read_csv(RAW_DIR / "tag_genome.csv", nrows=DEV_SAMPLE_SIZE)
    else:
        logger.info("Lendo tag_genome.csv em chunks...")
        chunks = []
        for chunk in pd.read_csv(
            RAW_DIR / "tag_genome.csv",
            encoding="utf-8",
            chunksize=CHUNK_SIZE,
        ):
            filtered = chunk[chunk["movieId"].isin(movie_ids)]
            if not filtered.empty:
                chunks.append(filtered)
        genome = pd.concat(chunks, ignore_index=True)

    logger.info(f"tag_genome.csv filtrado: {len(genome)} registros")
    genome.to_parquet(cache_path, index=False)
    logger.info(f"Cache salvo em {cache_path}")
    return genome


# ---------- Etapa 2: Limpeza de answers ----------
def clean_answers(answers: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Limpando answers.csv...")
    df = answers.copy()

    numeric_cols = ["rating", "timestamp"] + [f"s{i}" for i in range(1, 9)] + ["q"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    bool_cols = [c for c in df.columns if c.startswith(("s_ser_", "m_ser_"))]
    for col in bool_cols:
        df[col] = df[col].astype(str).str.upper().map({"TRUE": True, "FALSE": False})

    na_counts = df[[f"s{i}" for i in range(1, 9)] + ["q"]].isna().sum()
    logger.info(f"Valores NA em s1-s8 e q:\n{na_counts.to_string()}")
    return df


# ---------- Etapa 4: Filtrar movies ----------
def filter_movies(movies: pd.DataFrame, answers: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Filtrando movies.csv pelos filmes em answers.csv...")
    movie_ids = set(answers["movieId"].unique())
    filtered = movies[movies["movieId"].isin(movie_ids)].copy()

    for col in ["title", "genres", "directedBy", "starring"]:
        filtered[col] = filtered[col].fillna("").astype(str).str.strip()

    logger.info(f"movies.csv filtrado: {len(movies)} → {len(filtered)} filmes")
    return filtered


# ---------- Etapa 5: Extrair top-K tags ----------
def extract_top_tags(genome: pd.DataFrame, k: int, logger: logging.Logger) -> pd.DataFrame:
    logger.info(f"Extraindo top-{k} tags por filme...")
    genome_sorted = genome.sort_values(["movieId", "relevance"], ascending=[True, False])
    top = genome_sorted.groupby("movieId").head(k).copy()
    top["tag_weighted"] = top.apply(lambda r: f"{r['tag']} ({r['relevance']:.2f})", axis=1)
    agg = top.groupby("movieId")["tag_weighted"].apply(lambda x: "; ".join(x)).reset_index()
    agg.columns = ["movieId", "tags"]
    logger.info(f"Tags extraídas para {len(agg)} filmes")
    return agg


# ---------- Etapa 6: Join final ----------
def build_final_dataset(
    answers: pd.DataFrame,
    movies: pd.DataFrame,
    tags: pd.DataFrame,
    logger: logging.Logger,
) -> pd.DataFrame:
    logger.info("Construindo dataset final (join)...")
    df = answers.merge(movies, on="movieId", how="left", validate="many_to_one")
    df = df.merge(tags, on="movieId", how="left", validate="many_to_one")
    logger.info(f"Dataset final: {len(df)} registros, {len(df.columns)} colunas")
    return df


# ---------- Etapa 7: Serialização ----------
def serialize(df: pd.DataFrame, logger: logging.Logger) -> None:
    csv_path = PROCESSED_DIR / OUTPUT_CSV
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"CSV salvo em {csv_path}")

    json_path = PROCESSED_DIR / OUTPUT_JSON
    records = df.replace({np.nan: None}).to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON salvo em {json_path} ({len(records)} registros)")


# ---------- Orquestração ----------
def run_pipeline() -> pd.DataFrame:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("INÍCIO DO PIPELINE SERENDIPITY-LLM")
    logger.info("=" * 60)

    # Etapa 1: leitura inicial
    answers, movies = load_answers_and_movies(logger)

    # Etapa 2: limpeza
    answers = clean_answers(answers, logger)

    # Etapa 3: validações (V1-V5)
    answers, reports = run_all_validations(answers, logger)

    # Etapa 4: filtrar movies
    movies_f = filter_movies(movies, answers, logger)

    # Etapa 1b: carregar tag genome (com cache e filtragem)
    movie_ids = set(movies_f["movieId"].unique())
    genome = load_tag_genome(movie_ids, logger)

    # Etapa 5: extrair top-K tags
    tags = extract_top_tags(genome, TOP_K_TAGS, logger)

    # Etapa 6: join final
    final = build_final_dataset(answers, movies_f, tags, logger)

    # Etapa 3b: validação de cobertura de metadados (V6)
    final, r6 = validate_metadata_coverage(
        final, ["title", "genres", "tags"], logger
    )
    reports.append(r6)

    # Etapa 7: serialização
    serialize(final, logger)

    # Salvar relatório de validações
    report_path = PROCESSED_DIR / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    logger.info(f"Relatório de validações salvo em {report_path}")

    logger.info("=" * 60)
    logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
    logger.info("=" * 60)
    return final


if __name__ == "__main__":
    run_pipeline()