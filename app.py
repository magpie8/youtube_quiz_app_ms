import os
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from youtube_transcript_api import YouTubeTranscriptApi
from services.auth_service import AuthService
from services.youtube_service import YouTubeService
from services.quiz_service import QuizService
from components.header import create_header
from components.sidebar import create_sidebar
from components.quiz_components import create_quiz_interface
from utils.logger import setup_logger
from config import Config

# Initialize the app
app = Dash(__name__, 
           external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP],
           suppress_callback_exceptions=True,
           meta_tags=[{'name': 'viewport', 
                      'content': 'width=device-width, initial-scale=1.0'}])

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app.server)
login_manager.login_view = '/login'

# MongoDB setup
db_client = MongoClient(Config.MONGO_URI)
db = db_client[Config.MONGO_DB_NAME]

# Services initialization
auth_service = AuthService(db)
youtube_service = YouTubeService(Config.YOUTUBE_API_KEY)
quiz_service = QuizService(Config.DEEPSEEK_API_KEY)

# Logger setup
logger = setup_logger()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({'_id': user_id})
    if not user_data:
        return None
    return User(user_data)

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='transcript-store'),
    dcc.Store(id='quiz-data-store'),
    dcc.Store(id='user-answers-store'),
    dcc.Store(id='video-info-store'),
    
    # Main content will be rendered here
    html.Div(id='page-content'),
    
    # Feedback modal (hidden by default)
    dbc.Modal([
        dbc.ModalHeader("Submit Feedback"),
        dbc.ModalBody([
            dbc.Textarea(id='feedback-text', placeholder="Your feedback...", rows=5),
            dbc.Select(
                id='feedback-type',
                options=[
                    {'label': 'Bug Report', 'value': 'bug'},
                    {'label': 'Feature Request', 'value': 'feature'},
                    {'label': 'General Feedback', 'value': 'general'},
                ],
                value='general'
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("Submit", id="submit-feedback", color="primary"),
            dbc.Button("Close", id="close-feedback", color="secondary")
        ])
    ], id="feedback-modal", is_open=False),
    
    # Floating feedback button
    html.Div(
        dbc.Button(
            html.I(className="bi bi-chat-square-text"),
            id="open-feedback",
            color="primary",
            className="position-fixed",
            style={'bottom': '20px', 'right': '20px', 'zIndex': '1000', 'borderRadius': '50%'}
        )
    )
])

# Authentication pages
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Login", className="text-center mb-4"),
            dbc.Card([
                dbc.CardBody([
                    dcc.Input(id='login-username', type='text', placeholder='Username', className='form-control mb-3'),
                    dcc.Input(id='login-password', type='password', placeholder='Password', className='form-control mb-3'),
                    dbc.Button("Login", id='login-button', color='primary', className='w-100 mb-3'),
                    html.Div(id='login-message'),
                    html.Hr(),
                    html.P("Don't have an account?", className='text-center'),
                    dbc.Button("Register", id='go-to-register', color='secondary', className='w-100')
                ])
            ])
        ], md=6, className='mx-auto')
    ], className='mt-5')
])

register_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Register", className="text-center mb-4"),
            dbc.Card([
                dbc.CardBody([
                    dcc.Input(id='register-username', type='text', placeholder='Username', className='form-control mb-3'),
                    dcc.Input(id='register-email', type='email', placeholder='Email', className='form-control mb-3'),
                    dcc.Input(id='register-password', type='password', placeholder='Password', className='form-control mb-3'),
                    dcc.Input(id='register-confirm', type='password', placeholder='Confirm Password', className='form-control mb-3'),
                    dbc.Button("Register", id='register-button', color='primary', className='w-100 mb-3'),
                    html.Div(id='register-message'),
                    html.Hr(),
                    html.P("Already have an account?", className='text-center'),
                    dbc.Button("Login", id='go-to-login', color='secondary', className='w-100')
                ])
            ])
        ], md=6, className='mx-auto')
    ], className='mt-5')
])

# Main app layout
main_layout = html.Div([
    create_header(),
    dbc.Container([
        dbc.Row([
            dbc.Col(create_sidebar(), md=4, className='mb-4'),
            dbc.Col([
                dbc.Spinner(html.Div(id='main-content'), 
                html.Div(id='debug-panel', className='mt-4')
            ], md=8)
        ])
    ], fluid=True)
])

# Update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/login':
        return login_layout
    elif pathname == '/register':
        return register_layout
    elif pathname == '/logout':
        return html.Div("Logging out...")
    else:
        if current_user.is_authenticated:
            return main_layout
        else:
            return login_layout

# Authentication callbacks
@app.callback(
    Output('url', 'pathname'),
    Output('login-message', 'children'),
    Input('login-button', 'n_clicks'),
    State('login-username', 'value'),
    State('login-password', 'value')
)
def login(n_clicks, username, password):
    if n_clicks is None:
        return no_update, no_update
    
    if not username or not password:
        return no_update, dbc.Alert("Please enter both username and password", color="danger")
    
    result = auth_service.login_user(username, password)
    if result['success']:
        return '/', dbc.Alert("Login successful!", color="success")
    else:
        return no_update, dbc.Alert(result['message'], color="danger")

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('register-message', 'children'),
    Input('register-button', 'n_clicks'),
    State('register-username', 'value'),
    State('register-email', 'value'),
    State('register-password', 'value'),
    State('register-confirm', 'value'),
    prevent_initial_call=True
)
def register(n_clicks, username, email, password, confirm_password):
    if n_clicks is None:
        return no_update, no_update
    
    if not all([username, email, password, confirm_password]):
        return no_update, dbc.Alert("Please fill in all fields", color="danger")
    
    if password != confirm_password:
        return no_update, dbc.Alert("Passwords don't match", color="danger")
    
    result = auth_service.register_user(username, email, password)
    if result['success']:
        return '/login', dbc.Alert("Registration successful! Please login.", color="success")
    else:
        return no_update, dbc.Alert(result['message'], color="danger")

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('go-to-register', 'n_clicks'),
    prevent_initial_call=True
)
def go_to_register(n_clicks):
    if n_clicks:
        return '/register'
    return no_update

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('go-to-login', 'n_clicks'),
    prevent_initial_call=True
)
def go_to_login(n_clicks):
    if n_clicks:
        return '/login'
    return no_update

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        logout_user()
        return '/login'
    return no_update

# YouTube search and video processing
@app.callback(
    Output('video-results', 'children'),
    Input('search-button', 'n_clicks'),
    State('search-query', 'value'),
    prevent_initial_call=True
)
def search_videos(n_clicks, query):
    if not query:
        return dbc.Alert("Please enter a search term", color="warning")
    
    try:
        results = youtube_service.search_videos(query)
        if not results:
            return dbc.Alert("No videos found", color="warning")
        
        cards = []
        for video in results:
            card = dbc.Card([
                dbc.CardImg(src=video['thumbnail'], top=True),
                dbc.CardBody([
                    html.H5(video['title'], className="card-title"),
                    html.P(f"Duration: {video['duration']}", className="card-text"),
                    dbc.Button("Select", id={'type': 'select-video', 'index': video['id']}, 
                              color="primary", className="mt-2")
                ])
            ], className="mb-3")
            cards.append(card)
        
        return cards
    except Exception as e:
        logger.error(f"Error searching videos: {str(e)}")
        return dbc.Alert(f"Error searching videos: {str(e)}", color="danger")

@app.callback(
    Output('transcript-store', 'data'),
    Output('video-info-store', 'data'),
    Output('main-content', 'children'),
    Input({'type': 'select-video', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_video(n_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update, no_update
    
    video_id = ctx.triggered[0]['prop_id'].split('"index":')[1].split('}')[0].strip('"')
    
    try:
        # Get video info
        video_info = youtube_service.get_video_info(video_id)
        
        # Get transcript
        transcript = youtube_service.get_transcript(video_id)
        
        # Store transcript and video info
        transcript_data = {
            'video_id': video_id,
            'transcript': transcript,
            'timestamp': datetime.now().isoformat()
        }
        
        video_data = {
            'video_id': video_id,
            'title': video_info['title'],
            'thumbnail': video_info['thumbnail'],
            'duration': video_info['duration']
        }
        
        # Create transcript preview
        transcript_preview = html.Div([
            html.H4(f"Transcript for: {video_info['title']}"),
            html.P(f"Duration: {video_info['duration']}"),
            dbc.Accordion([
                dbc.AccordionItem(
                    html.Pre('\n'.join([f"{t['text']}" for t in transcript[:20]])),
                    title="View Transcript (First 20 entries)"
                )
            ]),
            dbc.Button("Generate Quiz", id="generate-quiz", color="primary", className="mt-3")
        ])
        
        return transcript_data, video_data, transcript_preview
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return no_update, no_update, dbc.Alert(f"Error processing video: {str(e)}", color="danger")

# Quiz generation
@app.callback(
    Output('quiz-data-store', 'data'),
    Output('main-content', 'children', allow_duplicate=True),
    Input('generate-quiz', 'n_clicks'),
    State('transcript-store', 'data'),
    State('question-type', 'value'),
    State('question-count', 'value'),
    prevent_initial_call=True
)
def generate_quiz(n_clicks, transcript_data, question_type, question_count):
    if n_clicks is None:
        return no_update, no_update
    
    try:
        quiz = quiz_service.generate_quiz(
            transcript=transcript_data['transcript'],
            question_type=question_type,
            num_questions=question_count,
            video_id=transcript_data['video_id']
        )
        
        # Store quiz data
        quiz_data = {
            'quiz_id': str(datetime.now().timestamp()),
            'questions': quiz['questions'],
            'video_id': transcript_data['video_id'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Create quiz interface
        quiz_ui = create_quiz_interface(quiz['questions'])
        
        return quiz_data, quiz_ui
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return no_update, dbc.Alert(f"Error generating quiz: {str(e)}", color="danger")

# Quiz interaction
@app.callback(
    Output('quiz-results', 'children'),
    Output('user-answers-store', 'data'),
    Input('submit-quiz', 'n_clicks'),
    State('quiz-data-store', 'data'),
    State({'type': 'question-answer', 'index': ALL}, 'value'),
    State({'type': 'question-answer', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def submit_quiz(n_clicks, quiz_data, answers, answer_ids):
    if n_clicks is None:
        return no_update, no_update
    
    try:
        # Map answers to questions
        user_answers = {}
        for answer, answer_id in zip(answers, answer_ids):
            question_idx = answer_id['index']
            user_answers[question_idx] = answer
        
        # Calculate score
        score = 0
        results = []
        for idx, question in enumerate(quiz_data['questions']):
            is_correct = user_answers.get(idx) == question['correct_answer']
            if is_correct:
                score += 1
            
            results.append(
                dbc.AccordionItem([
                    html.P(f"Your answer: {user_answers.get(idx, 'No answer')}"),
                    html.P(f"Correct answer: {question['correct_answer']}"),
                    html.P(question['explanation'], className="text-muted")
                ], title=f"Question {idx+1}: {'✓' if is_correct else '✗'}")
            )
        
        # Save quiz results to database
        if current_user.is_authenticated:
            db.quiz_results.insert_one({
                'user_id': current_user.id,
                'quiz_id': quiz_data['quiz_id'],
                'video_id': quiz_data['video_id'],
                'score': score,
                'total': len(quiz_data['questions']),
                'timestamp': datetime.now().isoformat(),
                'user_answers': user_answers
            })
        
        # Create results display
        results_display = html.Div([
            html.H4(f"Quiz Results: {score}/{len(quiz_data['questions'])}"),
            dbc.Accordion(results),
            dbc.Alert(f"You scored {score} out of {len(quiz_data['questions'])}", 
                      color="success" if score/len(quiz_data['questions']) >= 0.7 else "warning")
        ])
        
        return results_display, user_answers
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        return dbc.Alert(f"Error submitting quiz: {str(e)}", color="danger"), no_update

# Feedback system
@app.callback(
    Output('feedback-modal', 'is_open'),
    Output('feedback-message', 'children'),
    Input('open-feedback', 'n_clicks'),
    Input('submit-feedback', 'n_clicks'),
    Input('close-feedback', 'n_clicks'),
    State('feedback-modal', 'is_open'),
    State('feedback-text', 'value'),
    State('feedback-type', 'value'),
    prevent_initial_call=True
)
def toggle_feedback(open_clicks, submit_clicks, close_clicks, is_open, feedback_text, feedback_type):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'open-feedback':
        return not is_open, no_update
    elif trigger_id == 'close-feedback':
        return False, no_update
    elif trigger_id == 'submit-feedback':
        if not feedback_text:
            return is_open, dbc.Alert("Please enter feedback text", color="danger")
        
        try:
            feedback_data = {
                'user_id': current_user.id if current_user.is_authenticated else None,
                'type': feedback_type,
                'text': feedback_text,
                'timestamp': datetime.now().isoformat(),
                'status': 'new'
            }
            
            db.feedback.insert_one(feedback_data)
            return False, dbc.Alert("Thank you for your feedback!", color="success")
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return is_open, dbc.Alert(f"Error submitting feedback: {str(e)}", color="danger")
    
    return no_update, no_update

# Debug panel
@app.callback(
    Output('debug-panel', 'children'),
    Input('debug-toggle', 'n_clicks'),
    State('debug-panel', 'children'),
    prevent_initial_call=True
)
def toggle_debug(n_clicks, current_children):
    if n_clicks is None:
        return no_update
    
    if current_children is None or current_children == []:
        return dbc.Card([
            dbc.CardHeader("Debug Information"),
            dbc.CardBody([
                html.Pre(id='debug-output')
            ])
        ])
    else:
        return []

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
