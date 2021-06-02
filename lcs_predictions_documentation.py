import pandas as pd
df = pd.read_csv('lol_data.csv')

lcs = df.loc[df['league'] == 'LCS']
lcs = lcs.loc[lcs['player'].isna()]
del lcs['datacompleteness']
del lcs['url']
del lcs['gameid']
del lcs['position']
del lcs['date']
del lcs['split']
del lcs['champion']
del lcs['patch']
del lcs['ban1']
del lcs['ban2']
del lcs['ban3']
del lcs['ban4']
del lcs['ban5']


reg_season = lcs.loc[lcs['playoffs']== 0]
del reg_season['game']
playoffs = lcs.loc[lcs['playoffs']== 1]

    

def getTeamData(team, season_table):
  return season_table.loc[season_table['team'] == team]



def getWinrate(team, season_table):
  #print(team_results)
  team_results = getTeamData(team, season_table)
  wins = len(team_results.loc[team_results['result'] == 1])
  losses = len(team_results.loc[team_results['result'] == 0])

  win_rate = wins / (wins + losses)
  return win_rate

def getWins(team, season_table):
    team_results = getTeamData(team, season_table)
    return len(team_results.loc[team_results['result'] == 1])

def getLosses(team, season_table):
    team_results = getTeamData(team, season_table)
    return len(team_results.loc[team_results['result'] == 0])


teams = ['Cloud9','Team Liquid','TSM','Evil Geniuses','Golden Guardians','Dignitas',
         'FlyQuest','100 Thieves','Immortals','Counter Logic Gaming']

wins = [getWins(team, reg_season) for team in teams]
losses = [getLosses(team, reg_season) for team in teams]
rawWinrate = [getWinrate(team, reg_season) for team in teams]

elo_dict = {'Teams': teams,
        'Wins': wins,
        'Losses': losses,
        'Games': [18]*len(teams),
        'Raw Win %': rawWinrate,
        'Round 1 Adj': [0.0]*len(teams),
        'Adjusted score': [0.0]*len(teams),
        
        }
elo_df = pd.DataFrame(elo_dict, columns = ['Teams', 'Wins', 'Losses', 'Games', 'Raw Win %', 'Round 1 Adj', 'Adjusted Score'])

def Team_Lookup(team_param, teams): #returns index of the team name you are looking for
    return teams.index(team_param)


# Takes an elo_df DataFrame as an input.
# Also takes a season_df DataFrame as an input.
# Returns a new DataFrame (adjusted_elo_df) with two new columns:
# round1 adj 
# and
# round1 win%
# these are computed via .....

def Adjustment_Round(elo_df, season_df, teams):
  #print(season_df)
  adjusted_elo_df = elo_df.copy()
  

  red_games = season_df.loc[season_df['side'] == 'Red']
  blue_games = season_df.loc[season_df['side'] == 'Blue']


  
  red_wp = len(red_games.loc[season_df['result'] == 1]) / len(red_games)
  blue_wp = len(blue_games.loc[season_df['result'] == 1]) / len(blue_games)

  league_avg = (red_wp + blue_wp) / 2
  red_adv = red_wp - league_avg
  blue_adv = blue_wp - league_avg
  
  

  start_line = 0
  end_line = len(red_games.index) - 1

  for start_line in range(end_line):
    blue_team = blue_games.iloc[start_line][6]
    red_team = red_games.iloc[start_line][6]
    red_score = red_games.iloc[start_line][9]
    blue_score = blue_games.iloc[start_line][9]
    
    red_lookup = Team_Lookup(red_team, teams)
    blue_lookup = Team_Lookup(blue_team, teams)
    #red lookup is an integer


    teamRedGames = red_games.loc[red_games['team'] == teams[red_lookup]]
    team_red_winrate = len(teamRedGames.loc[teamRedGames['result'] == 1])/ len(teamRedGames) 
    
    teamBlueGames = blue_games.loc[blue_games['team'] == teams[blue_lookup]]
    team_blue_winrate = len(teamBlueGames.loc[teamBlueGames['result'] == 1]) / len(teamBlueGames)
    
    red_diff = team_red_winrate - league_avg
    blue_diff = team_blue_winrate - league_avg

    if reg_season.iloc[start_line][4] == 'Red':    
      adjustRed = adjusted_elo_df.iloc[red_lookup, 5]
      adjusted_elo_df.iat[red_lookup, 5] = adjustRed + red_diff + red_adv
      
      adjustBlue = adjusted_elo_df.iloc[blue_lookup, 5] + blue_diff + blue_adv
      adjusted_elo_df.iat[blue_lookup, 5] = adjustBlue
    
    else:
      
      adjustRed = adjusted_elo_df.iloc[red_lookup, 5] + red_diff
      adjusted_elo_df.iat[red_lookup, 5] = adjustRed 
      
      adjustBlue = adjusted_elo_df.iloc[blue_lookup, 5] + red_diff
      adjusted_elo_df.iat[blue_lookup, 5] = adjustBlue

  start_line = 0
  for start_line in range(len(teams)):
    adj = adjusted_elo_df.iloc[start_line, 5]
    games = 18

    adjusted_elo_df.iat[start_line, 5] = adj / games
    adjusted_elo_df.iat[start_line, 6] = adjusted_elo_df.iloc[start_line][4] + (adj / games)
  print(adjusted_elo_df)

def main():
  Adjustment_Round(elo_df, reg_season, teams)

main()