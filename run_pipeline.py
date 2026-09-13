from src.pipeline import run_pipeline

if __name__ == "__main__":
    df = run_pipeline()
    print(f"\nResumo: {len(df)} registros processados.")
    print(f"Colunas: {df.columns.tolist()}")