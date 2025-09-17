import pandas as pd
import glob

# Consolidar todos os CSVs
files = glob.glob('arco/apollo-accounts-export*.csv')
all_data = []
for f in files:
    df = pd.read_csv(f)
    all_data.append(df)

consolidated = pd.concat(all_data, ignore_index=True)
print(f'Total consolidado: {len(consolidated)} prospects')

# Salvar arquivo consolidado
consolidated.to_csv('arco/consolidated_prospects.csv', index=False)
print('Arquivo consolidado salvo: arco/consolidated_prospects.csv')

# Mostrar algumas estatísticas
print(f'Indústrias: {consolidated["Industry"].value_counts().head()}')
print(f'Funcionários médio: {consolidated["# Employees"].mean():.1f}')