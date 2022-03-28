import pandas as pd 
import numpy as np 
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go 


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

])
   
   
#Callback for MacroScore, Macroeconomic Z-Scores
@app.callback(
    Output(component_id='CoinData', component_property='figure'),
    [Input(component_id='CoinScores', component_property= 'value')]
)
def updateGraph(input_value):
    token = input_value
    path = 'Json_Data/'

    #DATA - USD Price, BTC PRice, Volume, Market Cap
    name = token + "_data.json"
    myFile = path + name
    #print(myFile)
    data = pd.read_json(myFile)

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
    usd = pd.DataFrame(usd)#.round(2)
    vol = pd.DataFrame(vol)#.round(0).astype(int)
    mkcap = pd.DataFrame(mkcap)#.round(0).astype(int)

    result = pd.concat([date, btc, usd, vol, mkcap], axis=1)#, join='inner')
    result.columns = ['Date', 'BTC', 'USD', 'VOL', 'MarketCap']
    result = result.set_index('Date')

    #RANKING
    name = token + "_rank.json"
    myFile = path + name
    data = pd.read_json(myFile)

    #FOR RANKING
    data = pd.json_normalize(data['data']).replace(to_replace="null", value=np.NaN).dropna().ffill().sort_values('x')
    rank = pd.DataFrame(data).rename(columns= {'x': 'Date', 'y': 'Rank'}).set_index('Date')
    # !!!!! OLD WAY UNSURE WHAT IS BEST !!!!!
    #data = pd.json_normalize(data['data']).replace(to_replace="null", value=np.NaN).sort_values('x')
    #rank = pd.DataFrame(data).rename(columns= {'x': 'Date', 'y': 'Rank'}).set_index('Date').replace(to_replace="null", value=np.NaN).ffill()#.bfill()#.bfill()
    rank.index = pd.to_datetime(rank.index).date
    merged = pd.concat([result, rank], axis=1, join='inner').ffill()#, join='inner')

    if token == 'bitcoin':
        default_transp = 0
    else:
        default_transp = 1


    ##### Create traces ######
    GRAPH_HEIGHT = 750
    fig = go.Figure()
    #config = dict({'scrollZoom': True})
    fig.add_trace(go.Scatter(x=merged.index, y=merged.Rank,
                        mode='lines',
                        name= 'Ranking',
                        line=dict(color='white'),
                        opacity=default_transp))
    fig.add_trace(go.Scatter(x=merged.index, y=merged.USD,
                        mode='lines',
                        name= 'USD Price',
                        line=dict(color='#39E126'),
                        yaxis="y2"))
    fig.add_trace(go.Scatter(x=merged.index, y=merged.BTC,
                        mode='lines',
                        name= 'BTC Price',
                        yaxis="y3",
                        line=dict(color='orange'),
                        opacity=default_transp))
    fig.add_trace(go.Bar(x=merged.index, y=merged.VOL,
                        name= 'Volume',
                        yaxis="y4",
                        opacity=.4))  
    fig.add_trace(go.Scatter(x=merged.index, y=merged.MarketCap,
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
            hoverformat="$.2f",
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
            zeroline=False
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

