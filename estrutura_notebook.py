# 01_exploracao_dados.ipynb

# 1. Importacao de bibliotecas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 2. Carregamento dos dados
answers = pd.read_csv('../dataset/answers.csv')
movies = pd.read_csv('../dataset/movies.csv')
training = pd.read_csv('../dataset/training.csv')
tags = pd.read_csv('../dataset/tags.csv')
tag_genome = pd.read_csv('../dataset/tag_genome.csv')
recommendations = pd.read_csv('../dataset/recommendations.csv')

# 3. Analise geral dos dados
print("=== ANSWERS.CSV ===")
print(f"Registros: {len(answers)}")
print(f"Usuarios unicos: {answers['userId'].nunique()}")
print(f"Filmes unicos: {answers['movieId'].nunique()}")
print(f"Colunas: {answers.columns.tolist()}")
print(f"Valores ausentes:\n{answers.isnull().sum()}")

print("\n=== MOVIES.CSV ===")
print(f"Registros: {len(movies)}")
print(f"Filmes unicos: {movies['movieId'].nunique()}")
print(f"Colunas: {movies.columns.tolist()}")
print(f"Generos unicos: {movies['genres'].str.split('|').explode().nunique()}")

print("\n=== TRAINING.CSV ===")
print(f"Registros: {len(training)}")
print(f"Usuarios unicos: {training['userId'].nunique()}")
print(f"Filmes unicos: {training['movieId'].nunique()}")

# 4. Analise da variavel alvo (serendipidade)
# Distribuicao dos scores de serendipidade
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# ... graficos para s_ser_rel, s_ser_find, s_ser_imp, s_ser_rec

# 5. Analise das respostas dos usuarios (s1-s8)
# Distribuicao das respostas as afirmacoes
s_cols = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
# ... heatmap de correlacao

# 6. Analise da distribuicao de ratings
# ... histograma e boxplot

# 7. Analise temporal
# ... periodo coberto pelos dados

# 8. Analise de metadados dos filmes
# Distribuicao de generos
# ... top generos, relacao com serendipidade

# 9. Analise de tags e tag genome
# ... tags mais relevantes, correlacao com serendipidade

# 10. Preparacao para LLM
# Selecao de amostra para prompts
# ... extrair filmes com respostas de serendipidade

# 11. Sumario executivo para o LLM
# Estatisticas descritivas para orientar os prompts