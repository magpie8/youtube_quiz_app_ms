import dash_bootstrap_components as dbc
from dash import html, dcc

def create_sidebar():
    return dbc.Card([
        dbc.CardHeader("Video Search", className="h5"),
        dbc.CardBody([
            dcc.Input(
                id='search-query',
                type='text',
                placeholder='Enter search term or YouTube URL',
                className='form-control mb-3'
            ),
            dbc.Button(
                "Search Videos",
                id='search-button',
                color='primary',
                className='w-100 mb-3'
            ),
            html.Div(id='video-results'),
            
            html.Hr(),
            
            html.H5("Quiz Options", className="mt-3"),
            dbc.Select(
                id='question-type',
                options=[
                    {'label': 'Multiple Choice', 'value': 'multiple_choice'},
                    {'label': 'True/False', 'value': 'true_false'},
                    {'label': 'Short Answer', 'value': 'short_answer'},
                ],
                value='multiple_choice',
                className='mb-3'
            ),
            dbc.Input(
                id='question-count',
                type='number',
                min=1,
                max=20,
                value=5,
                className='mb-3'
            ),
            
            html.Hr(),
            
            dbc.Button(
                "Toggle Debug Panel",
                id='debug-toggle',
                color='secondary',
                outline=True,
                className='w-100'
            )
        ])
    ])
