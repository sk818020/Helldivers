import streamlit as st
from st_aggrid import AgGrid
import st_aggrid
import json
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events
import plotly.express as px
import datetime as dt

st.set_page_config(layout="wide")

res = requests.get("https://helldiverstrainingmanual.com/api/v1/war/campaign")
response = json.loads(res.text)
df = pd.DataFrame(response)
l_planets = df['planetIndex'].unique().tolist()
df3 = pd.DataFrame()
for i in l_planets:
    planet = str(i)
    planet_name = df[df['planetIndex'] == int(planet)]['name'].iloc[0]
    res = requests.get("https://helldiverstrainingmanual.com/api/v1/war/history/{x}".format(x = planet))
    response = json.loads(res.text)
    df2 = pd.DataFrame(response)
    df2['created_at'] = pd.to_datetime(df2['created_at'])
    df2['created_at'] = df2['created_at'].dt.tz_convert('MST')
    df3 = pd.concat([df3, df2])
map1 = df[['planetIndex', 'name', 'faction']]
df3 = pd.merge(df3, map1, left_on='planet_index', right_on='planetIndex')
df3['created_at'] = pd.to_datetime(df3['created_at'])
df3['created_at'] = df3['created_at'].dt.tz_convert('MST')


stamp = dt.datetime.now().strftime('%m/%d/%y - %H:%M')
st.title('Helldivers 2 Player Count Analysis - {x} MST'.format(x = stamp))
st.text_area("",
    "Note: the left graph uses minute by minute data, and the right uses every 5 minute minute data. This can lead to small differences"\
    " in player count.",
             height = 68
)
fig1 = px.bar(df, x='faction', y='players', color = 'name',
              title = 'Player Count by Faction and Planet')
fig2 = px.line(df3, x = 'created_at', y = 'player_count', color = 'name',
               title = 'Player Count by Planet and Time (last 24 hours, Mountain time)')

st.sidebar.header('Choose selection:')
planet_filter = st.sidebar.selectbox(
    'Select Planet',
    options = df3['name'].unique()
)
faction_filter = st.sidebar.selectbox(
    'Select Faction',
    options = df3['faction'].unique()
)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1)
with col2:
    st.plotly_chart(fig2)
st_aggrid.AgGrid(df3)
