import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row(
            dbc.Col(
                html.A(
                    html.Img(
                        src="assets/dbdp-white-logo.png",
                        className="nav-image",
                    ),
                    href="https://dbdp.org/",
                    target="_blank"))),

        # TODO change pill color once a color is settled
        dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [html.I(className="bi bi-github home-icons"), "GitHub"],
                        className="icons-button",
                        size="sm",
                        href="https://github.com/DigitalBiomarkerDiscoveryPipeline",
                        target="_blank"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-twitter home-icons"), "DBDP ED"],
                        className="icons-button",
                        size="sm",
                        href="https://medium.com/digital-biomarker-discovery",
                        target="_blank"
                    ),
                    dbc.Button(
                        [html.I(className="bi bi-twitter home-icons"),
                         "Open DBDP"],
                        className="icons-button",
                        size="sm",
                        href="https://dbdp.org/opendbdp",
                        target="_blank"
                    ),
                ])
                ]),
    ],
        fluid=True
    ),
    color="primary"
)

# Sidebar
sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2"),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light",
)

app.layout = dbc.Container([
    navbar,
    html.Br(),

    # Sidebar and Pages
    dbc.Row([
        dbc.Col([
            sidebar
        ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
        dbc.Col([
            dash.page_container
        ],  xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
    ]),

    # Store user uploaded data
    dcc.Store(id='data-store', storage_type='local'),
    dcc.Store(id='filename', storage_type='local'),

    # Data store to hold updated data
    dcc.Store(id='cleaned-data-store', storage_type='local'),
], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True)
