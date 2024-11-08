import numpy as np
import pandas as pd
import pulp

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
  
class sim:
  def __init__(self, df=None, player_path=None, team_path=None): # Add df and data_path as arguments
    self.cur_roster = []
    self.budget = 200
    
    if df is not None:  # Use df if provided
        self.market = df
    elif player_path is not None and team_path is not None:  # Load from data_path if provided
      
        self.market = df_load(player_path, team_path)
    else:
        raise ValueError("Either 'df' or 'data_path' must be provided.")
    self.cur_roster = []
    self.budget = 200
    self.market['available'] = 1
    self.market['actual_price'] = self.market['actual_price'].fillna(1)
    self.market['cur_price'] = self.market['actual_price']
    self.market=self.market.sort_values('2025 total', ascending=False)
    self.roster = pd.DataFrame(columns=self.market.columns)

  def my_pick(self, name, price):
    self.market_price(name, price)
    self.market_update()
    self.cur_roster.append(name)
    self.roster = self.market[self.market['player'].isin(self.cur_roster)]

  def other_pick(self, name, price):
    self.market.loc[self.market['player']==name,'available'] = 0
    self.market_price(name, price)
    self.market_update()

  def market_update(self):
    self.market['actual_price'] = self.market['cur_price']

  def market_reset(self):
    self.market['cur_price'] = self.market['actual_price']

  def market_price(self, name, price):
    self.market.loc[self.market['player']==name,'cur_price'] = price
    price_diff = price - self.market.loc[self.market['player']==name,'actual_price'].sum()
    rest_players = ((self.market['player']!=name) & (~self.market['player'].isin(self.cur_roster)) & (self.market['available']==1) & (self.market['cur_price']!=1)).values
    rest_money = self.market.loc[rest_players,'cur_price'].sum()
    self.market.loc[rest_players,'cur_price'] *= (rest_money-price_diff)/rest_money

  def fair_value(self, name):
    self.market_reset()
    # print(name)
    # print(self.market.loc[self.market['player']==name,'actual_price'])
    p = round(self.market.loc[self.market['player']==name,'actual_price'].values[0]+10)
    p_list = []
    while name not in p_list:

      p -= 1
      self.market_price(name, p)
      res = self.run_proposal()
      p_list = res['player'].values
      self.market_reset()
      if p == 0:
        break

    return p

  # def robust_proposal(self, price_up):



  def run_proposal(self):
    players = self.market['player'].fillna(0).values
    p = self.market['2025 total'].fillna(0).values
    c = self.market['cur_price'].fillna(0).values
    last = self.market['2024 avg'].fillna(0).values>=28
    growth = (self.market['2025 proj']-self.market['2024 total']).fillna(0).values>=0
    health = self.market['2024 gp'].fillna(0).values>=65

    pg = self.market['is_pg'].fillna(0).values
    sg = self.market['is_sg'].fillna(0).values
    sf = self.market['is_sf'].fillna(0).values
    pf = self.market['is_pf'].fillna(0).values
    center = self.market['is_c'].fillna(0).values

    budget = self.budget

    prob = pulp.LpProblem("Fantasy_Team_Optimization", pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("Player", players, cat="Binary")

    prob += pulp.lpSum([p[i] * player_vars[players[i]] for i in range(len(players))])

    prob += pulp.lpSum([c[i] * player_vars[players[i]] for i in range(len(players))]) <= budget

    prob += pulp.lpSum([player_vars[players[i]] for i in range(len(players))]) == 13

    pg_vars = pulp.LpVariable.dicts("PG", players, cat="Binary")
    sg_vars = pulp.LpVariable.dicts("SG", players, cat="Binary")
    g_vars = pulp.LpVariable.dicts("G", players, cat="Binary")
    sf_vars = pulp.LpVariable.dicts("SF", players, cat="Binary")
    pf_vars = pulp.LpVariable.dicts("PF", players, cat="Binary")
    f_vars = pulp.LpVariable.dicts("F", players, cat="Binary")
    c1_vars = pulp.LpVariable.dicts("C1", players, cat="Binary")
    c2_vars = pulp.LpVariable.dicts("C2", players, cat="Binary")
    u1_vars = pulp.LpVariable.dicts("U1", players, cat="Binary")
    u2_vars = pulp.LpVariable.dicts("U2", players, cat="Binary")
    u3_vars = pulp.LpVariable.dicts("U3", players, cat="Binary")
    b1_vars = pulp.LpVariable.dicts("B1", players, cat="Binary")
    b2_vars = pulp.LpVariable.dicts("B2", players, cat="Binary")
    b3_vars = pulp.LpVariable.dicts("B3", players, cat="Binary")

    if len(self.roster)>0:
      prob += pulp.lpSum([player_vars[name] for name in self.roster['player']]) >= 1

    prob += pulp.lpSum([pg_vars[players[i]] * pg[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([sg_vars[players[i]] * sg[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([g_vars[players[i]] * pg[i] * sg[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([sf_vars[players[i]] * sf[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([pf_vars[players[i]] * pf[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([f_vars[players[i]] * (sf[i] + pf[i]) for i in range(len(players))]) >= 1
    prob += pulp.lpSum([c1_vars[players[i]] * center[i] for i in range(len(players))]) >= 1
    prob += pulp.lpSum([c2_vars[players[i]] * center[i] for i in range(len(players))]) >= 1

    prob += pulp.lpSum([player_vars[players[i]] * pg[i] for i in range(len(players))]) >= 3
    prob += pulp.lpSum([player_vars[players[i]] * sg[i] for i in range(len(players))]) >= 3
    prob += pulp.lpSum([player_vars[players[i]] * sf[i] for i in range(len(players))]) >= 3
    prob += pulp.lpSum([player_vars[players[i]] * pf[i] for i in range(len(players))]) >= 3
    prob += pulp.lpSum([player_vars[players[i]] * center[i] for i in range(len(players))]) >= 4
    # prob += pulp.lpSum([player_vars[players[i]] * last[i] * health[i]* growth[i] for i in range(len(players))]) >= 6
    # prob += pulp.lpSum([player_vars[players[i]] * health[i] for i in range(len(players))]) >= 8
    prob += pulp.lpSum([player_vars[players[i]] * growth[i] * health[i] for i in range(len(players))]) >= 8
    # prob += pulp.lpSum([player_vars[players[i]] * last[i] * growth[i] for i in range(len(players))]) >= 8
    # prob += pulp.lpSum([player_vars[players[i]]  for i in range(len(players))]) >= 10
    # prob += pulp.lpSum([player_vars[players[i]]  for i in range(len(players))]) >= 10
    for i in range(len(players)):
        prob += player_vars[players[i]] == pg_vars[players[i]] + sg_vars[players[i]] + g_vars[players[i]] + sf_vars[players[i]] + pf_vars[players[i]] + f_vars[players[i]] + c1_vars[players[i]] + c2_vars[players[i]]+b1_vars[players[i]]+b2_vars[players[i]]+b3_vars[players[i]]+u1_vars[players[i]]+u2_vars[players[i]]+u3_vars[players[i]]
        prob += player_vars[players[i]] <= self.market['available'][i]

    o = prob.solve()
    if o == -1:
      print('unsolved')
    selected_players = []

    for i in range(len(players)):
      if player_vars[players[i]].varValue==1:
        selected_players.append(players[i])
    # for v in prob.variables():
    #     if v.varValue == 1:
    #         selected_players.append(v.name)
    # print(f"Selected Players: {selected_players}")
    # print(f"Total Projections: {pulp.value(prob.objective)}")
    proposal = self.market[self.market['player'].isin(selected_players)]
    return proposal


  def pressure_price(self, name):
      self.market_reset()
      # print(name)
      proposal = self.run_proposal()
      sec = sim()
      for p1 in proposal['player']:
        if p1!=name:
          # print(p1,name,p1!=name)
          sec.other_pick(p1, sec.fair_value(p1)+1)
      return sec.fair_value(name)


  def grow(self, name, price):
    roster = self.add_player(pick, self.cur_roster)
    self.market_price(pick, price)
    self.market_update()
