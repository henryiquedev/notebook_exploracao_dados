# Estatisticas para engenharia de prompt
print("\n=== ESTATISTICAS PARA PROMPT ENGINEERING ===")

# Distribuicao dos scores (para calibrar o LLM)
print(f"Media de s_ser_rel: {answers['s_ser_rel'].mean():.2f}")
print(f"Desvio padrao: {answers['s_ser_rel'].std():.2f}")

# Perfil do usuario "tipico" para contexto
avg_s = answers[s_cols].mean()
print("\n Perfil madio do usuario:")
for i, col in enumerate(s_cols, 1):
    print(f"  s{i}: {avg_s[col]:.2f}")

# Filmes mais serendipitosos (para exemplos nos prompts)
top_serendipitous = answers.nlargest(10, 's_ser_rel')
print("\nTop 10 filmes mais serendipitosos:")
# ... juntar com movies.csv para mostrar titulos 

