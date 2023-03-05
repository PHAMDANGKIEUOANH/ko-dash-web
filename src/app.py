"""
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_csv('intro_bees.csv')

df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)
print(df[:5])

app.layout = html.Div([
    html.H1("Web Application Dashboards with Dash", style={'test-align' : 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                    {"label": "2015", "value" : 2015},
                    {"label": "2016", "value" : 2016},
                    {"label": "2017", "value" : 2017},
                    {"label": "2018", "value" : 2018}],
                 multi=False,
                 value=2015,
                 style={'width': '40%'}
                ),
    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})
])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)

def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["Year"] == option_slctd]
    dff = dff[dff["Affected by"] == "Varroa_mites"]

    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='Pct of Colonies Impacted',
        hover_data=['State', 'Pct of Colonies Impacted'],
        color_continuous_scale=px.colors.sequential.Tealgrn,
        labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
        template='plotly_white'
    )

    return container, fig

if __name__ == '__main__':
    app.run_server(debug=True)

"""

import dash                     # pip install dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px     # pip install plotly==5.2.2

import pandas as pd             # pip install pandas
# Data: https://www.dallasopendata.com/Services/Animals-Inventory/qgg6-h4bd

df = pd.read_csv("Animals_Inventory.csv")
df["intake_time"] = pd.to_datetime(df["intake_time"])
df["intake_time"] = df["intake_time"].dt.hour
print(df.head())


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1("Analytics Dashboard of Dallas Animal Shelter (Dash Plotly)", style={"textAlign":"center"}),
    html.Hr(),
    html.P("Choose animal of interest:"),
    html.Div(html.Div([
        dcc.Dropdown(id='animal-type', clearable=False,
                     value="DOG",
                     options=[{'label': x, 'value': x} for x in
                              df["animal_type"].unique()]),
    ],className="two columns"),className="row"),

    html.Div(id="output-div", children=[]),
])


@app.callback(Output(component_id="output-div", component_property="children"),
              Input(component_id="animal-type", component_property="value"),
)
def make_graphs(animal_chosen):
    # HISTOGRAM
    df_hist = df[df["animal_type"]==animal_chosen]
    fig_hist = px.histogram(df_hist, x="animal_breed")
    fig_hist.update_xaxes(categoryorder="total descending")

    # STRIP CHART
    fig_strip = px.strip(df_hist, x="animal_stay_days", y="intake_type")

    # SUNBURST
    df_sburst = df.dropna(subset=['chip_status'])
    df_sburst = df_sburst[df_sburst["intake_type"].isin(["STRAY", "FOSTER", "OWNER SURRENDER"])]
    fig_sunburst = px.sunburst(df_sburst, path=["animal_type", "intake_type", "chip_status"])

    # Empirical Cumulative Distribution
    df_ecdf = df[df["animal_type"].isin(["DOG","CAT"])]
    fig_ecdf = px.ecdf(df_ecdf, x="animal_stay_days", color="animal_type")

    # LINE CHART
    df_line = df.sort_values(by=["intake_time"], ascending=True)
    df_line = df_line.groupby(
        ["intake_time", "animal_type"]).size().reset_index(name="count")
    fig_line = px.line(df_line, x="intake_time", y="count",
                       color="animal_type", markers=True)

    return [
        html.Div([
            html.Div([dcc.Graph(figure=fig_hist)], className="six columns"),
            html.Div([dcc.Graph(figure=fig_strip)], className="six columns"),
        ], className="row"),
        html.H2("All Animals", style={"textAlign":"center"}),
        html.Hr(),
        html.Div([
            html.Div([dcc.Graph(figure=fig_sunburst)], className="six columns"),
            html.Div([dcc.Graph(figure=fig_ecdf)], className="six columns"),
        ], className="row"),
        html.Div([
            html.Div([dcc.Graph(figure=fig_line)], className="twelve columns"),
        ], className="row"),
    ]


if __name__ == '__main__':
    app.run_server(debug=True)