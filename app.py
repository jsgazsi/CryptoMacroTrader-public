import pandas as pd 
import numpy as np 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go 
import functions

import datetime as dt 

#MacroTraderFX Dashboard
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True
server = app.server
app.title = 'Crypto MacroTrader'

#Coin List for DropDown
CoinList = pd.read_csv("CoinList.csv")


app.layout = html.Div([ 

    #Header
    html.H1(
    children='Crypto MacroTrader',
    style={
        'font-size': '150%',
        'textAlign': 'center',
        'color': '#010057'}
    ),

    #Header
    #html.H1(
    #children='Rankinator',
    #style={
    #    'font-size': '175%',
    #    'textAlign': 'center',
    #    'color': '#7FDBFF'}
    #),

    #General Macro Z-Score Section
    html.Label('Cryptocurrency'),
    dcc.Dropdown(id='CoinScores', style={'width': '100%'},
        options=[
        {'label': i, 'value': j} for i, j in zip(CoinList.name + ' (' + CoinList.symbol + ')', CoinList.slug)
        ],
        value = 'bitcoin',
        #multi = True
    ),
    dcc.Graph(id='CoinData', config={'scrollZoom': True}),

    html.Div([html.Label("Daily Ranking Change Updates (Ctrl + click to follow link):")]),
    html.Div([dcc.Link(id="Rank Change Download", href="https://storage.googleapis.com/coin_data_bucket/rank_change.csv")]),
    html.Div([html.Label("View more info about coin at:")]),
    html.Div([html.A(id='CMC_Link')]),
    html.Div([html.A(id='Messario_Link')])
    
])
   

@app.callback(
    Output(component_id='CMC_Link', component_property='children'),
    [Input(component_id='CoinScores', component_property='value')]
)
def updateLink(input_value):
    value = 'https://coinmarketcap.com/currencies/' + str(input_value)
    return value

@app.callback(
    Output(component_id='Messario_Link', component_property='children'),
    [Input(component_id='CoinScores', component_property='value')]
)
def updateLink2(input_value):
    value = 'https://messari.io/asset/' + str(input_value)
    return value

#Callback for MacroScore, Macroeconomic Z-Scores
@app.callback(
    Output(component_id='CoinData', component_property='figure'),
    [Input(component_id='CoinScores', component_property= 'value')]
)
def updateGraph(input_value):
    token = input_value
    today = dt.datetime.today().strftime('%Y-%m-%d')
    date_range = pd.date_range("01-01-2015", today)
    idx = pd.DatetimeIndex(date_range)

    #DATA - USD Price, BTC PRice, Volume, Market Cap
    name = token + "_data.json"
    data = functions.getJson(name)


    #!!!!THIS IS SOMETHING
    data = pd.DataFrame(data.data)[6:]
    data.index = pd.to_datetime(data.index).date
    date = pd.DataFrame(data.index)

    btc = []
    usd = []
    vol = []
    mkcap = []
    for value in data.values:
        btc.append(value[0]['BTC'][0])
        usd.append(value[0]['USD'][0])
        vol.append(value[0]['USD'][1])
        mkcap.append(value[0]['USD'][2])
        

    btc = pd.DataFrame(btc)
    usd = pd.DataFrame(usd)
    vol = pd.DataFrame(vol)
    mkcap = pd.DataFrame(mkcap)

    market_data = pd.concat([date, btc, usd, vol, mkcap], axis=1)#, join='inner')
    market_data.columns = ['Date', 'BTC', 'USD', 'VOL', 'MarketCap']
    market_data = market_data.set_index('Date')
    market_data.index = pd.to_datetime(market_data.index).date
    market_data = market_data.reindex(idx)
    market_data.interpolate(inplace=True)
    market_data.dropna(inplace=True)

    #RANKING
    name = token + "_rank.json"
    data = functions.getJson(name)

    #FOR RANKING
    data = pd.json_normalize(data['data']).replace(to_replace="null", value=np.NaN).dropna().ffill().sort_values('x')
    rank_data = pd.DataFrame(data).rename(columns= {'x': 'Date', 'y': 'Rank'}).set_index('Date')
    rank_data.index = pd.to_datetime(rank_data.index).date
    rank_data = rank_data.reindex(idx)
    rank_data.interpolate('pad',inplace=True)
    rank_data.dropna(inplace=True)
 

    if token == 'bitcoin':
        default_transp = 0
    else:
        default_transp = 1


    ##### Create traces ######
    GRAPH_HEIGHT = 625
    fig = go.Figure()
    #config = dict({'scrollZoom': True})
    fig.add_trace(go.Scatter(x=rank_data.index, y=rank_data.Rank,
                        mode='lines',
                        name= 'Ranking',
                        line=dict(color='white'),
                        opacity=default_transp))
    fig.add_trace(go.Scatter(x=market_data.index, y=market_data.USD,
                        mode='lines',
                        name= 'USD Price',
                        line=dict(color='#39E126'),
                        yaxis="y2"))
    fig.add_trace(go.Scatter(x=market_data.index, y=market_data.BTC,
                        mode='lines',
                        name= 'BTC Price',
                        yaxis="y3",
                        line=dict(color='orange'),
                        opacity=default_transp))
    fig.add_trace(go.Bar(x=market_data.index, y=market_data.VOL,
                        name= 'Volume',
                        yaxis="y4",
                        #marker_color=dict(color='#E114D7'),
                        marker_color='#9CB9FF',
                        opacity=.4))  
    fig.add_trace(go.Scatter(x=market_data.index, y=market_data.MarketCap,
                        mode='lines',
                        name= 'MarketCap',
                        line=dict(color='blue'),
                        yaxis="y5",
                        opacity=0)) 

    fig.update_layout(
        height=GRAPH_HEIGHT,
        dragmode='pan',
        yaxis= dict(
            fixedrange=True, 
            autorange= "reversed",
            showgrid=True,
            side="right",
            zeroline=False,
            title="Rank",
        ),
        yaxis2=dict(
            title="USD Price",
            overlaying="y",
            side="left",
            fixedrange=True,
            showgrid=False,
            tickprefix="$",
            hoverformat=".2f",
            zeroline=False,
            #gridcolor="#014208",
            ticks="inside",
        ),
        yaxis3=dict(
            #title="BTC Price",
            overlaying="y",
            fixedrange=True,
            showgrid=False,
            showticklabels=False,
            hoverformat=".8f",
            zeroline=False,
        ),
            yaxis4=dict(
            #title="Volume",
            overlaying="y",
            position=0,
            fixedrange=True,
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
            yaxis5=dict(
            #title="Market Cap",        
            overlaying="y",
            fixedrange=True,
            showgrid=False,
            showticklabels=False,
            zeroline=False  
        ),
    )

    fig.update_layout(
        title_text= token, template="plotly_dark", hovermode='x unified'#plot_bgcolor='black',
    )
    
    return fig

    



#RUN PROGRAM
if __name__ == '__main__':
    app.run_server(debug=True)

