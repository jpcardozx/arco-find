import pandas as pd

df = pd.read_csv('arco/consolidated_prospects.csv')
print(f'Total prospects: {len(df)}')

valid_websites = [w for w in df["Website"] if pd.notna(w) and w.strip()]
print(f'Valid websites: {len(valid_websites)}')

print('\nSample domains:')
for i, row in df.head(5).iterrows():
    website = row.get('Website', '')
    if website:
        domain = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
        print(f'  {row["Company"]} -> {domain}')