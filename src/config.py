"""
Configurações centralizadas do pipeline Serendipity-LLM.

Este módulo concentra paths, parâmetros e definições de schema,
permitindo que o pipeline seja ajustado sem modificar a lógica.
"""

from pathlib import Path

# ---------- Diretórios ----------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "data" / "cache"

# Criar diretórios necessários
for d in [RAW_DIR, PROCESSED_DIR, LOG_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------- Parâmetros do pipeline ----------
TOP_K_TAGS = 15              # Número de tags mais relevantes por filme
CHUNK_SIZE = 1_000_000       # Tamanho do chunk para leitura do tag_genome.csv
DEV_MODE = False             # Se True, usa apenas uma amostra do tag genome
DEV_SAMPLE_SIZE = 100_000    # Número de linhas no modo DEV

# ---------- Schema: colunas obrigatórias ----------
REQUIRED_ANSWERS_COLS = [
    "userId", "movieId", "rating", "timestamp",
    "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "q",
    "s_ser_rel", "s_ser_find", "s_ser_imp", "s_ser_rec",
    "m_ser_rel", "m_ser_find", "m_ser_imp", "m_ser_rec",
]

REQUIRED_MOVIES_COLS = ["movieId", "title", "genres", "directedBy", "starring"]

REQUIRED_GENOME_COLS = ["movieId", "tag", "relevance"]

#Domínios válidos (para validação)
RATING_MIN = 0.5
RATING_MAX = 5.0
RATING_STEP = 0.5

S_MIN = 1
S_MAX = 5

Q_MIN = 1
Q_MAX = 7

#Nomes dos arquivos de saída
OUTPUT_CSV = "dataset_llm.csv"
OUTPUT_JSON = "dataset_llm.json"
CACHE_GENOME = "tag_genome_filtered.parquet"
LOG_FILE = "pipeline.log"