import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio
from barchart import Batter

def get_zone_number(x, y, zone_width, zone_height_low, zone_height_high):
    import numpy as np
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

def create_strike_zone_plot(data, title="Pitch Location Plot", batter=None, zone_stat_index=None, enable_heatmap=False):
    """
    Create a strike zone plot with pitch locations.
    
    Args:
        data (pd.DataFrame): DataFrame containing pitch location data with columns:
            - PlateLocSide: Horizontal location (-2 to 2 feet from center)
            - PlateLocHeight: Vertical location (0 to 4 feet from ground)
        title (str): Title for the plot
        batter: Batter object containing plate_zone_stats
        zone_stat_index (int): Index for zone stats to display
        enable_heatmap (bool): Whether to display a heatmap instead of scatter points
    
    Returns:
        dict: Plotly figure dictionary with data and layout
    """
    try:
        # Define strike zone coordinates
        zone_width = 17 * 0.0833  # 17 inches converted to feet
        zone_height_low = 1.5     # Approximately knee height
        zone_height_high = 3.5    # Approximately mid-chest height

        # Add zone numbers to the data
        data['Zone'] = data.apply(lambda row: get_zone_number(
            row['PlateLocSide'], 
            row['PlateLocHeight'],
            zone_width,
            zone_height_low,
            zone_height_high
        ), axis=1)

        # Check if exit velo and launch angle are nan and set them to 0.0
        if 'exit_Velocity' in data.columns:
            data['exit_Velocity'] = data['exit_Velocity'].fillna(0.0)

        if 'launch_angle' in data.columns:
            data['launch_angle'] = data['launch_angle'].fillna(0.0)
        
        if enable_heatmap:
            pitch_locations = go.Histogram2d(
                x=data['PlateLocSide'],
                y=data['PlateLocHeight'],
                colorscale='Reds',
                showscale=True,
                opacity=0.6
            )
        else:
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
                customdata=data[['outcome', 'exit_Velocity', 'launch_angle', 'pitch_type', 'rel_Speed', 'spin_rate', 'Zone']].values
            )

        # Create strike zone outline
        strike_zone = go.Scatter(
            x=[-zone_width/2, -zone_width/2, zone_width/2, zone_width/2, -zone_width/2],
            y=[zone_height_low, zone_height_high, zone_height_high, zone_height_low, zone_height_low],
            mode='lines',
            name='Strike Zone',
            line=dict(color='black', width=2),
            fill='none'
        )

        # Create vertical grid lines
        vertical_lines = []
        x_steps = np.linspace(-zone_width/2, zone_width/2, 5)  # 5 points for 4 sections
        for x in x_steps[1:-1]:  # Skip first and last points (they're the border)
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

        # Create horizontal grid lines
        horizontal_lines = []
        y_steps = np.linspace(zone_height_low, zone_height_high, 5)  # 5 points for 4 sections
        for y in y_steps[1:-1]:  # Skip first and last points (they're the border)
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
            
        # Layout configuration
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

       # Add zone stat annotations
        if zone_stat_index is not None and batter is not None:
            zone_annotations = []
            x_sections = np.linspace(-zone_width / 2, zone_width / 2, 5)
            y_sections = np.linspace(zone_height_high, zone_height_low, 5)
            z_num = 1  # Start at 1 since 0 may be reserved (or just not shown)

            print("Entering zone stats...")
            for row in range(4):
                for col in range(4):
                    x_center = (x_sections[col] + x_sections[col + 1]) / 2
                    y_center = (y_sections[row] + y_sections[row + 1]) / 2

                    if z_num in batter.plate_zone_stats:

                        print(batter.plate_zone_stats[z_num][zone_stat_index])
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


        # Combine all traces
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

def create_strike_zone_plot_from_pitches(batter,has_outcome, type_pitches, title="Pitch Location Plot", zone_stat_index=None, enable_heatmap=False):
    # Checks if outcomes is false only pitches with an outcome like walk, strikeout, etc. are included
    # If outcomes is true all pitches are included
    import pandas as pd
    print("Creating strike zone plot from pitches...")
    custom_batter = Batter(batter.name,"Custom")
    pitches_data = {"PlateLocSide": [], "PlateLocHeight": [], "pitch_type": [], "outcome": [], "exit_Velocity": [], "launch_angle": [], "rel_Speed": [], "spin_rate": []}
    for p in batter.pitches:
        if not(has_outcome ^ p.action) and (type_pitches == p.pitch_type or type_pitches == "All"):
            pitches_data["PlateLocSide"].append(p.plateLocSide)
            pitches_data["PlateLocHeight"].append(p.plateLocHeight)
            pitches_data["pitch_type"].append(p.pitch_type)
            pitches_data["outcome"].append(p.outcome)
            pitches_data["exit_Velocity"].append(p.exit_velocity)
            pitches_data["launch_angle"].append(p.launch_angle)
            pitches_data["rel_Speed"].append(p.rel_speed)
            pitches_data["spin_rate"].append(p.spin_rate)

            custom_batter.add_pitch(p)
        else:
            print("ERROR")
    custom_batter.calculate_stats()
        # elif p.action and (type_pitches == p.pitch_type):
        #     pitches_data["PlateLocSide"].append(p.plateLocSide)
        #     pitches_data["PlateLocHeight"].append(p.plateLocHeight)
        #     pitches_data["pitch_type"].append(p.pitch_type)
        #     pitches_data["outcome"].append(p.outcome)
        #     pitches_data["exit_Velocity"].append(p.exit_velocity)
        #     pitches_data["launch_angle"].append(p.launch_angle)
        #     pitches_data["rel_Speed"].append(p.rel_speed)
        #     pitches_data["spin_rate"].append(p.spin_rate)
        # elif p.action and (type_pitches == "Fastballs" or p.pitch_type != "Sinker" or p.pitch_type != "Cutter") and (p.pitch_type == "Fastball" or p.pitch_type == "Sinker" or p.pitch_type == "Cutter"):
        #     pitches_data["PlateLocSide"].append(p.plateLocSide)
        #     pitches_data["PlateLocHeight"].append(p.plateLocHeight)
        #     pitches_data["pitch_type"].append(p.pitch_type)
        #     pitches_data["outcome"].append(p.outcome)
        #     pitches_data["exit_Velocity"].append(p.exit_velocity)
        #     pitches_data["launch_angle"].append(p.launch_angle)
        #     pitches_data["rel_Speed"].append(p.rel_speed)
        #     pitches_data["spin_rate"].append(p.spin_rate)
        # elif p.action and (type_pitches == "Changeups"and p.pitch_type == "Changeup"):
        #     pitches_data["PlateLocSide"].append(p.plateLocSide)
        #     pitches_data["PlateLocHeight"].append(p.plateLocHeight)
        #     pitches_data["pitch_type"].append(p.pitch_type)
        #     pitches_data["outcome"].append(p.outcome)
        #     pitches_data["exit_Velocity"].append(p.exit_velocity)
        #     pitches_data["launch_angle"].append(p.launch_angle)
        #     pitches_data["rel_Speed"].append(p.rel_speed)
        #     pitches_data["spin_rate"].append(p.spin_rate)
        # elif p.action and (type_pitches == "Curveballs" and p.pitch_type == "Curveball"):
        #     pitches_data["PlateLocSide"].append(p.plateLocSide)
        #     pitches_data["PlateLocHeight"].append(p.plateLocHeight)
        #     pitches_data["pitch_type"].append(p.pitch_type)
        #     pitches_data["outcome"].append(p.outcome)
        #     pitches_data["exit_Velocity"].append(p.exit_velocity)
        #     pitches_data["launch_angle"].append(p.launch_angle)
        #     pitches_data["rel_Speed"].append(p.rel_speed)
        #     pitches_data["spin_rate"].append(p.spin_rate)
    
    data = pd.DataFrame(pitches_data)
    # Pass extra parameters
    return create_strike_zone_plot(data, title, batter=custom_batter, zone_stat_index=zone_stat_index, enable_heatmap=enable_heatmap)