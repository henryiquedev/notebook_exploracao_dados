##  Instruções de execução

### Pré-requisitos

- Python 3.10+ (recomendado: 3.11 ou 3.12)
- pip atualizado
- ~500 MB de espaço em disco
- Conexão com a internet (para baixar o dataset)

### Passo 1: Clonar o repositório

```bash
git clone https://github.com/<usuario>/projeto-serendipidade-llm.git
cd projeto-serendipidade-llm
```

### Passo 2: Criar e ativar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\Activate.ps1     # Windows (PowerShell)
# venv\Scripts\activate.bat     # Windows (CMD)
```

### Passo 3: Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Baixar o dataset Serendipity-2018

1. Acesse http://grouplens.org/datasets/
2. Baixe `serendipity-2018.zip`
3. Extraia os arquivos para `data/raw/`:
   - `answers.csv` (obrigatório)
   - `movies.csv` (obrigatório)
   - `tag_genome.csv` (obrigatório)

Estrutura esperada:

```
data/
└── raw/
    ├── answers.csv
    ├── movies.csv
    └── tag_genome.csv
```

> ⚠️ Os arquivos do dataset **não são versionados** no Git por questões de tamanho e licença.

### Passo 5: Executar o pipeline

```bash
python run_pipeline.py
```

### Passo 6: Verificar as saídas

| Arquivo | Descrição |
| :--- | :--- |
| `data/processed/dataset_llm.csv` | Dataset final em CSV |
| `data/processed/dataset_llm.json` | Dataset final em JSON (ideal para LLM) |
| `data/processed/validation_report.json` | Relatório das validações |
| `logs/pipeline.log` | Log completo da execução |
| `data/cache/tag_genome_filtered.parquet` | Cache do tag genome |

###  Tempo de execução

| Cenário | Tempo estimado |
| :--- | :--- |
| Primeira execução (sem cache) | ~30-60 segundos |
| Execuções subsequentes (com cache) | ~5-10 segundos |
| Modo DEV (amostra) | ~3-5 segundos |

Para ativar o modo DEV, edite `src/config.py`:

```python
DEV_MODE = True
```
