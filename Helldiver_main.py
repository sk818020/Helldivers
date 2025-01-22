import streamlit as st
from seaborn.external.docscrape import header
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
from streamlit_dynamic_filters import DynamicFilters

st.set_page_config(layout="wide")

x = 12

res = requests.get("https://helldiverstrainingmanual.com/api/v1/war/campaign")
response = json.loads(res.text)
df = pd.DataFrame(response)
df.rename(columns={'players': 'player_count'}, inplace=True)
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
    "Note: the left graph uses minute by minute data, and the right uses every 5 minute data. This can lead to small differences"\
    " in player count.",
             height = 68
)

st.sidebar.image(r"https://th.bing.com/th/id/OIP.waKn6kIxrziGi7stnV6GGQHaC2?rs=1&pid=ImgDetMain")
st.sidebar.header('Choose selection:')

planet_filter = st.sidebar.multiselect(
    'Select Planet',
    options = df3['name'].unique()
)
faction_filter = st.sidebar.multiselect(
    'Select Faction',
    options = df3['faction'].unique(),
    default = df3['faction'].unique()
)

col1, col2 = st.columns(2)
fig1 = px.bar(df[df['faction'].isin(faction_filter)], x='faction', y='player_count', color = 'name',
              title = 'Player Count by Faction and Planet')
fig2 = px.line(df3[df3['faction'].isin(faction_filter)], x = 'created_at', y = 'player_count', color = 'name',
               title = 'Player Count by Planet and Time (last 24 hours, Mountain time)')

with col1:
    st.plotly_chart(fig1)
with col2:
    st.plotly_chart(fig2)
@st.cache_data
def convert_df(df3):
    return df3.to_csv(index=False).encode('utf-8')

csv = convert_df(df3)
st.download_button(
    "Press to download data",
    csv,
    "file.csv",
    "text/csv",
    key="download-csv"
)
st_aggrid.AgGrid(df3[df3['faction'].isin(faction_filter)])
