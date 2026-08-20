import pandas as pd
import numpy as np

def run():
    t_df = pd.read_csv('data/results/portfolio_trades.csv')
    e_df = pd.read_csv('data/results/portfolio_daily_equity.csv')
    t_df['exit_date'] = pd.to_datetime(t_df['exit_date'])
    e_df['date'] = pd.to_datetime(e_df['date'])
    daily_realized = t_df.groupby('exit_date')['pnl'].sum().reset_index()
    recon = pd.merge(e_df, daily_realized, left_on='date', right_on='exit_date', how='left').fillna(0)

    curr = 1000000.0
    results = []
    for i, row in recon.iterrows():
        curr += row['pnl']
        if row['pos_count'] == 0:
            diff = row['equity'] - curr
            if abs(diff) > 0.01:
                results.append({'date': row['date'], 'diff': diff})

    print(pd.DataFrame(results).head(20))

if __name__ == "__main__":
    run()
