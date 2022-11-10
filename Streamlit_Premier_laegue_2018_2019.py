#import packages
import streamlit as st
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from PIL import Image
import seaborn as sns
import numpy as np
#from statsmodels.formula.api import ols
import streamlit.components.v1 as components
import geopandas as gdp
import folium
import geopandas.tools
import seaborn
#import osmnx as ox
#import networkx as nx
import geopandas as gpd
import requests



#title
st.markdown("<h1 style='text-align: center; color: black;'>Premier League 2018/19</h1>", unsafe_allow_html=True)

#create header
st.markdown("<h4 style='text-align: center; color: black;'>Dashboard gemaakt door Boris, Julius en Semih</h4>", unsafe_allow_html=True)



#import datasets
match = pd.read_csv('Wedstrijden.csv').iloc[:, 1:]
voorspelling = pd.read_csv('voorspelling.csv')
balbezit = pd.read_csv('balbezit.csv')
players = pd.read_csv('players1819.csv')
Toeschouwers1 = pd.read_csv('Toeschouwers.csv')
landen_plot = pd.read_csv('Landen_aantal.csv')
landen_plotje = pd.read_csv('Landen_aantal-UK.csv')
speelronde = pd.read_csv('speelrondes.csv').iloc[:, 1:]
data = pd.read_csv('Punten.csv')
team_kaarten = pd.read_csv('team_kaarten.csv')
df_ref_info = pd.read_csv('df_ref_info.csv')
lijstjes = pd.read_csv('lijstjes.csv').iloc[:, 1:]
top10 = pd.read_csv('top10_deel2.csv').iloc[:10, 1:]
elftallen = ['Manchester City', 'Liverpool', 'Chelsea', 'Tottenham Hotspur', 'Arsenal',
 'Manchester United', 'Wolverhampton Wanderers','Everton', 'Leicester City', 'West Ham United']


top10['Average Goals Stadium'] = top10['Average Goals Stadium'].apply(lambda x: round(x, 2) )
top10['Average age team'] = top10['Average age team'].apply(lambda x: round(x, 2) )
spelers = players[players['Current Club'].isin(elftallen)]
df = match[['date_GMT', 'home_team_name','away_team_name','Game Week','home_team_goal_count',
       'away_team_goal_count']]
df.columns = ['Datum', 'Thuisploeg', 'Uitploeg', 'Game', 'Thuis', 'Uit']
df.head()



def page_intro():
    video_file = open('PremierPromo.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

    
    

def page_one():
    ronden = st.slider('Speelronde:', 1, 38, 1)
    wedstrijden = match[match['Game Week'] <= ronden]

    
    teams = []
    winst = []
    gelijk = []
    verlies = []
    doelpunten = []
    doelpunten_tegen = []
    punten = []
    for i,x in wedstrijden.iterrows(): 
        teams.append(x['home_team_name'])
        teams.append(x['away_team_name'])
        winst.append(x['winst'])
        winst.append(x['verlies'])
        gelijk.append(x['gelijk'])
        gelijk.append(x['gelijk'])
        verlies.append(x['verlies'])
        verlies.append(x['winst'])
        doelpunten.append(x['home_team_goal_count'])
        doelpunten.append(x['away_team_goal_count'])
        doelpunten_tegen.append(x['away_team_goal_count'])
        doelpunten_tegen.append(x['home_team_goal_count'])
        punten.append(x['punten thuis'])
        punten.append(x['punten uit'])

    stand = pd.DataFrame(teams)
    stand.columns = ['Team']
    stand['Winst'] = winst
    stand['Gelijk'] = gelijk
    stand['Verlies'] = verlies
    stand['Doelpunten'] = doelpunten
    stand['Doelpunten tegen'] = doelpunten_tegen
    stand['Doelsaldo'] = stand['Doelpunten'] - stand['Doelpunten tegen']
    stand['Punten'] = punten
    stand = stand.groupby('Team').sum()
    stand = stand.reset_index()
    stand = stand[stand['Team'].isin(elftallen)]
    stand = stand.sort_values(['Punten','Doelsaldo'], ascending=False).reset_index()
    stand = stand.drop(['index'], axis=1)
    stand['Speelronde'] = ronden
    tussenstap = pd.DataFrame({'Ranglijst' : range(1, 11, 1)})
    stand['Positie'] = tussenstap['Ranglijst']
    stand = stand[['Positie', 'Team', 'Speelronde','Winst','Gelijk','Verlies','Doelpunten','Doelpunten tegen','Doelsaldo','Punten']]
    st.table(stand)
    
    st.markdown("Speelronde")
    ronde = speelronde[speelronde['Week'] == ronden]
    st.table(ronde)

    
    
    
    
def page_two():
    
    options = st.sidebar.multiselect(
    'Welke Teams wilt u selecteren?',
    ['Manchester City', 'Liverpool', 'Chelsea', 'Tottenham Hotspur', 'Arsenal',
 'Manchester United', 'Wolverhampton Wanderers','Everton', 'Leicester City', 'West Ham United'],
    ['Manchester City', 'Liverpool', 'Chelsea', 'Tottenham Hotspur', 'Arsenal',
 'Manchester United', 'Wolverhampton Wanderers','Everton', 'Leicester City', 'West Ham United'])
       
        
        
        
    players['Actual Birthday'] = players['age'] - 3    
    GK = players[players['position']=='Goalkeeper']['Actual Birthday']
    DEF = players[players['position']=='Defender']['Actual Birthday']
    MID = players[players['position']=='Midfielder']['Actual Birthday']
    FOR = players[players['position']=='Forward']['Actual Birthday']
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=GK, name='Doelmannen'))
    fig.add_trace(go.Histogram(x=DEF, name='Verdedigers'))
    fig.add_trace(go.Histogram(x=MID, name='Middenvelders'))
    fig.add_trace(go.Histogram(x=FOR, name='Aanvallers'))
    fig.update_layout(
        title="Leeftijd per linie",
        xaxis_title="Leeftijd",
        yaxis_title="Aantal spelers",
        legend_title="Legenda")
    st.plotly_chart(fig)
    
    
    
    
    fig = px.box(balbezit, x="team", y="balbezit", color='Top10')
    fig.update_layout(
    title="Balbezit per team",
    xaxis_title="Elftallen",
    yaxis_title="Hoeveelheid balbezit",
    legend_title="Legenda")
    st.plotly_chart(fig)
    

    #model
    def punten(data, elftal):
        team = [elftal]
        teams = elftal
        df2 = data[data['Thuisploeg'].isin(team) | data['Uitploeg'].isin(team)]
        df = df2.sort_values(by=['Game'])
        punten = []
        wed = []
        cumsum = []
        
        for i in range(df.shape[0]):
            HT = df.iloc[i]['Thuisploeg']
            AT = df.iloc[i]['Uitploeg']
            W = df.iloc[i]['Game']
            GT = df.iloc[i]['Thuis']
            GU = df.iloc[i]['Uit']
            punt = df.iloc[i]['Thuis'] - df.iloc[i]['Uit']
            
            if AT == teams:
                if punt < 0:
                    point = 3
                elif punt == 0:
                    point = 1
                elif punt > 0 :
                    point = 0
            if HT == teams:
                if punt > 0:
                    point = 3
                elif punt == 0:
                    point = 1
                elif punt < 0 :
                    point = 0
                    
            punten.append(point)
            wed.append(W)
            cumsum = np.cumsum(punten)   
    
        return_df = pd.DataFrame({'Wedstrijd':wed, elftal:cumsum})
        return return_df   


    
    
    fig = px.line(data, x='Wedstrijd', y=options, labels={
                         "value": "Aantal punten",
                         "Wedstrijd": "Speelronde",
                         "variable": "Clubs"}, 
                  title='Puntenverloop over het hele seizoen')
    st.plotly_chart(fig)
    
    
    
    
    dropdown_buttons = [{'label': 'Thuis & uit doelpunten', 'method': 'update',
                      'args': [{'visible': [True, True]},
                              {'title': 'Thuis & uit doelpunten'}]},
                    {'label': 'Thuis doelpunten', 'method': 'update', 
                     'args': [{'visible': [True, False]},
                              {'title': 'Thuis doelpunten'}]},
                     {'label': 'Uit doelpunten', 'method': 'update',
                      'args': [{'visible': [False, True]},
                              {'title': 'Uit doelpunten'}]}]
    
    
    df1 = top10[top10['Team'].isin(options)]
    
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df1['Team'],
                    y=df1['Doelpunten voor thuis'],
                    name='Thuis doelpunten',
                    marker_color='rgb(50,168,78)'
                    ))
    fig2.add_trace(go.Bar(x=df1['Team'],
                    y=df1['Doelpunten voor uit'],
                    name='Uit doelpunten',
                    marker_color='rgb(220,20,60)'
                    ))
    fig2.update_layout(
        {'updatemenus':[{
            'type': 'dropdown', 
            'x': 1.3, 
            'y': 0.5, 
            'showactive': True, 
            'active': 0,
            'buttons': dropdown_buttons}]},
        title='Doelpunten per team',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Gescoorde doelpunten over gehele seizoen'))
    st.plotly_chart(fig2)   
    
    
    
    fig2 = px.histogram(df1, x= "Team", y="Average age team", color = "Team", title='Gemiddeld leeftijd per team',
                       labels={'Team':'Elftallen', 'Average age team':'Gemiddelde leeftijd'})
    fig2.update_layout(yaxis_range=[20,30], showlegend=False)
    st.plotly_chart(fig2)

    dropdown_buttons = [{'label': 'Totaal toeschouwers met percentage', 'method': 'update',
                          'args': [{'visible': [True, True]},
                                  {'title': 'Totaal toeschouwers met percentage'}]},
                        {'label': 'Totaal aantal toeschouwers', 'method': 'update', 
                         'args': [{'visible': [True, False]},
                                  {'title': 'Totaal aantal toeschouwers'}]},
                         {'label': 'Percentage toeschouwers', 'method': 'update',
                          'args': [{'visible': [False, True]},
                                  {'title': 'Percentage toeschouwers'}]}]
    
    Toeschouwers = Toeschouwers1[Toeschouwers1['Team'].isin(options)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=Toeschouwers['Team'],
                    y=Toeschouwers['Totaal'],
                    name='Totaal toeschouwers',
                    marker_color='rgb(0,0,128)'
                    ))
    fig.add_trace(go.Bar(x=Toeschouwers['Team'],
                    y=Toeschouwers['Percentage'],
                    name='Percentage stadion gevuld',
                    marker_color='rgb(255,20,147)'
                    ))

    fig.update_layout(
        {'updatemenus':[{
            'type': 'dropdown', 
            'x': 1.5, 
            'y': 0.5, 
            'showactive': True, 
            'active': 0,
            'buttons': dropdown_buttons}]},
        title='Totaal aantal toeschouwers met percentage over geheel seizoen',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Aantal toeschouwers (%)'),
        xaxis=dict(
            title='Elftallen'))
    st.plotly_chart(fig)








    st.header('Locatie van de stadions en het gemiddelde aantal doelpunten per wedstrijd')
    st.markdown('Dit aantal is van de thuisploeg en de uitploeg samen')

    map_stadion = folium.Map(location=[52.584797 , -2.238721], tiles="OpenStreetMap", zoom_start=7)

    for i in range(0,len(df1)):
       folium.Marker(
          location=[df1.iloc[i]['lat'], df1.iloc[i]['long']],
          popup=df1.iloc[i]['Team'],
       ).add_to(map_stadion)

    for i in range(0,len(df1)): 
        folium.CircleMarker(
        radius=df1.iloc[i]['Average Goals Stadium']*5,
        location=[df1.iloc[i]['lat'], df1.iloc[i]['long']],
        popup=df1.iloc[i]['Average Goals Stadium'],
        color="red",
        fill= True,
    ).add_to(map_stadion)
    st_data = st_folium(map_stadion, height=950, width=700)
    
   
    
    

def page_three():
    dropdown_buttons = [{'label': 'Gele en rode kaarten', 'method': 'update',
                      'args': [{'visible': [True, True]},
                              {'title': 'Gemiddeld aantal kaarten per scheidsrechter'}]},
                    {'label': 'Gele kaarten', 'method': 'update', 
                     'args': [{'visible': [True, False]},
                              {'title': 'Gemiddeld aantal kaarten per scheidsrechter'}]},
                     {'label': 'Rode kaarten', 'method': 'update',
                      'args': [{'visible': [False, True]},
                              {'title': 'Gemiddeld aantal kaarten per scheidsrechter'}]}
                    
                   ]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_ref_info['referee'],
                    y=df_ref_info['yellow per game'],
                    name='Gele kaarten',
                    marker_color='rgb(255,255,102)'
                    ))
    fig.add_trace(go.Bar(x=df_ref_info['referee'],
                    y=df_ref_info['red per game'],
                    name='Rode kaarten',
                    marker_color='rgb(220,20,60)'
                    ))
    fig.update_layout(
        {'updatemenus':[{
            'type': 'dropdown', 
            'x': 1.3, 
            'y': 0.5, 
            'showactive': True, 
            'active': 0,
            'buttons': dropdown_buttons}]},
        title='Gemiddeld aantal kaarten per scheidsrechter',
        xaxis_tickfont_size=14,
        yaxis=dict(
        title='Aantal kaarten (per wedstrijd)'))
    
    st.plotly_chart(fig)
    
    
    fig = px.bar(team_kaarten, x='team', y= ['gele kaarten', 'rode kaarten'])


    dropdown_buttons2 = [{'label': 'gele en rode kaarten', 'method': 'update',
                          'args': [{'visible': [True, True]},
                                  {'title': 'totaal aantal gele en rode kaarten'}]},
                        {'label': 'gele kaarten', 'method': 'update', 
                         'args': [{'visible': [True, False]},
                                  {'title': 'totaal aantal gele kaarten'}]},
                         {'label': 'rode kaarten', 'method': 'update',
                          'args': [{'visible': [False, True]},
                                  {'title': 'totaal aantal rode kaarten'}]}]


    fig = go.Figure()
    fig.add_trace(go.Bar(x=team_kaarten['team'],
                    y=team_kaarten['gele kaarten'],
                    name='gele kaarten',
                    marker_color='rgb(255,255,102)'
                    ))
    fig.add_trace(go.Bar(x=team_kaarten['team'],
                    y=team_kaarten['rode kaarten'],
                    name='rode kaarten',
                    marker_color='rgb(220,20,60)'
                    ))


    fig.update_layout(
        {'updatemenus':[{
            'type': 'dropdown', 
            'x': 1.3, 
            'y': 0.5, 
            'showactive': True, 
            'active': 0,
            'buttons': dropdown_buttons2}]},
        title='Totaal gele en rode kaarten (per team)',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Aantal kaarten'))


    st.plotly_chart(fig)
    
    fig = px.bar(team_kaarten, x='team', y= ['gele kaarten', 'rode kaarten'])


    dropdown_buttons2 = [{'label': 'gele en rode kaarten', 'method': 'update',
                          'args': [{'visible': [True, True]},
                                  {'title': 'totaal aantal gele en rode kaarten'}]},
                        {'label': 'gele kaarten', 'method': 'update', 
                         'args': [{'visible': [True, False]},
                                  {'title': 'totaal aantal gele kaarten'}]},
                         {'label': 'rode kaarten', 'method': 'update',
                          'args': [{'visible': [False, True]},
                                  {'title': 'totaal aantal rode kaarten'}]}]


    fig = go.Figure()
    fig.add_trace(go.Bar(x=team_kaarten['team'],
                    y=team_kaarten['geel'],
                    name='gele kaarten',
                    marker_color='rgb(255,255,102)'
                    ))
    fig.add_trace(go.Bar(x=team_kaarten['team'],
                    y=team_kaarten['rood'],
                    name='rode kaarten',
                    marker_color='rgb(220,20,60)'
                    ))


    fig.update_layout(
        {'updatemenus':[{
            'type': 'dropdown', 
            'x': 1.3, 
            'y': 0.5, 
            'showactive': True, 
            'active': 0,
            'buttons': dropdown_buttons2}]},
        title='Saldo gele en rode kaarten (per team)',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Verhoudig kaarten'))


    st.plotly_chart(fig)





def page_four():
    
    links = st.selectbox('Wat wilt u zien aan de Linkerkant?',
                          ('Minuten gespeeld', 'Aantal gespeeld', 'Doelpunten', 'Assists','clean sheets', 
                           'tegendoelpunten per 90 min', 'Doelpunten betrokken', 'Gele kaarten', 'Rode kaarten', 'minuten per kaart'))
    rechts = st.selectbox('Wat wilt u zien aan de Rechterkant?',
                          ('Minuten gespeeld', 'Aantal gespeeld', 'Doelpunten', 'Assists','clean sheets', 
                           'tegendoelpunten per 90 min', 'Doelpunten betrokken', 'Gele kaarten', 'Rode kaarten', 'minuten per kaart'))
    
    def ranglijst(data, kolom1, kolom2):
        qw = pd.DataFrame({'Ranglijst' : list(range(1,11))}) 
        qe = pd.DataFrame({" ": " | ", 'Ranglijst' : list(range(1,11))})    
        def top10(kolom):
            df3 = data.sort_values([kolom], ascending=False)
            df2 = df3[['Naam', 'Leeftijd', 'Positie', kolom]].iloc[:10,:]
            df = df2.reset_index()
            df = df.drop(['index'], axis=1)
            return df
    
        eerste = qw.join(top10(kolom1))
        tweede  = qe.join(top10(kolom2))
        return_df = pd.merge(eerste,tweede, left_index=True, right_index=True, how='outer')
        #return_df = return_df.rename({'Ranglijst_x': 'Ranglijst', 'Naam_x': 'Naam',
        #                              'Leeftijd_x': 'Leeftijd', 'Positie_x': 'Positie',
        #                             'Ranglijst_y': 'Ranglijst', 'Naam_y': 'Naam',
        #                              'Leeftijd_y': 'Leeftijd', 'Positie_y': 'Positie'}, axis='columns')
        return return_df
    
    st.markdown('Spelers zijn alleen meegenomen in deze lijsten als zij meer dan 90 minuten gespeeld hebben over het gehele seizoen')
    lijst = ranglijst(lijstjes, links, rechts)    
    st.table(lijst)
    
    
    fig = px.scatter(spelers, x="goals_overall", y="assists_overall", color="position", opacity = 0.5,
                 color_discrete_sequence=["green", "orange", "red", "blue"],
                 size = 'minutes_played_overall', hover_data=['full_name', 'Current Club'], title="Top teams: spelers doelpunten & assists",
                labels={
                     "goals_overall": "Totaal aantal doelpunten",
                     "assists_overall": "Totaal aantal assists",
                     "position": "Positie"})
    st.plotly_chart(fig)
    
    
    
    
    countries = gpd.read_file('countries.geojson')
    nieuw = ['Republic of Ireland', "Côte d'Ivoire",'Serbia']
    oud = ['Ireland', 'Ivory Coast', 'Republic of Serbia']
    countries['ADMIN'] = countries['ADMIN'].replace(oud, nieuw)
    
    st.header('Afkomst van de spelers')
    
    map_spelers = folium.Map(location=[30,0], zoom_start=2,tiles="OpenStreetMap", zoom_control=True)

    folium.Choropleth(
        geo_data=countries,
        name="choropleth",
        data=landen_plotje,
        columns=["nationality", "eenheid"],
        key_on="feature.properties.ADMIN",
        fill_color="Greens",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Polio",
    ).add_to(map_spelers)

    st_data = st_folium(map_spelers, height=650, width=950)
    
    UK = ['England', 'Wales', 'Scotland', 'Northern Ireland']
    VK1 = landen_plot[landen_plot['nationality'].isin(UK)]
    VK = VK1[['nationality', 'eenheid']]

    st.markdown('Spelers uit het Verenigd Koningrijk')
    st.table(VK)

def page_five():
    st.title('Wat als het seizoen langer had geduurd?')
    
    
    fig = px.line(voorspelling, x='speelronde', y=elftallen, labels={
                     "value": "Aantal punten",
                     "Wedstrijd": "Speelronde",
                     "variable": "Clubs"
                 }, title='Puntenverloop voorspelling')
    fig.add_vline(x = 38)
    st.plotly_chart(fig)
    
    
    
#side-bar + data selection
st.sidebar.write("""# Selectie menu⚙️""")
options = st.sidebar.radio('Bladzijdes📂', options=['Intro', 'Algemeen', 'Teams', 'Scheidsrechters', 'Spelers', 'Model'])

if options == 'Intro':
    page_intro()

elif options == 'Algemeen':
    page_one()    
    
elif options == 'Teams':
    page_two()
    
elif options == 'Scheidsrechters':
    page_three()
    
elif options == 'Spelers':
    page_four()

elif options == 'Model':
    page_five()
