from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
not_year_options = [col for col in numeric_columns if col != 'year']
# external CSS stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dbc.Row([
        dbc.Col([html.H4(children='Выберите страну', style={'textAlign':'center'}),
                dcc.Dropdown(options=[{'label': country, 'value': country} for country in df.country.unique()], value=['Canada'], id='dropdown-selection', multi=True)]),
        dbc.Col([html.H4(children='Выберите метрику', style={'textAlign':'center'}),
                dcc.Dropdown(options=[{'label': col, 'value': col} for col in numeric_columns], value='pop', id='dropdown-y-selection')])
    ]),
    dbc.Col([html.H4(children='Линейный график', style={'textAlign':'center'}),
            dcc.Graph(id='graph-content')]),
    dbc.Row([
        dbc.Col([html.H4(children='Выберите метрику X', style={'textAlign':'center'}),
                dcc.Dropdown(options=[{'label': col, 'value': col} for col in not_year_options], value='pop', id='scatter-x')]),
        dbc.Col([html.H4(children='Выберите метрику Y', style={'textAlign':'center'}),
                dcc.Dropdown(options=[{'label': col, 'value': col} for col in not_year_options], value='pop', id='scatter-y')]),
        dbc.Col([html.H4(children='Выберите год', style={'textAlign':'center'}),
                dcc.Dropdown(options=[{'label': year, 'value': year} for year in df.year.unique()], value=df.year[0], id='year-selector')])
    ]),
    dbc.Col([
        dbc.Col([dbc.Col([html.H4(children='Выберите метрику, отвечающую за размер пузырьков', style={'textAlign':'center'}),
                          dcc.Dropdown(options=[{'label': col, 'value': col} for col in not_year_options], value='pop', id='size-selector'),
                          dcc.Graph(id='bubble-graph')])
        ]),
        dbc.Row([dbc.Col(dcc.Graph(id='top15-graph'), width=8),
                 dbc.Col(dcc.Graph(id='continent-pop-graph'), width=4)])
    ]),
])

@callback(
    Output('bubble-graph', 'figure'),
    Input('scatter-x', 'value'),
    Input('scatter-y', 'value'),
    Input('year-selector', 'value'),
    Input('size-selector', 'value')
)
def update_bubble(x,y,year, size):
    dff=df[df.year==year]
    return px.scatter(dff,
                      x=x,
                      y=y,
                      size=size,
                      hover_name='country',
                      title=f'Пузырковая диаграмма для {year} года',
                      labels={x: x, y: y})

@callback(
    Output('top15-graph', 'figure'),
    Input('year-selector', 'value')
)
def update_top15(year):
    dff=df[df.year==year]
    dff=dff.nlargest(15, 'pop')[['country', 'pop']]
    dff=dff[-1::-1]
    return px.bar(dff, 
                  y='country', 
                  x='pop', 
                  title=f'Tоп 15 стран по населению в {year}', 
                  labels={'pop': 'Население', 'country': 'Страна'})

@callback(
    Output('continent-pop-graph', 'figure'),
    Input('year-selector', 'value')
)
def update_pie(year):
    dff=df[df.year==year]
    dff = dff.groupby('continent')['pop'].sum().reset_index()
    return px.pie(dff, 
                  values='pop', 
                  names='continent', 
                  title=f'Население по континентам в {year}', 
                  labels={'pop': 'Население', 'continent': 'Континент'})

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dropdown-y-selection', 'value')
)
def update_graph(value, value2):
    dff = df[df.country.isin(value)]
    return px.line(dff, x='year', y=value2, color='country')

if __name__ == '__main__':
    app.run(debug=True)
