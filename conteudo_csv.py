import pandas as pd

conteudo_csv = """municipio, populacao
Niteroi, 515317
Sao Gonçalo, 1091737
Sao Paulo, 12396372
Belo Horzionte, 2530701
Florianopolis, 516524
Santo Andre, 723889
Santoo Andre, 700000
Rio de Janeiro, 6718903
Curitba, 1963726
Brasilia, 3094325"""

with open('input.csv', 'w') as f:
    f.write(conteudo_csv)

df_verificacao = pd.read_csv('input.csv', skipinitialspace=True)
print("Colunas detectadas:", df_verificacao.columns.tolist())