import dash_bootstrap_components as dbc
from dash import html, dcc

def create_quiz_interface(questions):
    question_elements = []
    
    for i, question in enumerate(questions):
        options = []
        for j, option in enumerate(question['options']):
            options.append(
                dbc.RadioButton(
                    label=option,
                    value=option,
                    id={'type': 'question-answer', 'index': i},
                    className='mb-2'
                )
            )
        
        question_elements.append(
            dbc.Card([
                dbc.CardHeader(f"Question {i+1}"),
                dbc.CardBody([
                    html.H5(question['question'], className="card-title"),
                    dbc.RadioItems(
                        options=[{'label': opt, 'value': opt} for opt in question['options']],
                        value=None,
                        id={'type': 'question-answer', 'index': i},
                        className='mb-3'
                    )
                ])
            ], className='mb-4')
        )
    
    return html.Div([
        html.H3("Generated Quiz", className="mb-4"),
        *question_elements,
        dbc.Button(
            "Submit Quiz",
            id='submit-quiz',
            color='success',
            className='w-100 mb-4'
        ),
        html.Div(id='quiz-results')
    ])
