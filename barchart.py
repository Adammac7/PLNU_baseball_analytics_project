import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import traceback
import numpy as np
import json
import os

class Pitcher:

    def __init__(self, name, pitches):
        self.name = name
        self.pitches = pitches  
        self.avg_speed = 0.0
        self.avg_spin = 0.0
        self.max_speed = 0.0
        self.max_spin = 0.0
        self.pitch_mix= 0

    def add_pitch(self, pitch):
        """
        Add a pitch to the pitcher's data.
        
        Args:
            pitch (Pitch): The pitch object to be added.
        """
        self.pitches.append(pitch)
        self.avg_speed = sum(p.rel_speed for p in self.pitches) / len(self.pitches)
        self.avg_spin = sum(p.spin_rate for p in self.pitches) / len(self.pitches)
        self.max_speed = max(p.rel_speed for p in self.pitches)
        self.max_spin = max(p.spin_rate for p in self.pitches)
        self.pitch_mix = len(set(p.pitch_type for p in self.pitches))



    
    
    

class Batter:
    """
    A class representing a baseball player with their pitches and stats.
    """
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.pitches = []  # Array to store pitch objects
        self.pitchers_faced = []
        self.at_bats= 0
        self.avg= 0.0
        self.obp= 0.0
        self.slg= 0.0
        self.ops= 0.0
        self.wobp= 0.0
        self.k_rate= 0.0
        self.bb_rate= 0.0

        self.hits= 0.0
        self.walks= 0.0
        self.strikeouts= 0.0
        self.total_bases= 0.0
        self.plate_appearances= 0.0
        #changed this to have a self. but dont know if it was a fix or if this is an error
        self.avg_exit_velocity = 0.0
        self.avg_launch_angle = 0.0
        self.max_exit_velocity = 0.0
        self.contacts = 0

       # 4x4 grid of plate zones, z1 = avg, z2 = slg, z3 = avg exit velocity
        self.plate_zones_avg = {
            0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # plate appearances, at bats, contacts, whiffs, hits, total bases, walks, strikeouts, avg exit velocity
            1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # plate appearances, at bats, contacts, whiffs, hits, total bases, walks, strikeouts, avg exit velocity
            2: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            4: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            7: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            9: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            10: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            11: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            12: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            13: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            14: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            15: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],
            16: [0, 0, 0, 0, 0, 0, 0, 0, 0,0],           
        }
                 # avg, slg, avg exit velocity, whiff rate
        self.plate_zone_stats = {
            0: [0, 0, 0, 0],
            1: [0, 0, 0, 0],
            2: [0, 0, 0, 0], 
            3: [0, 0, 0, 0],
            4: [0, 0, 0, 0],
            5: [0, 0, 0, 0],
            6: [0, 0, 0, 0],
            7: [0, 0, 0, 0],
            8: [0, 0, 0, 0],
            9: [0, 0, 0, 0],
            10: [0, 0, 0, 0],
            11: [0, 0, 0, 0],
            12: [0, 0, 0, 0],
            13: [0, 0, 0, 0],
            14: [0, 0, 0, 0],
            15: [0, 0, 0, 0],
            16: [0, 0, 0, 0]
        }
           
        # wOBA weights
        self.a = .69
        self.b = .89
        self.c = 1.27
        self.d = 1.62
        self.e = 2.10


    def get_outcome(self, pitch):   
        # print("pitch call ", pitch.pitch_call)
        # print("play result ", pitch.play_result)
        if pitch.pitch_call == "InPlay":
            if pitch.play_result == "Single":
                return "Single", True
            elif pitch.play_result == "Double":
                return "Double", True
            elif pitch.play_result == "Triple":
                return "Triple", True
            elif pitch.play_result == "HomeRun":
                return "HomeRun", True
            elif pitch.play_result == "Out":
                return "Out", True
            elif pitch.play_result == "Sacrifice":
                if pitch.tagged_result == "FlyBall":
                    return "Sac Fly", True
                elif pitch.tagged_result == "Bunt":
                    return "Sac Bunt", True
                else:
                    print("Tagged result ", pitch.tagged_result, " is not accounted for")
                    return "Undefined", True
        elif pitch.KorBB == "Strikeout":
            if pitch.pitch_call == "StrikeSwinging":
                return "Strikeout Swing", True
            elif pitch.pitch_call == "StrikeCalled":
                return "Strikeout Looking", True
            else:
                return "Strikeout", True
        elif pitch.KorBB == "Walk":
            return "Walk", True
        elif pitch.pitch_call == "StrikeSwinging":
            return "Whiff", False
        elif pitch.pitch_call == "StrikeCalled":
            return "Called Strike", False
        elif pitch.pitch_call == "BallCalled":
            return "Ball", False
        elif pitch.pitch_call == "BallIntentional":
            return "Intentional Ball", False
        elif pitch.pitch_call == "FoulBallNotFieldable" or pitch.pitch_call == "FoulBallFieldable":
            return "Foul ball", False
        elif pitch.pitch_call == "HitByPitch":
            return "Hit by Pitch", True
        else:
            print("play_call ", pitch.pitch_call, " is not accounted for")
            return "Undefined", False
             

    
    def add_pitch(self, p):
        self.pitches.append(p)
        self.pitchers_faced.append(p.pitcher_name)
        # add logic for batter stats vs a pitcher
        # if something happens count as an at bat
        if p.play_result == "Out":
            self.at_bats += 1
            self.plate_appearances += 1
            self.contacts += 1
            self.max_exit_velocity = p.exit_velocity if p.exit_velocity > self.max_exit_velocity else self.max_exit_velocity
            self.avg_exit_velocity += p.exit_velocity
            self.avg_launch_angle += p.launch_angle
            p.outcome,p.action = self.get_outcome(p)
        elif p.play_result != "Undefined" or p.KorBB != "Undefined":
            self.at_bats += 1
            self.plate_appearances += 1
            if p.play_result == "Single":
                self.hits += 1
                self.total_bases += 1
                self.contacts += 1
                self.max_exit_velocity = p.exit_velocity if p.exit_velocity > self.max_exit_velocity else self.max_exit_velocity
                self.avg_exit_velocity += p.exit_velocity
                self.avg_launch_angle += p.launch_angle
            elif p.play_result == "Double":
                self.hits += 1
                self.total_bases += 2
                self.contacts += 1
                self.max_exit_velocity = p.exit_velocity if p.exit_velocity > self.max_exit_velocity else self.max_exit_velocity
                self.avg_exit_velocity += p.exit_velocity
                self.avg_launch_angle += p.launch_angle
            elif p.play_result == "Triple":
                self.hits += 1
                self.total_bases += 3
                self.contacts += 1
                self.max_exit_velocity = p.exit_velocity if p.exit_velocity > self.max_exit_velocity else self.max_exit_velocity
                self.avg_exit_velocity += p.exit_velocity
                self.avg_launch_angle += p.launch_angle
            elif p.play_result == "HomeRun":
                self.hits += 1
                self.total_bases += 4
                self.contacts += 1
                self.max_exit_velocity = p.exit_velocity if p.exit_velocity > self.max_exit_velocity else self.max_exit_velocity
                self.avg_exit_velocity += p.exit_velocity
                self.avg_launch_angle += p.launch_angle
            elif p.KorBB == "Walk":
                self.walks += 1
                self.at_bats -= 1
            elif p.KorBB == "Strikeout":
                self.strikeouts += 1
        else:
            # print("Error entering batter stats during add pitch")
            pass
        p.outcome,p.action = self.get_outcome(p)
        p.zone = get_zone_number(p.plateLocSide, p.plateLocHeight,p.zone_width, p.zone_height_low, p.zone_height_high)
      
        # print("pzone ", p.zone)

        if p.zone in self.plate_zones_avg:
            if p.outcome == "Strikeout Swing":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][3] += 1 #whiffs
                self.plate_zones_avg[p.zone][7] += 1 #strikeouts
            elif p.outcome == "Strikeout Looking":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][7] += 1 #strikeouts 
            elif p.outcome == "Out":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][2] += 1 #contacts
                self.plate_zones_avg[p.zone][8] += p.exit_velocity #avg exit velocity
                self.plate_zones_avg[p.zone][9] += 1 #in play
            elif p.outcome == "Single":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][2] += 1 #contacts
                self.plate_zones_avg[p.zone][4] += 1 #hits
                self.plate_zones_avg[p.zone][5] += 1 #total bases
                self.plate_zones_avg[p.zone][8] += p.exit_velocity #avg exit velocity
                self.plate_zones_avg[p.zone][9] += 1 #in play
            elif p.outcome == "Double":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][2] += 1 #contacts
                self.plate_zones_avg[p.zone][4] += 1 #hits
                self.plate_zones_avg[p.zone][5] += 2 #total bases
                self.plate_zones_avg[p.zone][8] += p.exit_velocity #avg exit velocity
                self.plate_zones_avg[p.zone][9] += 1 #in play
            elif p.outcome == "Triple":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][2] += 1 #contacts
                self.plate_zones_avg[p.zone][4] += 1 #hits
                self.plate_zones_avg[p.zone][5] += 3 #total bases
                self.plate_zones_avg[p.zone][8] += p.exit_velocity #avg exit velocity
                self.plate_zones_avg[p.zone][9] += 1 #in play
            elif p.outcome == "HomeRun":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][1] += 1 #atbat
                self.plate_zones_avg[p.zone][2] += 1 #contacts
                self.plate_zones_avg[p.zone][4] += 1 #hits
                self.plate_zones_avg[p.zone][5] += 4 #total bases
                self.plate_zones_avg[p.zone][8] += p.exit_velocity #avg exit velocity
                self.plate_zones_avg[p.zone][9] += 1 #in play
            elif p.outcome == "Walk" or p.outcome == "Hit by Pitch":
                self.plate_zones_avg[p.zone][0] += 1 #pa
                self.plate_zones_avg[p.zone][6] += 1 #walks
            elif p.outcome == "Foul ball":
                self.plate_zones_avg[p.zone][2] += 1 #contacts
            elif p.outcome == "Whiff":
                self.plate_zones_avg[p.zone][3] += 1 #Whiffs
            
    def filter_pitches(self, data):
        for index, row in data.iterrows():
            if row['Batter'] == self.name:
                pitch = Pitch(
                    batter_name=row['Batter'],
                    pitcher_name=row['Pitcher'],
                    outcome="Undefined",
                    action="Undefined",
                    tagged_pitch_type=row['TaggedPitchType'],
                    auto_pitch_type=row['AutoPitchType'],
                    pitch_call=row['PitchCall'],
                    rel_speed=row['RelSpeed'],
                    spin_rate=row['SpinRate'],
                    IVB=row['InducedVertBreak'],
                    launch_angle=row['Angle'],
                    exit_velocity=row['ExitSpeed'],
                    tagged_result=row['TaggedHitType'],
                    play_result=row['PlayResult'],
                    KorBB=row['KorBB'],
                    plateLocHeight=row['PlateLocHeight'],
                    plateLocSide=row['PlateLocSide']
                )
                self.add_pitch(pitch)   

    def get_stats(self):
        #returns field variables as a dictionary
        data = {
            'name': self.name,
            'role': self.role,
            'hits': self.hits,
            'walks': self.walks,
            'strikeouts': self.strikeouts,
            'total bases': self.total_bases,
            'plate appearences': self.plate_appearances,
            'avg': self.avg,
            'obp': self.obp,
            'slg': self.slg,
            'ops': self.ops,
            'wobp': self.wobp,
            'k_rate': self.k_rate,
            'bb_rate': self.bb_rate,
            'avg_exit_velocity': self.avg_exit_velocity,
            'avg_launch_angle': self.avg_launch_angle,
            'max_exit_velocity': self.max_exit_velocity,    
            'plate_zone_stats': self.plate_zone_stats,
        }
        return data
                
    def calculate_stats(self):
        self.avg = self.hits / self.at_bats if self.at_bats > 0 else 0.0
        self.obp = (self.hits + self.walks) / self.plate_appearances if self.plate_appearances > 0 else 0.0
        self.slg = self.total_bases / self.at_bats if self.at_bats > 0 else 0.0
        self.ops = self.obp + self.slg 
        # wOBA is nonsense at the moment, fomula is wrong and weights are arbitray 
        self.wobp = (self.a * self.walks + self.b * self.hits + self.c * self.hits + self.d * self.hits + self.e * self.hits) / self.at_bats  if self.at_bats > 0 else 0.0
        self.k_rate = self.strikeouts / self.at_bats if self.at_bats > 0 else 0.0
        self.bb_rate = self.walks / self.plate_appearances if self.plate_appearances > 0 else 0.0

        self.avg_exit_velocity = self.avg_exit_velocity / self.contacts if self.contacts > 0 else 0.0
        self.avg_launch_angle = self.avg_launch_angle / self.contacts if self.contacts > 0 else 0.0
        
        # Calculate the average for each plate zone
        # AVG, SLG, AVG Exit Velocity, Whiff Rate
        # plate apearances, at bats, contacts, whiffs, hits, total bases, walks, strikeouts, summed exit velo,in play 
        print("Calculating batter stats...")
       
        for i in range(len(self.plate_zones_avg)):
            # if i == 1:
            #     print(self.plate_zones_avg[i][0] > 0)
            # print("plate zone ", i, " exit velo ", self.plate_zones_avg[i][8]," in play ", self.plate_zones_avg[i][9])
            # if self.plate_zones_avg[i][0] > 0:
                self.plate_zone_stats[i][0] = self.plate_zones_avg[i][4] / self.plate_zones_avg[i][1] if self.plate_zones_avg[i][1] > 0 else 0  # AVG = hits / at bats
                self.plate_zone_stats[i][1] = self.plate_zones_avg[i][5] / self.plate_zones_avg[i][1] if self.plate_zones_avg[i][1] > 0 else 0  # SLG = total bases / at bats
                self.plate_zone_stats[i][2] = self.plate_zones_avg[i][8] / self.plate_zones_avg[i][9] if self.plate_zones_avg[i][9] > 0 else 0  # AVG Exit Velocity = avg exit velocity / contacts
                self.plate_zone_stats[i][3] = self.plate_zones_avg[i][3] / (self.plate_zones_avg[i][3] + self.plate_zones_avg[i][2]) if (self.plate_zones_avg[i][3] + self.plate_zones_avg[i][2]) > 0 else 0
                # print("plate zone ", i, " whiffs ", self.plate_zones_avg[i][3], "  swings ", self.plate_zones_avg[i][2] + self.plate_zones_avg[i][3])
               
        
        print("Batter stats calculated.")
        # print("total exit velo: ", self.plate_zones_avg[2][8])
        # print("Batter stats: ", self.get_stats())        



    

        

class Pitch:
    def __init__(self, batter_name, pitcher_name, outcome, action, tagged_pitch_type, auto_pitch_type, pitch_call, 
                 rel_speed, spin_rate, IVB, launch_angle, exit_velocity, 
                 tagged_result, play_result, KorBB,plateLocHeight,plateLocSide):
        self.batter_name = batter_name
        self.pitcher_name = pitcher_name
        self.outcome = outcome
        self.action = action
        self.pitch_type = auto_pitch_type if auto_pitch_type else tagged_pitch_type
        self.pitch_call = pitch_call
        self.rel_speed = rel_speed
        self.spin_rate = spin_rate
        self.IVB = IVB
        self.launch_angle = launch_angle
        self.exit_velocity = exit_velocity
        self.tagged_result = tagged_result 
        self.play_result = play_result
        self.KorBB = KorBB
        self.plateLocHeight = plateLocHeight
        self.plateLocSide = plateLocSide

         # srikezone constants
        self.zone_width = 17 * 0.0833  # 17 inches converted to feet
        self.zone_height_low = 1.5     # Approximately knee height
        self.zone_height_high = 3.5    # Approximately mid-chest height
        
        if str(launch_angle).strip() in ["Undefined", ""]:
            print("launch angle is undefined")

    def __repr__(self):
        return f"Pitch({self.batter_name}, {self.pitcher_name},{self.outcome},{self.action},{self.pitch_type}, {self.rel_speed},{self.exit_velocity},{self.launch_angle})"
    
        

        

def filter_pitch_data(data, pitch_type=None, min_velocity=None):
    """
    Filter the DataFrame based on pitch characteristics.
    
    Parameters:
      - pitch_type: a string (e.g., "Fastball") to filter on the 'PitchType' column.
      - min_velocity: a numeric threshold for the 'RelSpeed' column.
      
    Returns the filtered DataFrame.
    """
    try:
        # Ensure the 'RelSpeed' column is numeric.
        data['RelSpeed'] = pd.to_numeric(data['RelSpeed'], errors='coerce')
        
        if pitch_type is not None:
            data = data[data['PitchType'] == pitch_type]
        if min_velocity is not None:
            data = data[data['RelSpeed'] > min_velocity]
        return data
    except Exception as e:
        print("Error in filter_pitch_data:", e)
        traceback.print_exc()
        return data

    


def create_player_stats_bar_chart(stats_df, selected_batter):
    """
    Create a bar chart showing one bar for each stat for the selected batter:
      - AVG, OBP, SLG, wOBP, K Rate, and BB Rate.
      
    The y-axis is scaled to accommodate rate stats (typically between 0 and 1).
    """
    try:
        # Filter the stats for the selected batter
        batter_stats = stats_df[stats_df['name'] == selected_batter]
        if batter_stats.empty:
            return {
                'data': [],
                'layout': {
                    'title': f"No stats found for {selected_batter}",
                    'xaxis': {'title': "Stat"},
                    'yaxis': {'title': "Value", 'range': [0, 1.2]},
                    'annotations': [{
                        'text': "No data for this batter.",
                        'xref': "paper",
                        'yref': "paper",
                        'x': 0.5,
                        'y': 0.5,
                        'showarrow': False
                    }]
                }
            }
        # Since grouping returns a single row per batter, extract it
        row = batter_stats.iloc[0]
        
        # Create a dictionary with the desired stats.
        stats = {
            'AVG': round(row['avg'], 3),
            'OBP': round(row['obp'], 3), 
            'SLG': round(row['slg'], 3),
            # 'wOBP': round(row['wobp'], 3), # uncomment if wOBA starts working
            'K Rate': round(row['k_rate'], 2),
            'BB Rate': round(row['bb_rate'], 2),
        }
        
        # Create bar chart with one bar per stat
        # List of stats with their corresponding number of decimal places

        # Create bar chart with rounded values
        
        fig_data = [
            go.Bar(
                x=list(stats.keys()),
                y = list(stats.values()),          
                marker=dict(color='green')
            )
        ]

        # Set the y-axis range to a maximum of 1.2 (or slightly higher if needed)
        y_max = max(1.2, max(stats.values()) * 1.1)
        layout = dict(
            title=f"Performance Stats for {selected_batter}",
            xaxis=dict(title="Stat"),
            yaxis=dict(title="Value", range=[0, y_max]),
            hovermode='closest',
            width=700,
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return {'data': fig_data, 'layout': layout}

    except Exception as e:
        print("Error in create_player_stats_bar_chart:", str(e))
        traceback.print_exc()
        return {
            'data': [],
            'layout': {
                'title': "Error generating stats bar chart",
                'xaxis': {'title': "Stat"},
                'yaxis': {'title': "Value", 'range': [0, 1.2]},
                'annotations': [{
                    'text': f"Error: {str(e)}",
                    'xref': "paper",
                    'yref': "paper",
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False
                }]
            }
        }



def get_zone_number(x, y, zone_width, zone_height_low, zone_height_high):
    x_sections = np.linspace(-zone_width/2, zone_width/2, 5)
    y_sections = np.linspace(zone_height_high, zone_height_low, 5)

    zone_num = 0
    for row in range(4):
        for col in range(4):
            x_min, x_max = x_sections[col], x_sections[col+1]
            y_max, y_min = y_sections[row], y_sections[row+1]
            if (x_min <= x <= x_max) and (y_min <= y <= y_max):
                zone_num = row * 4 + col + 1
                break
    return zone_num

def create_strike_zone_plot(data, title, batter, zone_stat_index, show_pitches):
    
    def get_color_gradient(value, min_val, max_val, base_color='red', reverse=False):
        norm = (value - min_val) / (max_val - min_val + 1e-9)
        if base_color == 'blue':
            color_map = plt.cm.Blues
        else:
            color_map = plt.cm.Reds
            norm = 1 - norm if reverse else norm
        rgba = color_map(norm)
        return f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, 0.5)'

    try:
        zone_width = 17 * 0.0833
        zone_height_low = 1.5
        zone_height_high = 3.5

        data['Zone'] = data.apply(lambda row: get_zone_number(
            row['PlateLocSide'], 
            row['PlateLocHeight'],
            zone_width,
            zone_height_low,
            zone_height_high
        ), axis=1)

        if 'exit_Velocity' in data.columns:
            data['exit_Velocity'] = data['exit_Velocity'].fillna(0.0)
        if 'launch_angle' in data.columns:
            data['launch_angle'] = data['launch_angle'].fillna(0.0)

        pitch_locations = go.Scatter(
            x=data['PlateLocSide'],
            y=data['PlateLocHeight'],
            mode='markers',
            name='Pitches',
            marker=dict(
                size=8,
                color='blue',
                opacity=0.6
            ),
            hovertemplate=(
                "Outcome: %{customdata[0]}<br>"
                "EV: %{customdata[1]:.1f}  LA: %{customdata[2]:.1f}<br>"
                "Pitch Type: %{customdata[3]}<br>"
                "Speed: %{customdata[4]:.1f} mph<br>"
                "Spin: %{customdata[5]:.0f} rpm<br>"
                "Zone: %{customdata[6]}"
                "<extra></extra>"
            ),
            customdata=data[['outcome', 'exit_Velocity', 'launch_angle', 'pitch_type', 'rel_Speed', 'spin_rate', 'Zone']].values,
            visible='legendonly' if not show_pitches else True
        )

        strike_zone = go.Scatter(
            x=[-zone_width/2, -zone_width/2, zone_width/2, zone_width/2, -zone_width/2],
            y=[zone_height_low, zone_height_high, zone_height_high, zone_height_low, zone_height_low],
            mode='lines',
            name='Strike Zone',
            line=dict(color='black', width=2),
            fill='none'
        )

        vertical_lines = []
        x_steps = np.linspace(-zone_width/2, zone_width/2, 5)
        for x in x_steps[1:-1]:
            vertical_lines.append(
                go.Scatter(
                    x=[x, x],
                    y=[zone_height_low, zone_height_high],
                    mode='lines',
                    line=dict(color='gray', width=1, dash='dash'),
                    showlegend=False,
                    hoverinfo='none'
                )
            )

        horizontal_lines = []
        y_steps = np.linspace(zone_height_low, zone_height_high, 5)
        for y in y_steps[1:-1]:
            horizontal_lines.append(
                go.Scatter(
                    x=[-zone_width/2, zone_width/2],
                    y=[y, y],
                    mode='lines',
                    line=dict(color='gray', width=1, dash='dash'),
                    showlegend=False,
                    hoverinfo='none'
                )
            )

        layout = dict(
            title=title,
            xaxis=dict(
                title='Horizontal Location (ft)',
                range=[-2, 2],
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=1
            ),
            yaxis=dict(
                title='Height from Ground (ft)',
                range=[0, 5],
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=1
            ),
            showlegend=True,
            width=600,
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        if zone_stat_index is not None and batter is not None:
            zone_annotations = []
            x_sections = np.linspace(-zone_width / 2, zone_width / 2, 5)
            y_sections = np.linspace(zone_height_high, zone_height_low, 5)
            z_num = 1
            for row in range(4):
                for col in range(4):
                    x_center = (x_sections[col] + x_sections[col + 1]) / 2
                    y_center = (y_sections[row] + y_sections[row + 1]) / 2
                    if z_num in batter.plate_zone_stats:
                        stat_value = float('{:.3g}'.format(batter.plate_zone_stats[z_num][zone_stat_index]))
                        zone_annotations.append(dict(
                            x=x_center,
                            y=y_center,
                            text=str(round(stat_value, 3)),
                            showarrow=False,
                            font=dict(color='black')
                        ))
                    z_num += 1
            layout['annotations'] = layout.get('annotations', []) + zone_annotations

            stat_values = [batter.plate_zone_stats.get(z, [0]*7)[zone_stat_index] for z in range(1, 17)]
            min_val = min(stat_values)
            max_val = max(stat_values)
            use_blue = (zone_stat_index == 3)
            base_color = 'blue' if use_blue else 'red'
            reverse = False

            layout.setdefault("shapes", [])
            for i, stat in enumerate(stat_values):
                row = i // 4
                col = i % 4
                x0 = x_sections[col]
                x1 = x_sections[col + 1]
                y0 = y_sections[row]
                y1 = y_sections[row + 1]
                color = get_color_gradient(stat, min_val, max_val, base_color=base_color)
                layout['shapes'].append(dict(
                    type="rect",
                    xref="x", yref="y",
                    x0=x0, x1=x1,
                    y0=y0, y1=y1,
                    fillcolor=color,
                    line=dict(width=0),
                    layer="below"
                ))

        all_traces = [strike_zone] + vertical_lines + horizontal_lines + [pitch_locations]
        return {
            'data': all_traces,
            'layout': layout
        }

    except Exception as e:
        print(f"Error creating strike zone plot: {str(e)}")
        return {
            'data': [],
            'layout': {
                'title': 'Error creating strike zone plot',
                'annotations': [{
                    'text': str(e),
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'x': 0.5,
                    'y': 0.5
                }]
            }
        }






def create_strike_zone_plot_from_pitches(batter, has_outcome, type_pitches,velo_min, velo_max, spin_min, spin_max, create_json, create_barchart, title, zone_stat_index, show_pitches):
    # Checks if outcomes is false only pitches with an outcome like walk, strikeout, etc. are included
    # If outcomes is true all pitches are included
    print("Creating strike zone plot from pitches...")
    custom_batter = Batter(batter.name,"Custom")
    pitches_data = {"PlateLocSide": [], "PlateLocHeight": [], "pitch_type": [], "outcome": [], "exit_Velocity": [], "launch_angle": [], "rel_Speed": [], "spin_rate": []}
    for p in batter.pitches:            
        if (has_outcome and p.action) or (not has_outcome):
            if type_pitches == "All" or p.pitch_type == type_pitches or (
                type_pitches == "Four-Seam" and p.pitch_type in {"Cutter", "Sinker"}):

                if(p.rel_speed >= velo_min and p.rel_speed <= velo_max) or (velo_max and velo_min == 0):
                    if( p.spin_rate >= spin_min and p.spin_rate <= spin_max) or (spin_max and spin_min == 0):

                        pitches_data["PlateLocSide"].append(p.plateLocSide)
                        pitches_data["PlateLocHeight"].append(p.plateLocHeight)
                        pitches_data["pitch_type"].append(p.pitch_type)
                        pitches_data["outcome"].append(p.outcome)
                        pitches_data["exit_Velocity"].append(p.exit_velocity)
                        pitches_data["launch_angle"].append(p.launch_angle)
                        pitches_data["rel_Speed"].append(p.rel_speed)
                        pitches_data["spin_rate"].append(p.spin_rate)

                        custom_batter.add_pitch(p)
               
    custom_batter.calculate_stats()
    # print(len(custom_batter.pitches))  

    data = pd.DataFrame(pitches_data)
    if create_barchart:
        # uncomment to output barchart
        bar_chart = create_player_stats_bar_chart(
            pd.DataFrame([custom_batter.get_stats()]), 
            custom_batter.name
        )
        pio.write_html(bar_chart, 'barchart.html', auto_open=True)

    if create_json:
        # Ensure the folder exists
        os.makedirs("player_jsons", exist_ok=True)

        # Sanitize the file name
        safe_name = custom_batter.name.replace(" ", "_").replace(",", "")
        safe_type = type_pitches.replace(" ", "_")
        json_name = f"player_jsons/{safe_name}_vs_{safe_type}.json"

        # Save JSON file
        with open(json_name, "w") as f:
            json.dump(custom_batter.get_stats(), f, indent=4)

    # Pass extra parameters
    return create_strike_zone_plot(data, title, batter=custom_batter, zone_stat_index=zone_stat_index, show_pitches=show_pitches)


def main():
    print("Running main function...")
    
    Battername = "Entrekin, Jake"  # edit player name here, this sets the filter of who we are looking for
    data = pd.read_csv('Regular Season Master CSV.csv')
    player = Batter(Battername, "gerneral") # general is for basic analysis, recomend changing general to a different role to distinguish filter paramters

    # Create a Pitch object from the first row
    # Iterate through each row in the DataFrame
    player.filter_pitches(data)
    player.calculate_stats()
    # now player has data from every pitch they have seen

    # filter paramteres, these will ensure all pitches are included, change as needed
    velo_min = 0
    velo_max = 200
    spin_min = 0
    spin_max = 4000


    str_fig = create_strike_zone_plot_from_pitches(
        player, 
        has_outcome=False, # when true only pitches with an outcome like walk, strikeout, etc. are included, false is all pitches
        type_pitches="All", # "All", "Fastball", "Curveball", "Slider", "Changeup" - sinker & cutter included with fastball
        velo_min= velo_min,
        velo_max= velo_max,
        spin_min= spin_min,
        spin_max = spin_max, 
        create_json=False,  # saves all batter data to a json file
        create_barchart=True, #creates a barchart to display batter stats
        title="Pitch Location Plot",  # arbitrary name
        zone_stat_index=2,       # 0 indicates batting average, 1 for slugging, 2 for avg exit velocity,4 for whiff rate
        show_pitches=True      # shows the dots for each pitch if true, only has color and zone metrics if false
    )
    pio.write_html(str_fig, 'strikezone.html', auto_open=True)
   
    
if __name__ == "__main__":
    main()

# to run the script in the terminal:
# you may need to create a virtual environment and install the required packages
#   python -m venv venv    in the terminal to create the enviornment with this commmand
#   .\venv\Scripts\activate       run this to activate the enviorment
#   python src/backend/visualizations/barchart.py    use this command to run the script, may need to change path to file once its in your directory