import dash_bootstrap_components as dbc
from dash import html

def create_header():
    return dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(html.I(className="bi bi-youtube me-2"), width="auto"),
                    dbc.Col(dbc.NavbarBrand("YouTube Quiz Generator", className="ms-2")),
                ], align="center", className="g-0"),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("History", href="/history")),
                    dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
                    dbc.NavItem(dbc.NavLink("Logout", href="/logout", id="logout-button")),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4",
    )
