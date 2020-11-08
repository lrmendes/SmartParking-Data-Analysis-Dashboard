import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from apps import basic1, basic2, home

PLOTLY_LOGO = "http://192.168.1.30:2424/assets/iconNew.png"

nav_item = dbc.NavItem(dbc.NavLink("Home", href="/"))

# make a reuseable dropdown for the different examples
dropdown1 = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Daily Parkings", href="/basic/graph1"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Total Parkings", href="/basic/graph2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Grafico 3", href="/basic/graph3"),
    ],
    nav=True,
    in_navbar=True,
    label="Basic Analysis",
)

# make a reuseable dropdown for the different examples
dropdown2 = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Grafico 1", href="/advanced/graph1"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Grafico 2", href="/advanced/graph2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Grafico 3", href="/advanced/graph3"),
    ],
    nav=True,
    in_navbar=True,
    label="Advanced Analysis",
)

dropdown3 = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Grafico 1"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Grafico 2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Grafico 3"),
    ],
    nav=True,
    in_navbar=True,
    label="Predictive Analysis (ML)",
)

# custom navbar based on https://getbootstrap.com/docs/4.1/examples/dashboard/
dashboard = dbc.Navbar(
    [
        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px"),sm=1, md=1),
        dbc.Col(dbc.NavbarBrand("Parking Analytics", href="#"), sm=3, md=2),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav(
                [nav_item, dropdown1, dropdown2, dropdown3], className="ml-auto", navbar=True
            ),
            id="navbar-collapse",
            navbar=True,
        ),
        #dbc.Col(
        #    dbc.Nav(dbc.NavItem(dbc.NavLink("Sign out")), navbar=True),
        #    width="auto",
        #),
    ],
    color="#6900af",
    dark=True,
    className="mb-5"
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dashboard,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/basic/graph1':
        return basic1.layout
    elif pathname == '/basic/graph2':
        return basic2.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=True, host='192.168.1.30', port=2424)