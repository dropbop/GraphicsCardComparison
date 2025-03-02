from flask import Flask, render_template
import plotly.graph_objs as go
import plotly.io as pio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

app = Flask(__name__)

# Define the Google Sheet ID
SHEET_ID = '1zjpAMjWHLXMZzyRfFNW4r_4vWBetVhNO7-blObtud0g'
# Replace with your worksheet name (tab name)
WORKSHEET_NAME = 'Toms Hardware'  # Update this to match your actual worksheet name

def get_sheet_data():
    # For local testing with a JSON file
    if os.path.exists('google-credentials.json'):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'google-credentials.json',
            ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
    # For production with environment variables
    else:
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
        if not credentials_json:
            # Return dummy data if no credentials found
            return pd.DataFrame({
                'Game': ['Test Game 1', 'Test Game 2'],
                'FPS': [100, 150],
                'GPU Specs': ['AD102, 16384 shaders, 2520MHz, 24GB GDDR6X@21Gbps, 1008GB/s, 450W',
                             'Navi 23, 2048 shaders, 2589MHz, 8GB GDDR6@16Gbps, 256GB/s, 160W']
            })
        
        credentials_info = json.loads(credentials_json)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_info,
            ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
    
    # Connect to Google Sheets
    client = gspread.authorize(credentials)
    
    try:
        # Open the sheet by ID and access the specific worksheet
        sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)
        
        # Get all values (including headers)
        all_data = sheet.get_all_values()
        
        # Convert to DataFrame
        headers = all_data[0]
        data = all_data[1:]
        df = pd.DataFrame(data, columns=headers)
        
        return df
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        # Return dummy data if there's an error
        return pd.DataFrame({
            'Game': ['Error Game 1', 'Error Game 2'],
            'FPS': [100, 150],
            'GPU Specs': ['AD102, 16384 shaders, 2520MHz, 24GB GDDR6X@21Gbps, 1008GB/s, 450W',
                         'Navi 23, 2048 shaders, 2589MHz, 8GB GDDR6@16Gbps, 256GB/s, 160W']
        })

def extract_gpu_info(df):
    """Extract VRAM and power values from GPU specs column"""
    if 'GPU Specs' in df.columns:
        # Extract VRAM (GB)
        df['VRAM'] = df['GPU Specs'].apply(lambda x: 
            int(x.split('GB')[0].split()[-1]) if 'GB' in x else None)
        
        # Extract power (W)
        df['Power'] = df['GPU Specs'].apply(lambda x: 
            int(x.split('W')[0].split()[-1]) if 'W' in x else None)
    
    return df

@app.route('/')
def index():
    # Get data from Google Sheets
    df = get_sheet_data()
    
    # Extract GPU info
    df = extract_gpu_info(df)
    
    # Create plots
    figures = []
    
    # FPS data visualization (assuming you have FPS data)
    if 'FPS' in df.columns and 'Game' in df.columns:
        fps_fig = go.Figure(
            data=go.Bar(
                x=df['Game'],
                y=df['FPS'].astype(float),
                marker_color='royalblue'
            )
        )
        fps_fig.update_layout(
            title="FPS by Game",
            xaxis_title="Game",
            yaxis_title="FPS",
            height=500
        )
        figures.append(pio.to_html(fps_fig, full_html=False))
    
    # VRAM vs Power scatter plot
    if 'VRAM' in df.columns and 'Power' in df.columns:
        scatter_fig = go.Figure(
            data=go.Scatter(
                x=df['Power'],
                y=df['VRAM'],
                mode='markers',
                text=df['GPU Specs'] if 'GPU Specs' in df.columns else None,
                marker=dict(
                    size=10,
                    color='firebrick',
                    opacity=0.7
                )
            )
        )
        scatter_fig.update_layout(
            title="GPU VRAM vs Power Requirement",
            xaxis_title="Power (W)",
            yaxis_title="VRAM (GB)",
            height=500
        )
        figures.append(pio.to_html(scatter_fig, full_html=False))
    
    # Check if any figures were created
    if not figures:
        # Create a dummy figure if no data columns were found
        dummy_fig = go.Figure(
            data=go.Scatter(
                x=[1, 2, 3, 4],
                y=[10, 20, 15, 25],
                mode='lines+markers'
            )
        )
        dummy_fig.update_layout(title="Sample Data (No Google Sheet Data Found)")
        figures.append(pio.to_html(dummy_fig, full_html=False))
    
    return render_template('index.html', plot_htmls=figures)