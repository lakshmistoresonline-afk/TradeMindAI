import pandas as pd
df = pd.read_csv('docs/STEP4_EXPIRED_FORENSIC_AUDIT.csv')
gaps = df[df['extreme_gap_count'] > 0]
print(gaps[['symbol', 'signal_date', 'first_gap_pct']])
