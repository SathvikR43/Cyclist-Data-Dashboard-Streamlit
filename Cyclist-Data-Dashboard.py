import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Cyclist Data Dashboard",
    page_icon="🚴",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main background */
    .main {
        padding: 0rem 1rem;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
    }
    
    /* Storybook/App background */
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
    }
    
    /* Block container backgrounds */
    .block-container {
        background-color: transparent !important;
        padding: 2rem 1rem;
    }
    
    /* HIDE ALL WARNING/ALERT BOXES */
    .stAlert {
        display: none !important;
    }
    
    div[data-baseweb="notification"] {
        display: none !important;
    }
    
    .stException {
        display: none !important;
    }
    
    /* Remove yellow expander headers */
    .streamlit-expanderHeader {
        background-color: transparent !important;
    }
    
    /* Element container - remove yellow background */
    .element-container {
        background-color: transparent !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
    }
    
    /* Metric styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%) !important;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #64b5f6;
        box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
    }
    
    div[data-testid="stMetric"] label {
        color: #1565c0 !important;
        font-weight: 600;
        font-size: 1rem;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0d47a1 !important;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Headers */
    h1 {
        color: #0d47a1 !important;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(13, 71, 161, 0.1);
        background-color: transparent !important;
    }
    
    h2 {
        color: #1565c0 !important;
        font-weight: 600;
        background-color: transparent !important;
    }
    
    h3 {
        color: #1976d2 !important;
        background-color: transparent !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1976d2 0%, #1565c0 100%) !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #1976d2 0%, #1565c0 100%) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #1565c0 !important;
        font-weight: 600;
        background-color: transparent !important;
    }
    
    .stRadio > div {
        background-color: transparent !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: #ffffff !important;
        border: 2px solid #64b5f6;
        border-radius: 8px;
    }
    
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Horizontal rule */
    hr {
        border-color: #64b5f6 !important;
        opacity: 0.5;
    }
    
    /* Chart containers - remove yellow background */
    div[data-testid="stPlotlyChart"] {
        background-color: transparent !important;
    }
    
    /* Column containers */
    div[data-testid="column"] {
        background-color: transparent !important;
    }
    
    /* Vertical block */
    div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* All divs with white/yellow backgrounds */
    div[style*="background-color: rgb(255, 255, 255)"],
    div[style*="background-color: rgb(240, 242, 246)"],
    div[style*="background-color: white"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("🚴 Cyclist Data Overview Dashboard")
st.markdown("---")

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv('Cyclist-data.csv')
    
    # Parse datetime columns
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['ended_at'] = pd.to_datetime(df['ended_at'])
    
    # Calculate ride duration in minutes
    df['duration_minutes'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60
    
    # Extract time-based features
    df['hour'] = df['started_at'].dt.hour
    df['day_of_week'] = df['started_at'].dt.day_name()
    df['date'] = df['started_at'].dt.date
    df['month'] = df['started_at'].dt.month_name()
    
    # Calculate distance (approximate using Haversine formula)
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth's radius in km
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return R * c
    
    df['distance_km'] = haversine_distance(
        df['start_lat'], df['start_lng'], 
        df['end_lat'], df['end_lng']
    )
    
    return df

# Load data
with st.spinner('Loading data...'):
    df = load_data()

# Filter out invalid rides (negative or extremely long durations)
df_filtered = df[(df['duration_minutes'] > 0) & (df['duration_minutes'] < 1440)]

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Member type filter
member_types = st.sidebar.multiselect(
    "Member Type",
    options=df_filtered['member_casual'].unique(),
    default=df_filtered['member_casual'].unique()
)

# Bike type filter
bike_types = st.sidebar.multiselect(
    "Bike Type",
    options=df_filtered['rideable_type'].unique(),
    default=df_filtered['rideable_type'].unique()
)

# Apply filters
df_filtered = df_filtered[
    (df_filtered['member_casual'].isin(member_types)) &
    (df_filtered['rideable_type'].isin(bike_types))
]

# Key Metrics
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Rides", f"{len(df_filtered):,}")

with col2:
    avg_duration = df_filtered['duration_minutes'].mean()
    st.metric("Avg Duration", f"{avg_duration:.1f} min")

with col3:
    avg_distance = df_filtered['distance_km'].mean()
    st.metric("Avg Distance", f"{avg_distance:.2f} km")

with col4:
    member_pct = (df_filtered['member_casual'] == 'member').sum() / len(df_filtered) * 100
    st.metric("Member %", f"{member_pct:.1f}%")

st.markdown("---")

# Row 1: Rides over time and Member distribution
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Rides Over Time")
    daily_rides = df_filtered.groupby('date').size().reset_index(name='rides')
    daily_rides['date'] = pd.to_datetime(daily_rides['date'])
    
    fig_timeline = px.line(
        daily_rides, 
        x='date', 
        y='rides',
        title='Daily Ride Count',
        labels={'date': 'Date', 'rides': 'Number of Rides'}
    )
    fig_timeline.update_traces(line_color='#1976d2', line_width=2.5)
    fig_timeline.update_layout(
        height=350,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_timeline, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("👥 Member vs Casual")
    member_dist = df_filtered['member_casual'].value_counts().reset_index()
    member_dist.columns = ['Type', 'Count']
    
    fig_member = px.pie(
        member_dist,
        values='Count',
        names='Type',
        title='User Type Distribution',
        color='Type',
        color_discrete_map={'member': '#1976d2', 'casual': '#42a5f5'}
    )
    fig_member.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black')
    )
    st.plotly_chart(fig_member, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# Row 2: Hourly patterns and Day of week
col1, col2 = st.columns(2)

with col1:
    st.subheader("🕐 Rides by Hour of Day")
    hourly_rides = df_filtered.groupby('hour').size().reset_index(name='rides')
    
    fig_hourly = px.bar(
        hourly_rides,
        x='hour',
        y='rides',
        title='Ride Distribution by Hour',
        labels={'hour': 'Hour of Day', 'rides': 'Number of Rides'},
        color='rides',
        color_continuous_scale='Blues'
    )
    fig_hourly.update_layout(
        height=350,
        showlegend=False,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_hourly, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("📅 Rides by Day of Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_rides = df_filtered.groupby('day_of_week').size().reindex(day_order).reset_index(name='rides')
    daily_rides.columns = ['Day', 'Rides']
    
    fig_daily = px.bar(
        daily_rides,
        x='Day',
        y='Rides',
        title='Ride Distribution by Day',
        labels={'Day': 'Day of Week', 'Rides': 'Number of Rides'},
        color='Rides',
        color_continuous_scale='Blues'
    )
    fig_daily.update_layout(
        height=350,
        showlegend=False,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_daily, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# Row 3: Bike types and Duration distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚲 Bike Type Distribution")
    bike_dist = df_filtered['rideable_type'].value_counts().reset_index()
    bike_dist.columns = ['Bike Type', 'Count']
    
    fig_bike = px.bar(
        bike_dist,
        x='Bike Type',
        y='Count',
        title='Bike Type Usage',
        labels={'Bike Type': 'Type', 'Count': 'Number of Rides'},
        color='Bike Type',
        color_discrete_sequence=['#1565c0', '#1976d2', '#42a5f5']
    )
    fig_bike.update_layout(
        height=350,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_bike, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("⏱️ Ride Duration Distribution")
    # Filter extreme values for better visualization
    duration_filtered = df_filtered[df_filtered['duration_minutes'] <= 60]
    
    fig_duration = px.histogram(
        duration_filtered,
        x='duration_minutes',
        nbins=50,
        title='Ride Duration (up to 60 min)',
        labels={'duration_minutes': 'Duration (minutes)', 'count': 'Number of Rides'},
        color_discrete_sequence=['#1976d2']
    )
    fig_duration.update_layout(
        height=350,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_duration, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# Row 4: Heatmap and Distance
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Hour vs Day Heatmap")
    heatmap_data = df_filtered.groupby(['day_of_week', 'hour']).size().reset_index(name='rides')
    heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='rides').reindex(day_order)
    
    fig_heatmap = px.imshow(
        heatmap_pivot,
        title='Ride Intensity by Day and Hour',
        labels=dict(x="Hour of Day", y="Day of Week", color="Rides"),
        color_continuous_scale='Blues',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(color='#0d47a1'),
        yaxis=dict(color='#0d47a1')
    )
    st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("📍 Distance Distribution")
    # Filter extreme values for better visualization
    distance_filtered = df_filtered[df_filtered['distance_km'] <= 10]
    
    fig_distance = px.histogram(
        distance_filtered,
        x='distance_km',
        nbins=50,
        title='Ride Distance (up to 10 km)',
        labels={'distance_km': 'Distance (km)', 'count': 'Number of Rides'},
        color_discrete_sequence=['#1565c0']
    )
    fig_distance.update_layout(
        height=400,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_distance, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# Geographic Analysis
st.header("🗺️ Geographic Analysis - Station Usage")

# Prepare station data
@st.cache_data
def prepare_station_data(df):
    # Starting stations
    start_stations = df[df['start_station_name'].notna()].groupby(
        ['start_station_name', 'start_lat', 'start_lng']
    ).size().reset_index(name='start_count')
    
    # Ending stations
    end_stations = df[df['end_station_name'].notna()].groupby(
        ['end_station_name', 'end_lat', 'end_lng']
    ).size().reset_index(name='end_count')
    
    return start_stations, end_stations

start_stations, end_stations = prepare_station_data(df_filtered)

# Map type selector
map_type = st.radio(
    "Select Map View:",
    ["Most Popular Starting Stations", "Most Popular Ending Stations", "Station Connections (Top Routes)"],
    horizontal=True
)

if map_type == "Most Popular Starting Stations":
    # Top starting stations
    top_start = start_stations.nlargest(50, 'start_count')
    
    fig_map = px.scatter_map(
        top_start,
        lat='start_lat',
        lon='start_lng',
        size='start_count',
        color='start_count',
        hover_name='start_station_name',
        hover_data={'start_lat': False, 'start_lng': False, 'start_count': True},
        color_continuous_scale='Blues',
        size_max=30,
        zoom=11,
        title=f'Top 50 Starting Stations (Total: {len(start_stations)} stations)'
    )
    fig_map.update_layout(
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black')
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    
    # Show top 10 stations table
    st.subheader("📊 Top 10 Starting Stations")
    top_10_start = start_stations.nlargest(10, 'start_count')[['start_station_name', 'start_count']]
    top_10_start.columns = ['Station Name', 'Number of Rides']
    top_10_start.index = range(1, 11)
    st.dataframe(top_10_start, width='stretch')

elif map_type == "Most Popular Ending Stations":
    # Top ending stations
    top_end = end_stations.nlargest(50, 'end_count')
    
    fig_map = px.scatter_map(
        top_end,
        lat='end_lat',
        lon='end_lng',
        size='end_count',
        color='end_count',
        hover_name='end_station_name',
        hover_data={'end_lat': False, 'end_lng': False, 'end_count': True},
        color_continuous_scale='Blues',
        size_max=30,
        zoom=11,
        title=f'Top 50 Ending Stations (Total: {len(end_stations)} stations)'
    )
    fig_map.update_layout(
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black')
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    
    # Show top 10 stations table
    st.subheader("📊 Top 10 Ending Stations")
    top_10_end = end_stations.nlargest(10, 'end_count')[['end_station_name', 'end_count']]
    top_10_end.columns = ['Station Name', 'Number of Rides']
    top_10_end.index = range(1, 11)
    st.dataframe(top_10_end, width='stretch')

else:  # Station Connections
    # Find top routes
    routes = df_filtered[
        (df_filtered['start_station_name'].notna()) & 
        (df_filtered['end_station_name'].notna())
    ].groupby([
        'start_station_name', 'start_lat', 'start_lng',
        'end_station_name', 'end_lat', 'end_lng'
    ]).size().reset_index(name='count')
    
    # Filter out same station routes
    routes = routes[routes['start_station_name'] != routes['end_station_name']]
    top_routes = routes.nlargest(20, 'count')
    
    # Create map with lines connecting stations
    fig_map = go.Figure()
    
    # Add lines for routes
    for _, route in top_routes.iterrows():
        fig_map.add_trace(go.Scattermap(
            mode='lines',
            lon=[route['start_lng'], route['end_lng']],
            lat=[route['start_lat'], route['end_lat']],
            line=dict(width=2, color='rgba(25, 118, 210, 0.5)'),
            hoverinfo='skip',
            showlegend=False
        ))
    
    # Add starting points
    fig_map.add_trace(go.Scattermap(
        lat=top_routes['start_lat'],
        lon=top_routes['start_lng'],
        mode='markers',
        marker=dict(size=10, color='#1565c0'),
        text=top_routes['start_station_name'],
        hovertemplate='<b>Start:</b> %{text}<extra></extra>',
        name='Start Station',
        showlegend=True
    ))
    
    # Add ending points
    fig_map.add_trace(go.Scattermap(
        lat=top_routes['end_lat'],
        lon=top_routes['end_lng'],
        mode='markers',
        marker=dict(size=10, color='#42a5f5'),
        text=top_routes['end_station_name'],
        hovertemplate='<b>End:</b> %{text}<extra></extra>',
        name='End Station',
        showlegend=True
    ))
    
    fig_map.update_layout(
        map=dict(
            style='carto-positron',
            zoom=11,
            center=dict(
                lat=top_routes['start_lat'].mean(),
                lon=top_routes['start_lng'].mean()
            )
        ),
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0},
        title='Top 20 Most Popular Routes',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black')
    )
    
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})
    
    # Show top 10 routes table
    st.subheader("📊 Top 10 Most Popular Routes")
    top_10_routes = top_routes.nlargest(10, 'count')[
        ['start_station_name', 'end_station_name', 'count']
    ]
    top_10_routes.columns = ['From Station', 'To Station', 'Number of Rides']
    top_10_routes.index = range(1, 11)
    st.dataframe(top_10_routes, width='stretch')

st.markdown("---")

# Comparison: Member vs Casual behavior
st.header("🔍 Member vs Casual Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Duration by User Type")
    duration_comparison = df_filtered.groupby('member_casual')['duration_minutes'].mean().reset_index()
    duration_comparison.columns = ['User Type', 'Avg Duration (min)']
    
    fig_duration_comp = px.bar(
        duration_comparison,
        x='User Type',
        y='Avg Duration (min)',
        title='Average Ride Duration',
        color='User Type',
        color_discrete_map={'member': '#1976d2', 'casual': '#42a5f5'}
    )
    fig_duration_comp.update_layout(
        height=350,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_duration_comp, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("Average Distance by User Type")
    distance_comparison = df_filtered.groupby('member_casual')['distance_km'].mean().reset_index()
    distance_comparison.columns = ['User Type', 'Avg Distance (km)']
    
    fig_distance_comp = px.bar(
        distance_comparison,
        x='User Type',
        y='Avg Distance (km)',
        title='Average Ride Distance',
        color='User Type',
        color_discrete_map={'member': '#1976d2', 'casual': '#42a5f5'}
    )
    fig_distance_comp.update_layout(
        height=350,
        plot_bgcolor='rgba(255,255,255,0.5)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0d47a1', size=12),
        title_font=dict(color='#0d47a1', size=16, family='Arial Black'),
        xaxis=dict(gridcolor='#e0e0e0', color='#0d47a1'),
        yaxis=dict(gridcolor='#e0e0e0', color='#0d47a1')
    )
    st.plotly_chart(fig_distance_comp, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# Data table
st.header("📋 Raw Data Sample")
st.dataframe(df_filtered.head(100), width='stretch')

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚴 Cyclist Data Dashboard | Data refreshed on page load</p>
    </div>
    """, unsafe_allow_html=True)