import numpy as np
import pandas as pd

def df_load(player_path, team_path):
  df = pd.read_csv(player_path)
  team_df = pd.read_csv(team_path).rename(columns={"short":'team'})
  df.rename(columns={'team':'team-position'},inplace=True)
  df['team'] = df['team-position'].apply(lambda x: x[:3])
  df['position'] = df['team-position'].apply(lambda x: x[6:])
  df.iloc[0,-1] = 'C'
  df.iloc[1,-1] = 'C'
  df[['is_pg',	'is_sg',	'is_sf',	'is_pf',	'is_c']].fillna(0)
  df['2024 gp'] = round(df['2024 total']/df['2024 avg'])
  df['2023 gp'] = round(df['2023 total']/df['2023 avg'])
  df = df.merge(team_df, on='team')
  #pts estimation
  df['2025 total'] = df['2025 proj']/82*df['before playoff']+df['2025 proj']/82*df['playoff week']*2
  #price adjustment
  df['proj'] = df['proj'].apply(lambda x: 1 if x==0 else x)
  df = df.sort_values('2025 total', ascending=False).reset_index().iloc[:,1:]
  proj_total = df[:90]['proj'].sum()
  actual_total = df[:90]['avg'].sum()
  df.loc[110:150,'actual_price']=1
  df.loc[90:110,'actual_price']=2
  df.loc[:90,'proj_price'] = df.loc[:90,'proj']*1940/proj_total
  df.loc[:90,'actual_price'] = df.loc[:90,'avg']*1940/actual_total
  df.iloc[57,0] = 'Mi. Bridges'
  df.iloc[138,0] = 'As. Thompson'
  return df
