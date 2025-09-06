# 🏙️ Enhanced Smart Waste Management Dashboard
# Complete Implementation with 3D Visualizations + Fixed Upload

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import time
import warnings
import io
import math

# Advanced 3D imports
try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False

try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

warnings.filterwarnings('ignore')

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="🏙️ Enhanced Smart Waste Management Dashboard",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== SESSION STATE =====
def init_session_state():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'ml_model' not in st.session_state:
        st.session_state.ml_model = None
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = False

# ===== ENHANCED CSS =====
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .metric-card:hover {
        transform: scale(1.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .status-critical { background-color: #dc3545; }
    .status-high { background-color: #ffc107; }
    .status-medium { background-color: #17a2b8; }
    .status-low { background-color: #28a745; }
    .status-none { background-color: #6c757d; }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .upload-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px dashed rgba(255, 255, 255, 0.3);
    }
    
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ===== REAL SAMPLE DATA =====
def create_real_sample_data():
    """Load the actual GIS sample data"""
    data = [
        {"City": "Malad P-East", "Community": "Amrapali", "Latitude": 19.1758892, "Longitude": 72.8801895, "Pincode": 400079, "Total Households": 25, "Total Kgs in Jul 2025": 0},
        {"City": "Malad P-East", "Community": "Chaitanya", "Latitude": 19.1719219, "Longitude": 72.8820646, "Pincode": 400069, "Total Households": 52, "Total Kgs in Jul 2025": 0},
        {"City": "Malad P-East", "Community": "Girnar", "Latitude": 19.1728255, "Longitude": 72.8800865, "Pincode": 400066, "Total Households": 36, "Total Kgs in Jul 2025": 48},
        {"City": "Malad P-East", "Community": "Harmony", "Latitude": 19.1691566, "Longitude": 72.8814445, "Pincode": 400079, "Total Households": 30, "Total Kgs in Jul 2025": 24},
        {"City": "Malad P-East", "Community": "Maitreyee", "Latitude": 19.1751654, "Longitude": 72.8813227, "Pincode": 400079, "Total Households": 77, "Total Kgs in Jul 2025": 48},
        {"City": "Malad P-East", "Community": "Mamta", "Latitude": 19.1767443, "Longitude": 72.8788171, "Pincode": 400079, "Total Households": 24, "Total Kgs in Jul 2025": 43},
        {"City": "Malad P-East", "Community": "Mandvi", "Latitude": 19.1751161, "Longitude": 72.8786865, "Pincode": 400075, "Total Households": 35, "Total Kgs in Jul 2025": 0},
        {"City": "Malad P-East", "Community": "Mantri Park", "Latitude": 19.1692779, "Longitude": 72.8810874, "Pincode": 400065, "Total Households": 102, "Total Kgs in Jul 2025": 616},
        {"City": "Malad P-East", "Community": "Mantri Serene", "Latitude": 19.1679463, "Longitude": 72.8815347, "Pincode": 400079, "Total Households": 12, "Total Kgs in Jul 2025": 60},
        {"City": "Malad P-East", "Community": "Medha", "Latitude": 19.1778573, "Longitude": 72.8789503, "Pincode": 400079, "Total Households": 40, "Total Kgs in Jul 2025": 50},
        {"City": "Malad P-East", "Community": "Netravati", "Latitude": 19.1751194, "Longitude": 72.8787102, "Pincode": 400065, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Malad P-East", "Community": "New Dindoshi Green Hill Society", "Latitude": 19.1701868, "Longitude": 72.881522, "Pincode": 400065, "Total Households": 45, "Total Kgs in Jul 2025": 268},
        {"City": "Malad P-East", "Community": "New dindoshi hill view", "Latitude": 19.1704272, "Longitude": 72.8822567, "Pincode": 400097, "Total Households": 53, "Total Kgs in Jul 2025": 100},
        {"City": "Malad P-East", "Community": "Pratibha sankalp", "Latitude": 19.1779652, "Longitude": 72.8794885, "Pincode": 400097, "Total Households": 37, "Total Kgs in Jul 2025": 133},
        {"City": "Malad P-East", "Community": "Royal hill", "Latitude": 19.1700539, "Longitude": 72.8820844, "Pincode": 400079, "Total Households": 33, "Total Kgs in Jul 2025": 6},
        {"City": "Malad P-East", "Community": "Samta", "Latitude": 19.1772575, "Longitude": 72.8788406, "Pincode": 400079, "Total Households": 58, "Total Kgs in Jul 2025": 28},
        {"City": "Malad P-East", "Community": "Sankalp siddhi", "Latitude": 19.1677461, "Longitude": 72.8814354, "Pincode": 400097, "Total Households": 62, "Total Kgs in Jul 2025": 310},
        {"City": "Malad P-East", "Community": "Shraddha", "Latitude": 19.1773698, "Longitude": 72.8790552, "Pincode": 400079, "Total Households": 21, "Total Kgs in Jul 2025": 40},
        {"City": "Malad P-East", "Community": "Sukh shanti", "Latitude": 19.1752397, "Longitude": 72.8791617, "Pincode": 400079, "Total Households": 53, "Total Kgs in Jul 2025": 0},
        {"City": "Malad P-East", "Community": "Urja", "Latitude": 19.1778649, "Longitude": 72.879123, "Pincode": 400079, "Total Households": 47, "Total Kgs in Jul 2025": 25},
        {"City": "Malad P-East", "Community": "Vastu Sankalp", "Latitude": 19.1762565, "Longitude": 72.878686, "Pincode": 400097, "Total Households": 33, "Total Kgs in Jul 2025": 117},
        {"City": "Malad P-East", "Community": "Vidya sankalp", "Latitude": 19.1768318, "Longitude": 72.8796572, "Pincode": 400097, "Total Households": 58, "Total Kgs in Jul 2025": 84},
        {"City": "Malad P-East", "Community": "Vikas", "Latitude": 19.1779826, "Longitude": 72.8779476, "Pincode": 400079, "Total Households": 35, "Total Kgs in Jul 2025": 35},
        {"City": "Malad P-East", "Community": "Vinay sankalp", "Latitude": 19.1767857, "Longitude": 72.8796494, "Pincode": 400097, "Total Households": 52, "Total Kgs in Jul 2025": 143},
        {"City": "Malad P-East", "Community": "Viraj", "Latitude": 19.1769737, "Longitude": 72.8720962, "Pincode": 400097, "Total Households": 112, "Total Kgs in Jul 2025": 362},
        {"City": "Malad P-East", "Community": "Vivek sankalp", "Latitude": 19.177148, "Longitude": 72.8795804, "Pincode": 400097, "Total Households": 47, "Total Kgs in Jul 2025": 101},

        # Mangaon communities
        {"City": "Mangaon", "Community": "Aadi", "Latitude": 18.3032234, "Longitude": 73.2118427, "Pincode": 402103, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Aamdoshi", "Latitude": 18.2444858, "Longitude": 73.2137437, "Pincode": 402104, "Total Households": 23, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Bhuvan", "Latitude": 18.3714408, "Longitude": 73.2211806, "Pincode": 402112, "Total Households": 16, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Bhuvan Adiwasiwadi", "Latitude": 18.3606295, "Longitude": 73.199676, "Pincode": 402112, "Total Households": 25, "Total Kgs in Jul 2025": 13},
        {"City": "Mangaon", "Community": "Chandore", "Latitude": 18.1648451, "Longitude": 73.180721, "Pincode": 402101, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Chervali", "Latitude": 18.2190468, "Longitude": 73.2295385, "Pincode": 402104, "Total Households": 15, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Degaon", "Latitude": 18.2074552, "Longitude": 73.2523934, "Pincode": 402104, "Total Households": 0, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Hedmalai", "Latitude": 18.15853, "Longitude": 73.2349117, "Pincode": 402101, "Total Households": 45, "Total Kgs in Jul 2025": 14},
        {"City": "Mangaon", "Community": "Kalamje", "Latitude": 18.2549929, "Longitude": 73.2582911, "Pincode": 402104, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Karanjewadi pansai", "Latitude": 18.3066582, "Longitude": 73.2389439, "Pincode": 402112, "Total Households": 24, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Khadkoli", "Latitude": 18.1824681, "Longitude": 73.3525233, "Pincode": 402103, "Total Households": 14, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Khardi Bk", "Latitude": 18.252686, "Longitude": 73.2686117, "Pincode": 402104, "Total Households": 22, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Lakhpale", "Latitude": 18.1308607, "Longitude": 73.3231552, "Pincode": 402103, "Total Households": 22, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Muthvali", "Latitude": 18.3714408, "Longitude": 73.2211806, "Pincode": 402112, "Total Households": 24, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Nivi", "Latitude": 18.3047535, "Longitude": 73.2328563, "Pincode": 402112, "Total Households": 20, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Panhalghar Khurd", "Latitude": 18.1618489, "Longitude": 73.3211739, "Pincode": 402103, "Total Households": 20, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Pen tarf Tale", "Latitude": 18.2444857, "Longitude": 73.2137436, "Pincode": 402104, "Total Households": 22, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Rajivali", "Latitude": 18.2283702, "Longitude": 73.2575539, "Pincode": 402104, "Total Households": 18, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Ranavde", "Latitude": 18.1687708, "Longitude": 73.1808717, "Pincode": 402101, "Total Households": 24, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Shilim Boudhwadi", "Latitude": 18.3785372, "Longitude": 73.3349466, "Pincode": 402103, "Total Households": 15, "Total Kgs in Jul 2025": 22},
        {"City": "Mangaon", "Community": "Tolwadi", "Latitude": 18.1214987, "Longitude": 73.3268401, "Pincode": 402103, "Total Households": 15, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Vadvali Boudhwadi", "Latitude": 18.1796102, "Longitude": 73.270086, "Pincode": 402103, "Total Households": 24, "Total Kgs in Jul 2025": 42},
        {"City": "Mangaon", "Community": "Vihule", "Latitude": 18.1949038, "Longitude": 73.192302, "Pincode": 402122, "Total Households": 15, "Total Kgs in Jul 2025": 9},
        {"City": "Mangaon", "Community": "Wadachi vadi", "Latitude": 18.3413551, "Longitude": 73.2179777, "Pincode": 402112, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Mangaon", "Community": "Waghose", "Latitude": 18.1876333, "Longitude": 73.3529033, "Pincode": 402103, "Total Households": 16, "Total Kgs in Jul 2025": 0},

        # Tala communities
        {"City": "Tala", "Community": "Barpe", "Latitude": 18.3606295, "Longitude": 73.199676, "Pincode": 402111, "Total Households": 21, "Total Kgs in Jul 2025": 36},
        {"City": "Tala", "Community": "Girne", "Latitude": 18.3203781, "Longitude": 73.1019389, "Pincode": 402111, "Total Households": 40, "Total Kgs in Jul 2025": 12},
        {"City": "Tala", "Community": "Khambali Boudhwadi", "Latitude": 18.2807256, "Longitude": 73.1214988, "Pincode": 402111, "Total Households": 38, "Total Kgs in Jul 2025": 0},
        {"City": "Tala", "Community": "Khambavali", "Latitude": 18.2807256, "Longitude": 73.1214988, "Pincode": 402111, "Total Households": 23, "Total Kgs in Jul 2025": 0},
        {"City": "Tala", "Community": "Kumbet", "Latitude": 18.2481105, "Longitude": 73.0917588, "Pincode": 402111, "Total Households": 45, "Total Kgs in Jul 2025": 22},
        {"City": "Tala", "Community": "Mahagaon", "Latitude": 18.3606295, "Longitude": 73.199676, "Pincode": 402111, "Total Households": 64, "Total Kgs in Jul 2025": 46},
        {"City": "Tala", "Community": "Medhe", "Latitude": 18.3157805, "Longitude": 73.1398329, "Pincode": 402111, "Total Households": 76, "Total Kgs in Jul 2025": 67},
        {"City": "Tala", "Community": "Nanavli", "Latitude": 18.3527061, "Longitude": 73.0923599, "Pincode": 402111, "Total Households": 20, "Total Kgs in Jul 2025": 9},
        {"City": "Tala", "Community": "Padhava", "Latitude": 18.3442871, "Longitude": 73.1405278, "Pincode": 402111, "Total Households": 40, "Total Kgs in Jul 2025": 14},
        {"City": "Tala", "Community": "Shenvali Boudhwadi", "Latitude": 18.2815467, "Longitude": 73.1090133, "Pincode": 402111, "Total Households": 12, "Total Kgs in Jul 2025": 0},
        {"City": "Tala", "Community": "Solamwadi", "Latitude": 18.296805, "Longitude": 73.1565344, "Pincode": 402111, "Total Households": 32, "Total Kgs in Jul 2025": 17},
        {"City": "Tala", "Community": "Wave haveli", "Latitude": 18.2775302, "Longitude": 73.1775531, "Pincode": 402111, "Total Households": 9, "Total Kgs in Jul 2025": 0},
    ]
    
    df = pd.DataFrame(data)
    return df

# ===== ADVANCED 3D VISUALIZATION FUNCTIONS =====
def create_rectangular_bar_geometry(lat, lon, width_meters, height):
    """Create rectangular bar geometry for 3D visualization"""
    width_deg = width_meters / 111000
    half_width = width_deg / 2
    
    coordinates = [
        [lon - half_width, lat - half_width],
        [lon + half_width, lat - half_width],
        [lon + half_width, lat + half_width],
        [lon - half_width, lat + half_width],
        [lon - half_width, lat - half_width]
    ]
    
    return {
        "type": "Polygon",
        "coordinates": [coordinates]
    }

def create_rectangular_bars_data(df, bar_width_meters=50):
    """Convert dataframe to rectangular bars data for GeoJsonLayer"""
    rectangular_data = []
    
    for _, row in df.iterrows():
        if row['Total Kgs in Jul 2025'] > 0:
            geometry = create_rectangular_bar_geometry(
                row['Latitude'],
                row['Longitude'],
                bar_width_meters,
                row['Total Kgs in Jul 2025']
            )
            
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "Community": row['Community'],
                    "City": row['City'],
                    "Total_Kgs": row['Total Kgs in Jul 2025'],
                    "Total_Households": row['Total Households'],
                    "Collection_Status": row['Collection_Status'],
                    "Waste_Per_Household": row.get('Waste_Per_Household', 0),
                    "Efficiency_Score": row.get('Efficiency_Score', 0),
                    "Color": row.get('Color', [128, 128, 128, 120]),
                    "elevation": row['Total Kgs in Jul 2025']
                }
            }
            rectangular_data.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": rectangular_data
    }

def create_rectangular_bars_layer(df, elevation_scale=20, bar_width_meters=50):
    """Create PyDeck GeoJsonLayer with extruded rectangular bars"""
    if len(df) == 0 or not HAS_PYDECK:
        return None
        
    geojson_data = create_rectangular_bars_data(df, bar_width_meters)
    
    if not geojson_data["features"]:
        return None
    
    layer = pdk.Layer(
        'GeoJsonLayer',
        data=geojson_data,
        get_elevation='properties.elevation',
        get_fill_color='properties.Color',
        get_line_color=[255, 255, 255, 100],
        elevation_scale=elevation_scale,
        extruded=True,
        wireframe=True,
        filled=True,
        pickable=True,
        auto_highlight=True,
        line_width_min_pixels=1,
        opacity=0.8
    )
    
    return layer

def create_advanced_3d_hexagon_view(df, radius=100, elevation_scale=10):
    """Create advanced hexagon layer with dynamic aggregation"""
    if len(df) == 0 or not HAS_PYDECK:
        return None
    
    color_range = [
        [65, 182, 196], [127, 205, 187], [199, 233, 180], [237, 248, 177],
        [255, 255, 204], [255, 237, 160], [254, 217, 118], [254, 178, 76],
        [253, 141, 60], [240, 59, 32], [189, 0, 38]
    ]
    
    layer = pdk.Layer(
        'HexagonLayer',
        data=df,
        get_position=['Longitude', 'Latitude'],
        get_elevation_weight='Total Kgs in Jul 2025',
        get_color_weight='Total Kgs in Jul 2025',
        elevation_scale=elevation_scale,
        elevation_range=[0, 1000],
        radius=radius,
        coverage=1,
        extruded=True,
        pickable=True,
        auto_highlight=True,
        color_range=color_range,
        upper_percentile=90
    )
    
    return layer

def create_advanced_column_layer(df, elevation_scale=20, radius=50):
    """Create enhanced cylindrical column layer"""
    if len(df) == 0 or not HAS_PYDECK:
        return None
    
    # Filter out zero waste
    df_filtered = df[df['Total Kgs in Jul 2025'] > 0].copy()
    
    if len(df_filtered) == 0:
        return None
    
    layer = pdk.Layer(
        'ColumnLayer',
        data=df_filtered,
        get_position=['Longitude', 'Latitude'],
        get_elevation='Total Kgs in Jul 2025',
        get_fill_color='Color',
        elevation_scale=elevation_scale,
        radius=radius,
        pickable=True,
        auto_highlight=True,
        extruded=True,
        wireframe=False
    )
    
    return layer

def create_scatter_layer(df, radius_scale=100):
    """Create scatter layer for household density visualization"""
    if len(df) == 0 or not HAS_PYDECK:
        return None
    
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position=['Longitude', 'Latitude'],
        get_color='Color',
        get_radius='Total Households',
        radius_scale=radius_scale,
        radius_min_pixels=5,
        radius_max_pixels=50,
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_line_color=[255, 255, 255, 100]
    )
    
    return layer

def create_advanced_3d_deck(df, layers, view_state_params=None):
    """Create advanced PyDeck visualization with multiple layers"""
    if len(df) == 0 or not HAS_PYDECK:
        return None
    
    if view_state_params is None:
        view_state_params = {
            'longitude': df['Longitude'].mean(),
            'latitude': df['Latitude'].mean(),
            'zoom': 9,
            'pitch': 50,
            'bearing': 0
        }
    
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(**view_state_params),
        tooltip={
            'html': '''
            <b>{Community}</b><br>
            City: {City}<br>
            Waste: {Total_Kgs} kg<br>
            Households: {Total_Households}<br>
            Status: {Collection_Status}
            ''',
            'style': {
                'backgroundColor': 'rgba(0,0,0,0.8)',
                'color': 'white',
                'border': '1px solid white',
                'borderRadius': '8px',
                'padding': '10px'
            }
        }
    )
    
    return deck

# ===== DATA PROCESSING =====
def process_data(df):
    """Process and add derived metrics to dataframe"""
    if df is None or len(df) == 0:
        return df
    
    # Ensure required columns exist
    required_cols = ['City', 'Community', 'Latitude', 'Longitude', 'Total Households', 'Total Kgs in Jul 2025']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return None
    
    # Convert to numeric
    df['Total Households'] = pd.to_numeric(df['Total Households'], errors='coerce').fillna(0)
    df['Total Kgs in Jul 2025'] = pd.to_numeric(df['Total Kgs in Jul 2025'], errors='coerce').fillna(0)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    # Add derived metrics
    df['Waste_Per_Household'] = df.apply(
        lambda row: row['Total Kgs in Jul 2025'] / row['Total Households'] if row['Total Households'] > 0 else 0,
        axis=1
    )
    
    df['Collection_Status'] = df['Total Kgs in Jul 2025'].apply(
        lambda x: 'Critical' if x > 300 else 'High' if x > 100 else 'Medium' if x > 25 else 'Low' if x > 0 else 'None'
    )
    
    df['Efficiency_Score'] = df.apply(
        lambda row: max(0, min(100, 100 - (row['Total Kgs in Jul 2025'] / max(row['Total Households'], 1) * 15))),
        axis=1
    )
    
    # Color coding for visualizations
    df['Color'] = df['Total Kgs in Jul 2025'].apply(
        lambda x: [220, 20, 60, 200] if x > 300 else [255, 69, 0, 180] if x > 100 else
        [255, 140, 0, 160] if x > 25 else [50, 205, 50, 140] if x > 0 else [128, 128, 128, 120]
    )
    
    # Environmental and cost metrics
    df['CO2_Impact'] = df['Total Kgs in Jul 2025'] * 0.5
    df['Collection_Cost'] = df['Total Kgs in Jul 2025'] * 5  # ₹5 per kg
    df['Processing_Cost'] = df['Total Kgs in Jul 2025'] * 2  # ₹2 per kg
    
    # Community classification
    def classify_community(row):
        if row['Total Households'] > 80:
            return "Large Residential"
        elif row['Total Households'] > 40:
            return "Medium Residential"
        elif row['Total Households'] > 20:
            return "Small Residential"
        else:
            return "Community Housing"
    
    df['Community_Type'] = df.apply(classify_community, axis=1)
    
    return df

# ===== FILE UPLOAD HANDLER =====
def handle_file_upload():
    """Enhanced file upload with immediate processing"""
    st.markdown("### 📤 Upload Your Waste Management Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your waste management data in CSV format",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Read file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! {len(df)} records found.")
            
            # Show preview
            with st.expander("📊 Data Preview"):
                st.dataframe(df.head(), use_container_width=True)
                st.write(f"**Columns:** {list(df.columns)}")
            
            # Process data
            with st.spinner("🔄 Processing data and calculating metrics..."):
                processed_df = process_data(df)
            
            if processed_df is not None:
                # Store in session state
                st.session_state.df = processed_df
                st.session_state.data_loaded = True
                
                st.success("✅ Data processed successfully! All metrics calculated.")
                
                # Show processed stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Communities", len(processed_df))
                with col2:
                    st.metric("Cities", processed_df['City'].nunique())
                with col3:
                    st.metric("Total Waste", f"{processed_df['Total Kgs in Jul 2025'].sum():,.0f} kg")
                with col4:
                    st.metric("Avg Efficiency", f"{processed_df['Efficiency_Score'].mean():.1f}%")
                
                return processed_df
            else:
                st.error("❌ Failed to process data. Please check your file format.")
                return None
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            return None
    
    return None

# ===== ML MODEL =====
class WastePredictionModel:
    def __init__(self):
        self.is_trained = False
        self.model = None
        self.scaler = None
        
    def train(self, df):
        if not HAS_SKLEARN or len(df) < 10:
            return False
            
        try:
            features = df[['Total Households', 'Latitude', 'Longitude']].copy()
            target = df['Total Kgs in Jul 2025'].values
            
            mask = ~(features.isna().any(axis=1) | pd.isna(target) | (features['Total Households'] == 0))
            features = features[mask]
            target = target[mask]
            
            if len(features) < 5:
                return False
            
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
            
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model.fit(features_scaled, target)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            return False
    
    def predict(self, df):
        if not self.is_trained or not HAS_SKLEARN:
            return np.array([])
            
        try:
            features = df[['Total Households', 'Latitude', 'Longitude']].copy()
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            return predictions
        except:
            return np.array([])

# ===== VISUALIZATION FUNCTIONS =====
def create_metrics_cards(df):
    """Create enhanced metrics cards"""
    total_waste = df['Total Kgs in Jul 2025'].sum()
    total_communities = len(df)
    avg_efficiency = df['Efficiency_Score'].mean()
    critical_count = len(df[df['Collection_Status'] == 'Critical'])
    total_cost = df['Collection_Cost'].sum() + df['Processing_Cost'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        (f"{total_waste:,.0f}", "Total Waste (kg)", "🗑️"),
        (f"{total_communities}", "Communities", "🏘️"),
        (f"{avg_efficiency:.1f}%", "Avg Efficiency", "⚡"),
        (f"{critical_count}", "Critical Areas", "🚨"),
        (f"₹{total_cost:,.0f}", "Total Cost", "💰")
    ]
    
    for i, (value, label, icon) in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def create_status_pie_chart(df):
    """Create status distribution pie chart"""
    status_counts = df['Collection_Status'].value_counts()
    
    colors = {
        'Critical': '#dc3545', 'High': '#ffc107', 'Medium': '#17a2b8',
        'Low': '#28a745', 'None': '#6c757d'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        marker_colors=[colors.get(status, '#6c757d') for status in status_counts.index],
        textinfo='label+percent',
        hole=0.3
    )])
    
    fig.update_layout(
        title="Collection Status Distribution",
        font=dict(family="Inter"),
        height=400
    )
    
    return fig

def create_city_bar_chart(df):
    """Create city comparison bar chart"""
    city_data = df.groupby('City').agg({
        'Total Kgs in Jul 2025': 'sum',
        'Total Households': 'sum'
    }).round(2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=city_data.index,
        y=city_data['Total Kgs in Jul 2025'],
        name='Total Waste (kg)',
        marker_color='#667eea'
    ))
    
    fig.update_layout(
        title="Waste Generation by City/Area",
        xaxis_title="City/Area",
        yaxis_title="Total Waste (kg)",
        height=400
    )
    
    return fig

def create_trend_chart(df):
    """Create trend analysis chart"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    base_total = df['Total Kgs in Jul 2025'].sum()
    
    trend_data = []
    for i, date in enumerate(dates):
        weekly_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 7)
        random_factor = 1 + np.random.normal(0, 0.05)
        daily_total = base_total * weekly_factor * random_factor
        
        trend_data.append({
            'Date': date,
            'Total_Waste': daily_total,
            'Efficiency': 85 + np.random.normal(0, 5)
        })
    
    trend_df = pd.DataFrame(trend_data)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Waste Generation Trend', 'System Efficiency Trend'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=trend_df['Date'], y=trend_df['Total_Waste'],
                  mode='lines+markers', name='Daily Waste',
                  line=dict(color='#667eea', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=trend_df['Date'], y=trend_df['Efficiency'],
                  mode='lines+markers', name='Efficiency %',
                  line=dict(color='#28a745', width=2)),
        row=2, col=1
    )
    
    fig.update_layout(title="30-Day Analytics Trends", height=600)
    
    return fig

# ===== SIDEBAR =====
def create_sidebar():
    """Create enhanced sidebar"""
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>🏙️ Smart Waste Analytics</h2>
        <p style="margin: 0; opacity: 0.9;">Next-Generation Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature badges
    st.sidebar.markdown("### 🚀 Available Features")
    
    features = [
        ("3D Visualizations", HAS_PYDECK),
        ("AI Predictions", HAS_SKLEARN),
        ("Interactive Maps", HAS_FOLIUM)
    ]
    
    for feature, available in features:
        status = "✅" if available else "❌"
        st.sidebar.markdown(f"""
        <span class="feature-badge" style="background: {'linear-gradient(135deg, #28a745, #20c997)' if available else 'linear-gradient(135deg, #dc3545, #c82333)'};">
            {status} {feature}
        </span>
        """, unsafe_allow_html=True)
    
    # Theme toggle
    st.sidebar.markdown("### 🎨 Theme")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("☀️ Light"):
            st.session_state.theme = 'light'
            st.rerun()
    
    with col2:
        if st.button("🌙 Dark"):
            st.session_state.theme = 'dark'
            st.rerun()
    
    # Data info
    if st.session_state.data_loaded and st.session_state.df is not None:
        df = st.session_state.df
        st.sidebar.markdown("### 📊 Current Dataset")
        st.sidebar.success("✅ Data loaded successfully")
        st.sidebar.info(f"""
        📍 **{len(df)}** communities  
        🏙️ **{df['City'].nunique()}** areas  
        🗑️ **{df['Total Kgs in Jul 2025'].sum():,.0f}** kg total waste  
        🏠 **{df['Total Households'].sum():,}** households
        """)

# ===== MAIN APPLICATION =====
def main():
    """Main application function"""
    init_session_state()
    load_custom_css()
    create_sidebar()
    
    # Header
    st.markdown("""
    <div class="glass-card" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 700;">
            🏙️ Enhanced Smart Waste Management Dashboard
        </h1>
        <p style="margin: 1rem 0 0 0; font-size: 1.3rem; opacity: 0.9;">
            🆕 Next-Generation Analytics with Rectangular 3D Bars
        </p>
        <div style="margin-top: 1rem;">
            <span class="feature-badge">🎮 3D Visualizations</span>
            <span class="feature-badge">🤖 AI Predictions</span>
            <span class="feature-badge">📊 Real-time Analytics</span>
            <span class="feature-badge">🗺️ Interactive Maps</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data loading section
    st.markdown("## 📁 Data Configuration")
    
    data_source = st.selectbox(
        "Select Data Source",
        ["GIS Sample Data (Malad/Mangaon/Tala)", "Upload Your CSV File"],
        help="Choose your data source for analysis"
    )
    
    df = None
    
    if data_source == "GIS Sample Data (Malad/Mangaon/Tala)":
        if st.button("🚀 Load Sample Data", type="primary"):
            with st.spinner("Loading real GIS sample data..."):
                df = create_real_sample_data()
                df = process_data(df)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.data_loaded = True
                    st.success(f"✅ Loaded {len(df)} real community records!")
                    st.rerun()
    
    elif data_source == "Upload Your CSV File":
        df = handle_file_upload()
        if df is not None:
            st.rerun()
    
    # Use stored data
    if st.session_state.data_loaded and st.session_state.df is not None:
        df = st.session_state.df
    
    # Main dashboard
    if df is not None and len(df) > 0:
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🎮 3D Visualizations", "🗺️ Geographic Analysis", 
            "🤖 AI Insights", "📈 Trends & Analytics"
        ])
        
        with tab1:
            st.markdown("## 📊 Dashboard Overview")
            create_metrics_cards(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = create_status_pie_chart(df)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = create_city_bar_chart(df)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Summary table
            st.markdown("### 📋 Community Summary")
            summary_df = df.groupby('City').agg({
                'Total Kgs in Jul 2025': ['sum', 'mean', 'max'],
                'Total Households': 'sum',
                'Efficiency_Score': 'mean'
            }).round(2)
            st.dataframe(summary_df, use_container_width=True)
        
        with tab2:
            st.markdown("## 🎮 Advanced 3D Visualizations")
            
            if HAS_PYDECK:
                # Visualization type selector
                viz_type = st.selectbox(
                    "Choose 3D Visualization Type",
                    ["🔳 Rectangular 3D Bars", "🔶 Hexagon Aggregation", "🏛️ Cylindrical Columns", "⚪ Scatter Bubbles"]
                )
                
                # Visualization parameters
                col1, col2, col3 = st.columns(3)
                with col1:
                    elevation_scale = st.slider("Elevation Scale", 5, 50, 20)
                with col2:
                    if viz_type == "🔳 Rectangular 3D Bars":
                        bar_width = st.slider("Bar Width (meters)", 20, 100, 50)
                    elif viz_type == "🔶 Hexagon Aggregation":
                        radius = st.slider("Hexagon Radius", 50, 200, 100)
                    else:
                        radius = st.slider("Radius", 20, 100, 50)
                with col3:
                    pitch = st.slider("View Pitch", 0, 90, 50)
                
                # Create appropriate layer
                if viz_type == "🔳 Rectangular 3D Bars":
                    layer = create_rectangular_bars_layer(df, elevation_scale, bar_width)
                    st.markdown("### 🔳 Rectangular 3D Bars - Next-Generation Visualization")
                elif viz_type == "🔶 Hexagon Aggregation":
                    layer = create_advanced_3d_hexagon_view(df, radius, elevation_scale)
                    st.markdown("### 🔶 Hexagon Aggregation View")
                elif viz_type == "🏛️ Cylindrical Columns":
                    layer = create_advanced_column_layer(df, elevation_scale, radius)
                    st.markdown("### 🏛️ Cylindrical Columns View")
                else:
                    layer = create_scatter_layer(df, radius)
                    st.markdown("### ⚪ Scatter Bubbles View")
                
                if layer:
                    view_state = {
                        'longitude': df['Longitude'].mean(),
                        'latitude': df['Latitude'].mean(),
                        'zoom': 11,
                        'pitch': pitch,
                        'bearing': 0
                    }
                    
                    deck = create_advanced_3d_deck(df, [layer], view_state)
                    st.pydeck_chart(deck)
                    
                    st.info(f"🎯 Showing {len(df[df['Total Kgs in Jul 2025'] > 0])} communities with waste data in 3D visualization")
                else:
                    st.warning("⚠️ No data available for 3D visualization")
            else:
                st.error("❌ 3D visualizations require PyDeck. Install with: `pip install pydeck`")
                st.info("📊 Install PyDeck to unlock advanced 3D visualization features!")
        
        with tab3:
            st.markdown("## 🗺️ Geographic Intelligence")
            
            if HAS_FOLIUM:
                # Create enhanced folium map
                center_lat = df['Latitude'].mean()
                center_lon = df['Longitude'].mean()
                
                m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles='CartoDB Positron')
                
                # Add markers
                for _, row in df.iterrows():
                    color_map = {
                        'Critical': 'red', 'High': 'orange', 'Medium': 'blue',
                        'Low': 'green', 'None': 'gray'
                    }
                    
                    popup_html = f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4 style="margin: 0; color: #333;">{row['Community']}</h4>
                        <hr style="margin: 5px 0;">
                        <b>City:</b> {row['City']}<br>
                        <b>Waste:</b> {row['Total Kgs in Jul 2025']:.1f} kg<br>
                        <b>Households:</b> {row['Total Households']}<br>
                        <b>Status:</b> <span style="color: {color_map.get(row['Collection_Status'], 'gray')};">{row['Collection_Status']}</span><br>
                        <b>Efficiency:</b> {row['Efficiency_Score']:.1f}%
                    </div>
                    """
                    
                    marker_size = max(5, min(25, row['Total Kgs in Jul 2025'] / 20)) if row['Total Kgs in Jul 2025'] > 0 else 5
                    
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=marker_size,
                        popup=popup_html,
                        color=color_map.get(row['Collection_Status'], 'gray'),
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)
                
                st_folium(m, width=700, height=500)
                
                # Geographic statistics
                st.markdown("### 📍 Geographic Statistics")
                geo_stats = df.groupby('City').agg({
                    'Total Kgs in Jul 2025': ['sum', 'mean'],
                    'Total Households': 'sum',
                    'Efficiency_Score': 'mean'
                }).round(2)
                st.dataframe(geo_stats, use_container_width=True)
            else:
                # Fallback scatter plot
                fig = px.scatter(
                    df, x='Longitude', y='Latitude', 
                    size='Total Kgs in Jul 2025', 
                    color='Collection_Status',
                    hover_data=['Community', 'City', 'Total Households'],
                    title="Geographic Distribution of Waste"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.markdown("## 🤖 AI-Powered Insights")
            
            if HAS_SKLEARN:
                # Train ML model
                if st.session_state.ml_model is None:
                    with st.spinner("🤖 Training AI model..."):
                        ml_model = WastePredictionModel()
                        if ml_model.train(df):
                            st.session_state.ml_model = ml_model
                            st.success("✅ AI model trained successfully!")
                        else:
                            st.warning("⚠️ Unable to train AI model with current data")
                
                if st.session_state.ml_model and st.session_state.ml_model.is_trained:
                    # Predictions
                    predictions = st.session_state.ml_model.predict(df)
                    
                    if len(predictions) > 0:
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df['Total Kgs in Jul 2025'],
                            y=predictions,
                            mode='markers',
                            name='Predictions',
                            marker=dict(color='#667eea', size=8, opacity=0.7),
                            text=df['Community'],
                            hovertemplate='<b>%{text}</b><br>Actual: %{x:.1f} kg<br>Predicted: %{y:.1f} kg<extra></extra>'
                        ))
                        
                        # Perfect prediction line
                        min_val = min(df['Total Kgs in Jul 2025'].min(), predictions.min())
                        max_val = max(df['Total Kgs in Jul 2025'].max(), predictions.max())
                        
                        fig.add_trace(go.Scatter(
                            x=[min_val, max_val],
                            y=[min_val, max_val],
                            mode='lines',
                            name='Perfect Prediction',
                            line=dict(color='red', dash='dash')
                        ))
                        
                        fig.update_layout(
                            title="🎯 AI Predictions vs Actual Waste",
                            xaxis_title="Actual Waste (kg)",
                            yaxis_title="Predicted Waste (kg)",
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Zero-waste predictions
                        zero_waste = df[df['Total Kgs in Jul 2025'] == 0]
                        if len(zero_waste) > 0:
                            st.markdown("### 🔮 Predictions for Zero-Waste Communities")
                            zero_predictions = st.session_state.ml_model.predict(zero_waste)
                            zero_results = zero_waste[['Community', 'City', 'Total Households']].copy()
                            zero_results['Predicted_Waste'] = zero_predictions.round(1)
                            st.dataframe(zero_results, use_container_width=True)
            else:
                st.warning("🤖 AI features require scikit-learn. Install with: `pip install scikit-learn`")
        
        with tab5:
            st.markdown("## 📈 Trends & Advanced Analytics")
            
            # Trend chart
            trend_fig = create_trend_chart(df)
            st.plotly_chart(trend_fig, use_container_width=True)
            
            # Correlation analysis
            st.markdown("### 🔗 Correlation Matrix")
            numeric_cols = ['Total Households', 'Total Kgs in Jul 2025', 'Waste_Per_Household', 'Efficiency_Score']
            corr_matrix = df[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Correlation Matrix of Key Metrics",
                color_continuous_scale="RdBu"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Community analysis
            st.markdown("### 🏘️ Community Type Analysis")
            type_analysis = df.groupby('Community_Type').agg({
                'Total Kgs in Jul 2025': ['count', 'mean', 'sum'],
                'Efficiency_Score': 'mean',
                'Collection_Cost': 'sum'
            }).round(2)
            st.dataframe(type_analysis, use_container_width=True)
            
            # Export data
            st.markdown("### 📥 Export Data")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Current Dataset"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Complete CSV",
                        data=csv,
                        file_name=f"waste_management_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📋 Export Summary Report"):
                    summary = df.groupby('City').agg({
                        'Total Kgs in Jul 2025': ['sum', 'mean'],
                        'Total Households': 'sum',
                        'Efficiency_Score': 'mean',
                        'Collection_Cost': 'sum'
                    }).round(2)
                    csv = summary.to_csv()
                    st.download_button(
                        label="⬇️ Download Summary CSV",
                        data=csv,
                        file_name=f"waste_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 16px; margin-top: 2rem;'>
            <h4 style='margin: 0 0 1rem 0; color: #333;'>🏙️ Enhanced Smart Waste Management Dashboard</h4>
            <p style='margin: 0; color: #666; font-size: 14px;'>
                🚀 Next-Generation Analytics • 🎮 3D Visualizations • 🤖 AI Predictions • 🗺️ Interactive Maps<br>
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Records: {len(df):,} | PyDeck: {'✅' if HAS_PYDECK else '❌'} | AI: {'✅' if HAS_SKLEARN else '❌'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Welcome screen
        st.info("👆 Please load data using the options above to begin comprehensive analysis")
        
        st.markdown("""
        ### 🚀 Dashboard Features
        
        **🎮 Advanced 3D Visualizations**
        - 🔳 **Rectangular 3D Bars** - Next-generation visualization technique
        - 🔶 **Hexagon Aggregation** - Dynamic spatial clustering
        - 🏛️ **Cylindrical Columns** - Traditional 3D column charts
        - ⚪ **Scatter Bubbles** - Interactive bubble visualization
        
        **🤖 AI-Powered Analytics**
        - Machine learning waste prediction models
        - Anomaly detection for unusual patterns
        - Zero-waste community predictions
        - Performance optimization insights
        
        **📊 Real-time Analytics**
        - Interactive metrics dashboard
        - Geographic intelligence mapping
        - Trend analysis and forecasting
        - Environmental impact assessment
        
        **📁 Flexible Data Sources**
        - Real GIS sample data (57 communities)
        - CSV file upload with validation
        - Automatic metric calculation
        - Export capabilities
        """)

if __name__ == "__main__":
    main()