import flask
import firebase_admin
import os
import uuid
import hashlib
import logging
import re
import random
import threading
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime, timedelta
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core import exceptions
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from openai import OpenAI
from dotenv import load_dotenv
from model_predictor import load_models, get_full_prediction
from flask_talisman import Talisman

# Load .env file from the Flask app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(APP_DIR, '.env')
load_dotenv(ENV_PATH, override=True)

app = flask.Flask(__name__)

#########################==================== SECURITY CONFIGURATION ====================#########################
# Use environment variable for secret key
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32).hex())
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = '/tmp'  # Use temp folder for uploads
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Keep session alive for each request

# Disable HTTPS enforcement for development
force_https = os.getenv('FORCE_HTTPS', 'False').lower() == 'true'
Talisman(app, 
         content_security_policy=None, 
         force_https=force_https,
         force_https_permanent=False) 

# Fix for proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

#########################==================== LOGGING SETUP ====================#########################
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#########################==================== FIREBASE INITIALIZATION ====================#########################
BASE_DIR = APP_DIR
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'serviceAccountKey.json')

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(f"Firebase service account not found at {SERVICE_ACCOUNT_PATH}")

cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Simple in-memory cache for user lookups (reduces Firebase queries)
user_cache = {}  # {email: {user_data}}
cache_timeout = 300  # 5 minutes

# DEMO MODE: Store demo predictions in memory
demo_predictions = {}  # {email: [predictions]}

#########################==================== AI MODEL INITIALIZATION ====================#########################
print("Loading AI models...")
try:
    load_models()
    logger.info("AI models loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load AI models: {e}")

# Initialize OpenAI client
hf_token = os.getenv("HF_TOKEN", "").strip()
hf_token_configured = bool(hf_token and hf_token.strip() and hf_token != 'your_huggingface_token_here')
if not hf_token_configured:
    logger.warning("HF_TOKEN is missing or still using the placeholder value")
    client = None
else:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=hf_token,
    )

#########################==================== CONFIGURATION ====================#########################
# Admin credentials (store hashed in production)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@admin.com')
ADMIN_PASSWORD_HASH = generate_password_hash(os.getenv('ADMIN_PASSWORD', '1234'), method='pbkdf2:sha256:100000')

# DEMO MODE CREDENTIALS (for testing without Firebase)
DEMO_MODE = True  # Set to False to disable demo mode
DEMO_EMAIL = 'demo@test.com'
DEMO_PASSWORD = 'demo123'

# Medical keywords for chatbot
MEDICAL_KEYWORDS = [
    'liver', 'cancer', 'tumor', 'symptom', 'pain', 'treatment', 'diagnosis',
    'doctor', 'hospital', 'clinic', 'medicine', 'drug', 'prescription',
    'health', 'medical', 'disease', 'illness', 'condition', 'therapy',
    'surgery', 'transplant', 'hepatitis', 'cirrhosis', 'fatigue', 'nausea',
    'vomiting', 'weight loss', 'appetite', 'jaundice', 'swelling', 'abdomen',
    'stomach', 'scan', 'ct', 'mri', 'ultrasound', 'blood test', 'biopsy',
    'chemotherapy', 'radiation', 'immunotherapy', 'oncologist', 'hepatologist',
    'risk factor', 'prevention', 'prognosis', 'survival', 'stage', 'metastasis',
    'fever', 'chills', 'night sweats', 'ascites', 'portal vein', 'liver function',
    'alt', 'ast', 'bilirubin', 'albumin', 'alpha-fetoprotein', 'afp', 'thanks', 'thank u', 'thank you', 'hi'
]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# SMTP Configuration
SMTP_HOST     = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT     = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER     = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM     = os.getenv('SMTP_FROM', 'Liver Care <noreply@livercare.com>')

# In-memory stores  {email: {code, expires_at, type}}
verification_codes    = {}   # for both reset & registration verification
pending_registrations = {}   # {email: {form data + password_hash, expires_at}}

#########################==================== DOCTOR MANAGEMENT FUNCTIONS ====================#########################

def get_random_doctor():
    """Get a random available doctor from the doctors collection"""
    try:
        doctors_ref = db.collection('doctors')
        doctors = doctors_ref.get()
        
        doctors_list = list(doctors)
        if not doctors_list:
            logger.warning("No doctors found in database")
            return None
        
        # Get random doctor
        random_doctor = random.choice(doctors_list)
        doctor_data = random_doctor.to_dict()
        
        return {
            'doctor_id': random_doctor.id,
            'name': doctor_data.get('name', 'Medical Specialist'),
            'email': doctor_data.get('email', 'doctor@livercare.com'),
            'mobile_num': doctor_data.get('mobile-num', 'Not available'),
            'specialization': doctor_data.get('specialization', 'General Medicine')
        }
    except Exception as e:
        logger.error(f"Error getting random doctor: {e}")
        return None

def assign_doctor_to_patient(patient_email):
    """Assign a doctor to a patient if not already assigned"""
    try:
        patient_record = get_user_record_by_email(patient_email)

        if not patient_record:
            logger.warning(f"Patient not found: {patient_email}")
            return None

        patient_data = patient_record['data']
        
        # If patient already has a doctor, return existing doctor info
        if patient_data.get('assigned_doctor_id'):
            return {
                'doctor_id': patient_data.get('assigned_doctor_id'),
                'name': patient_data.get('assigned_doctor_name'),
                'email': patient_data.get('assigned_doctor_email'),
                'mobile_num': patient_data.get('assigned_doctor_mobile'),
                'specialization': patient_data.get('assigned_doctor_specialty')
            }
        
        # Get a random doctor
        doctor = get_random_doctor()
        if not doctor:
            logger.warning("No doctor available for assignment")
            return None
        
        # Assign doctor to patient
        patient_record['reference'].update({
            'assigned_doctor_id': doctor['doctor_id'],
            'assigned_doctor_name': doctor['name'],
            'assigned_doctor_email': doctor['email'],
            'assigned_doctor_mobile': doctor['mobile_num'],
            'assigned_doctor_specialty': doctor['specialization'],
            'assigned_at': datetime.now()
        })

        invalidate_user_cache(patient_email)
        
        logger.info(f"Doctor {doctor['name']} assigned to patient {patient_email}")
        return doctor
        
    except Exception as e:
        logger.error(f"Error assigning doctor: {e}")
        return None

#########################==================== HELPER FUNCTIONS ====================#########################

def get_user_by_email(email):
    """Get user from cache first, then Firebase - reduces quota usage"""
    try:
        # Check cache first
        if email in user_cache:
            cached_data = user_cache[email]
            if cached_data.get('timestamp'):
                if datetime.now().timestamp() - cached_data['timestamp'] < cache_timeout:
                    logger.debug(f"User {email} loaded from cache")
                    return cached_data.get('data')

        # Query Firebase if not in cache
        users = db.collection('users')\
            .where(filter=FieldFilter('email', '==', email))\
            .limit(1)\
            .get()

        if users:
            user_data = list(users)[0].to_dict()
            # Cache it for 5 minutes
            user_cache[email] = {
                'data': user_data,
                'timestamp': datetime.now().timestamp()
            }
            logger.debug(f"User {email} loaded from Firebase and cached")
            return user_data

        return None
    except exceptions.ResourceExhausted as e:
        logger.error(f"Firebase quota exceeded for user: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None

def invalidate_user_cache(email):
    """Remove a user from the local cache after profile changes"""
    if email:
        user_cache.pop(email, None)

def get_user_record_by_email(email, force_refresh=False):
    """Return cached user data together with the document reference when available"""
    try:
        if not email:
            return None

        if not force_refresh and email in user_cache:
            cached_data = user_cache[email]
            timestamp = cached_data.get('timestamp')
            if timestamp and datetime.now().timestamp() - timestamp < cache_timeout:
                return cached_data

        users = db.collection('users')\
            .where(filter=FieldFilter('email', '==', email))\
            .limit(1)\
            .get()

        if not users:
            return None

        user_doc = list(users)[0]
        record = {
            'data': user_doc.to_dict(),
            'reference': user_doc.reference,
            'doc_id': user_doc.id,
            'timestamp': datetime.now().timestamp()
        }
        user_cache[email] = record
        return record
    except exceptions.ResourceExhausted as e:
        logger.error(f"Firebase quota exceeded when getting user record for {email}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting user record: {e}")
        return None

def clear_deleted_user_session():
    """Clear session when the account backing it no longer exists."""
    deleted_email = flask.session.get('user_email', '')
    flask.session.clear()
    logger.warning(f"Session cleared because user no longer exists: {deleted_email}")

def unauthorized_response(message):
    """Return JSON for API calls and redirect for page requests."""
    wants_json = flask.request.path.startswith('/api/') or flask.request.is_json
    if wants_json:
        return flask.jsonify({'success': False, 'message': message}), 401
    return flask.redirect('/login.html')

def save_chat_log(question, answer, status='success', model_name='moonshotai/Kimi-K2-Instruct-0905'):
    """Persist chatbot interactions for debugging and analytics."""
    try:
        db.collection('chat_logs').document().set({
            'user_email': flask.session.get('user_email', ''),
            'user_name': flask.session.get('user_name', ''),
            'is_admin': flask.session.get('admin_logged_in', False),
            'question': question,
            'answer': answer,
            'status': status,
            'model': model_name,
            'created_at': datetime.now()
        })
    except exceptions.ResourceExhausted:
        logger.warning(f"Firebase quota exceeded - chat log not saved: {question[:50]}")
    except Exception as e:
        logger.error(f"Failed to save chat log: {e}")

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in flask.session and not flask.session.get('admin_logged_in'):
            return unauthorized_response('Please login first')

        if flask.session.get('admin_logged_in'):
            return f(*args, **kwargs)

        user_record = get_user_record_by_email(flask.session.get('user_email'), force_refresh=True)
        if not user_record:
            clear_deleted_user_session()
            return unauthorized_response('Your account was removed. Please log in again.')

        user_data = user_record.get('data', {})
        flask.session['user_name'] = user_data.get('full_name', flask.session.get('user_name', ''))
        flask.session['patient_id'] = user_data.get('patient_id', flask.session.get('patient_id', ''))
        flask.session['age'] = str(user_data.get('age', '')) if user_data.get('age') is not None else ''
        flask.session['gender'] = user_data.get('gender', flask.session.get('gender', ''))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.get('admin_logged_in'):
            return flask.jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_email_extension(email):
    """Validate email extension/domain is from an allowed provider"""
    allowed_domains = {
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'email.com',
        'aol.com', 'icloud.com', 'mail.com', 'protonmail.com', 'zoho.com',
        'yandex.com', 'mail.ru', 'gmx.com', 'webmail.com', 'inbox.com'
    }
    
    try:
        # Extract domain from email
        domain = email.split('@')[1].lower() if '@' in email else ''
        
        if domain in allowed_domains:
            return True
        return False
    except Exception:
        return False

def validate_phone(phone):
    """Validate Egyptian phone number"""
    pattern = r'^01[0-9]{9}$'
    return re.match(pattern, phone) is not None

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ''
    return re.sub(r'[<>{}]', '', text)[:500]

def generate_patient_id():
    """Generate atomic auto-incrementing patient ID using Firestore transaction"""
    counter_ref = db.collection('metadata').document('counters')
    
    @firestore.transactional
    def update_counter(transaction):
        snapshot = transaction.get(counter_ref)
        if not snapshot.exists:
            transaction.set(counter_ref, {'patient_counter': 1})
            return 1
        else:
            current = snapshot.get('patient_counter', 0)
            new_counter = current + 1
            transaction.update(counter_ref, {'patient_counter': new_counter})
            return new_counter
    
    try:
        transaction = db.transaction()
        new_num = update_counter(transaction)
        return f"#PT-{new_num:05d}"
    except Exception as e:
        logger.error(f"Failed to generate patient ID: {e}")
        return f"#PT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def is_medical_question(question):
    """Check if the question is medical-related"""
    if not question:
        return False
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in MEDICAL_KEYWORDS)

def generate_verification_code():
    """Generate a secure 6-digit verification code"""
    return str(secrets.randbelow(900000) + 100000)   # always 6 digits

def send_verification_email(to_email, code, purpose='registration'):
    """Send a verification code email via SMTP (Gmail / any SMTP provider)"""
    if not SMTP_USER or not SMTP_PASSWORD or SMTP_PASSWORD == 'your_app_password':
        logger.warning("SMTP not configured – verification email not sent")
        return False
    try:
        if purpose == 'reset':
            subject   = 'Liver Care – Password Reset Code'
            headline  = 'Password Reset Request'
            body_line = 'Use the code below to reset your password.'
        else:
            subject   = 'Liver Care – Email Verification Code'
            headline  = 'Verify Your Email Address'
            body_line = 'Use the code below to complete your registration.'

        html = f"""
        <html><body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr><td align="center" style="padding:40px 20px;">
            <table width="480" cellpadding="0" cellspacing="0"
                   style="background:#fff;border-radius:16px;overflow:hidden;
                          box-shadow:0 4px 24px rgba(0,0,0,0.08);">
              <tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1B3C53 50%,#0ea5e9 100%);
                             padding:32px 40px;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:24px;font-weight:700;">Liver Care</h1>
                <p style="color:rgba(255,255,255,0.75);margin:6px 0 0;font-size:13px;">
                  AI-Powered Liver Cancer Detection
                </p>
              </td></tr>
              <tr><td style="padding:40px;">
                <h2 style="color:#0f172a;font-size:20px;margin:0 0 8px;">{headline}</h2>
                <p style="color:#64748b;font-size:15px;margin:0 0 32px;">{body_line}</p>
                <div style="background:#f0f9ff;border:2px dashed #0ea5e9;border-radius:12px;
                            text-align:center;padding:28px;">
                  <p style="color:#64748b;font-size:13px;margin:0 0 8px;
                            letter-spacing:0.05em;text-transform:uppercase;">Your verification code</p>
                  <span style="font-size:40px;font-weight:800;color:#0ea5e9;letter-spacing:10px;">
                    {code}
                  </span>
                </div>
                <p style="color:#94a3b8;font-size:13px;margin:24px 0 0;text-align:center;">
                  This code expires in <strong>10 minutes</strong>.<br>
                  If you did not request this, please ignore this email.
                </p>
              </td></tr>
              <tr><td style="background:#f8fafc;padding:20px 40px;text-align:center;
                             border-top:1px solid #e2e8f0;">
                <p style="color:#94a3b8;font-size:12px;margin:0;">
                  &copy; 2025 Liver Care. All rights reserved.
                </p>
              </td></tr>
            </table>
          </td></tr>
        </table>
        </body></html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = SMTP_FROM
        msg['To']      = to_email
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        logger.info(f"Verification email ({purpose}) sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def store_verification_code(email, purpose):
    """Generate, store and return a new code for the given email & purpose"""
    code = generate_verification_code()
    verification_codes[email] = {
        'code':       code,
        'expires_at': datetime.now() + timedelta(minutes=10),
        'purpose':    purpose,
        'verified':   False
    }
    return code

def check_verification_code(email, code):
    """Return True if code is correct and not expired"""
    entry = verification_codes.get(email)
    if not entry:
        return False, 'No verification code found'
    if datetime.now() > entry['expires_at']:
        verification_codes.pop(email, None)
        return False, 'Code has expired'
    if entry['code'] != code.strip():
        return False, 'Incorrect code'
    return True, 'OK'

##########################==================== CONTEXT PROCESSORS ====================#########################

@app.context_processor
def inject_user():
    """Make session available in all templates"""
    return dict(session=flask.session)

#########################==================== PAGE ROUTES ====================#########################

@app.route("/")
def root():
    return flask.redirect('/index.html')

@app.route("/index.html")
def home():
    return flask.render_template('index.html', title="Home Page")

@app.route("/news.html")
def news():
    return flask.render_template("news.html", title="News Page")

@app.route('/contact-us.html')
def contact_us():
    return flask.render_template('contact-us.html', title="Contact-us Page")

@app.route('/faq.html')
def helpage():
    return flask.render_template('faq.html', title="Help Page")

@app.route('/profile.html')
@login_required
def profile():
    if flask.session.get('admin_logged_in'):
        return flask.redirect('/admin-dashboard.html?denied=profile')

    user_record = get_user_record_by_email(flask.session['user_email'])
    user = user_record.get('data', {}) if user_record else {}
    return flask.render_template('profile.html', title="Profile Page", user=user)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if flask.session.get('admin_logged_in'):
        return flask.jsonify({'success': False, 'error': 'Not a user account'}), 400
    
    try:
        data = flask.request.json
        
        full_name = sanitize_input(data.get('fullName', ''))
        age = data.get('age')
        gender = data.get('gender', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        
        if phone and not validate_phone(phone):
            return flask.jsonify({'success': False, 'error': 'Invalid phone number'}), 400
        
        if age:
            try:
                age = int(age)
                if age < 0 or age > 150:
                    return flask.jsonify({'success': False, 'error': 'Invalid age'}), 400
            except ValueError:
                return flask.jsonify({'success': False, 'error': 'Age must be a number'}), 400
        
        current_email = flask.session['user_email']
        user_record = get_user_record_by_email(current_email, force_refresh=True)

        if not user_record:
            return flask.jsonify({'success': False, 'error': 'User not found'}), 404

        user_record['reference'].update({
            'full_name': full_name,
            'age': age,
            'gender': gender,
            'phone': phone,
            'email': email,
            'updated_at': datetime.now()
        })

        if email and email != current_email:
            invalidate_user_cache(current_email)
        invalidate_user_cache(email or current_email)

        flask.session['user_email'] = email or current_email
        flask.session['user_name'] = full_name
        flask.session['age'] = str(age) if age else ''
        flask.session['gender'] = gender
        
        return flask.jsonify({'success': True})
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return flask.jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/result.html')
def result():
    return flask.render_template('result.html', title='Result Page')

@app.route('/my-results.html')
@login_required
def my_results_page():
    if flask.session.get('admin_logged_in'):
        return flask.redirect('/admin-dashboard.html?denied=results')
    return flask.render_template('my-results.html', title='My Results')

@app.route('/admin-dashboard.html')
@admin_required
def admin_dashboard():
    return flask.render_template('admin-dashboard.html', title='Admin Dashboard')

#########################==================== AUTHENTICATION ROUTES ====================#########################

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        email = sanitize_input(flask.request.form.get('email', '').strip())
        password = flask.request.form.get('password', '')
        normalized_email = email.lower()
        normalized_admin_email = ADMIN_EMAIL.strip().lower()
        
        if not email or not password:
            return flask.jsonify({'success': False, 'message': 'Email and password required'}), 400

        # DEMO MODE LOGIN (no Firebase required)
        if DEMO_MODE and email == DEMO_EMAIL and password == DEMO_PASSWORD:
            flask.session.clear()
            flask.session.permanent = True
            flask.session['user_email'] = DEMO_EMAIL
            flask.session['user_name'] = 'Demo User'
            flask.session['patient_id'] = '#PT-00001'
            flask.session['age'] = '30'
            flask.session['gender'] = 'Male'
            flask.session['is_admin'] = False
            logger.info(f"DEMO MODE login: {DEMO_EMAIL}")
            return flask.jsonify({
                'success': True,
                'is_admin': False,
                'redirect': '/index.html',
                'name': 'Demo User'
            }), 200

        # Fast admin check
        if normalized_email == normalized_admin_email:
            if check_password_hash(ADMIN_PASSWORD_HASH, password):
                flask.session.clear()
                flask.session.permanent = True
                flask.session['admin_logged_in'] = True
                flask.session['admin_username'] = email
                flask.session['is_admin'] = True
                logger.info(f"Admin login successful: {email}")
                return flask.jsonify({
                    'success': True,
                    'is_admin': True,
                    'redirect': '/admin-dashboard.html',
                    'name': 'Administrator'
                }), 200

            logger.warning(f"Invalid admin credentials for {email}")
            return flask.jsonify({'success': False, 'message': 'Invalid admin credentials'}), 200
        
        # Refresh on login so the session always gets the canonical patient ID
        user_record = get_user_record_by_email(email, force_refresh=True)
        user_data = user_record.get('data') if user_record else None

        if not user_data:
            return flask.jsonify({'success': False, 'message': 'Email not found'}), 200
        
        # Password check
        if not check_password_hash(user_data['password_hash'], password):
            logger.warning(f"Failed login attempt for {email}")
            return flask.jsonify({'success': False, 'message': 'Incorrect password'}), 200
        
        # Set session (fast)
        flask.session.clear()
        flask.session.permanent = True
        flask.session['user_email'] = email
        flask.session['user_name'] = user_data.get('full_name', '')
        flask.session['patient_id'] = user_data.get('patient_id', '')
        flask.session['is_admin'] = False
        flask.session['age'] = str(user_data.get('age', ''))
        flask.session['gender'] = user_data.get('gender', '')
        
        logger.info(f"User login successful: {email}")
        return flask.jsonify({
            'success': True,
            'is_admin': False,
            'redirect': '/index.html',
            'name': user_data.get('full_name', '')
        }), 200
    
    return flask.render_template('login.html', title='Login Page')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        try:
            full_name = sanitize_input(flask.request.form.get('full_name', '').strip())
            email = sanitize_input(flask.request.form.get('email', '').strip())
            phone = sanitize_input(flask.request.form.get('phone', '').strip())
            age = flask.request.form.get('age', 0)
            gender = flask.request.form.get('gender', '')
            password = flask.request.form.get('password', '')
            confirm = flask.request.form.get('confirm_password', '')
            
            # Fast validations
            if not all([full_name, email, phone, password]):
                return flask.jsonify({'success': False, 'message': 'All fields are required'}), 400
            
            if len(password) < 8:
                return flask.jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

            if not any(c.isupper() for c in password):
                return flask.jsonify({'success': False, 'message': 'Password must contain at least one uppercase letter'}), 400

            if not any(c.islower() for c in password):
                return flask.jsonify({'success': False, 'message': 'Password must contain at least one lowercase letter'}), 400

            if password != confirm:
                return flask.jsonify({'success': False, 'message': 'Passwords do not match'}), 400
            
            if not validate_email(email):
                return flask.jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            if not validate_email_extension(email):
                return flask.jsonify({'success': False, 'message': 'Email provider not allowed. Please use gmail.com, yahoo.com, outlook.com, hotmail.com, or other supported providers'}), 400
            
            if not validate_phone(phone):
                return flask.jsonify({'success': False, 'message': 'Phone number not valid (must be 01XXXXXXXXX)'}), 400
            
            try:
                age = int(age) if age else None
                if age and (age < 0 or age > 150):
                    return flask.jsonify({'success': False, 'message': 'Invalid age'}), 400
            except (ValueError, TypeError):
                age = None
            
            # Check existing user - parallel checks
            existing_email = db.collection('users')\
                .where(filter=FieldFilter('email', '==', email))\
                .limit(1)\
                .get()
            if list(existing_email):
                return flask.jsonify({'success': False, 'message': 'Email already registered'}), 400

            existing_phone = db.collection('users')\
                .where(filter=FieldFilter('phone', '==', phone))\
                .limit(1)\
                .get()
            if list(existing_phone):
                return flask.jsonify({'success': False, 'message': 'Phone number already registered'}), 400
            
            # Hash password
            password_hash = generate_password_hash(password, method='pbkdf2:sha256:100000')

            # Store as pending — do NOT write to Firestore yet
            pending_registrations[email] = {
                'full_name':     full_name,
                'phone':         phone,
                'age':           age,
                'gender':        gender,
                'password_hash': password_hash,
                'expires_at':    datetime.now() + timedelta(minutes=15)
            }

            # Send verification code
            code = store_verification_code(email, 'registration')
            sent = send_verification_email(email, code, purpose='registration')
            if not sent:
                logger.warning(f"[DEV] Registration code for {email}: {code}")

            logger.info(f"Pending registration stored for {email}, verification email sent={sent}")

            return flask.jsonify({
                'success':              True,
                'requires_verification': True,
                'email':                email,
                'redirect':             f'/verify-email.html?email={email}'
            }), 200
        
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return flask.jsonify({'success': False, 'message': 'Server error during registration'}), 500
    
    return flask.render_template('register.html', title='Register Page')


@app.route('/logout')
def logout():
    user = flask.session.get('user_email') or flask.session.get('admin_username')
    logger.info(f"User logged out: {user}")
    flask.session.clear()
    return flask.redirect('/login.html')

# ─────────────────────────────────────────────────────────────
#  FORGOT PASSWORD
# ─────────────────────────────────────────────────────────────

@app.route('/forgot-password')
@app.route('/forgot-password.html')
def forgot_password_page():
    return flask.render_template('forgot-password.html', title='Forgot Password')

@app.route('/api/send-reset-code', methods=['POST'])
def send_reset_code():
    """Step 1 – send a 6-digit reset code to the email address"""
    data  = flask.request.get_json(silent=True) or {}
    email = sanitize_input(data.get('email', '').strip().lower())

    if not email or not validate_email(email):
        return flask.jsonify({'success': False, 'message': 'Valid email required'}), 400

    # Always respond the same way to avoid leaking whether an account exists
    user = get_user_by_email(email)
    if user:
        code = store_verification_code(email, 'reset')
        sent = send_verification_email(email, code, purpose='reset')
        if not sent:
            # SMTP not configured – log the code for development
            logger.warning(f"[DEV] Reset code for {email}: {code}")
    else:
        logger.warning(f"Password reset requested for unknown email: {email}")

    return flask.jsonify({
        'success': True,
        'message': 'If that email is registered, a code has been sent.'
    }), 200

@app.route('/api/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Step 2 – verify the code; mark it as confirmed"""
    data  = flask.request.get_json(silent=True) or {}
    email = sanitize_input(data.get('email', '').strip().lower())
    code  = data.get('code', '').strip()

    if not email or not code:
        return flask.jsonify({'success': False, 'message': 'Email and code required'}), 400

    ok, msg = check_verification_code(email, code)
    if not ok:
        return flask.jsonify({'success': False, 'message': msg}), 400

    # Mark as verified so the reset step can proceed
    verification_codes[email]['verified'] = True
    return flask.jsonify({'success': True}), 200

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Step 3 – save the new password after code has been verified"""
    data         = flask.request.get_json(silent=True) or {}
    email        = sanitize_input(data.get('email', '').strip().lower())
    new_password = data.get('password', '')
    confirm      = data.get('confirm_password', '')

    if not email or not new_password:
        return flask.jsonify({'success': False, 'message': 'Email and new password required'}), 400

    if new_password != confirm:
        return flask.jsonify({'success': False, 'message': 'Passwords do not match'}), 400

    if len(new_password) < 8:
        return flask.jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

    if not any(c.isupper() for c in new_password):
        return flask.jsonify({'success': False, 'message': 'Password must contain at least one uppercase letter'}), 400

    if not any(c.islower() for c in new_password):
        return flask.jsonify({'success': False, 'message': 'Password must contain at least one lowercase letter'}), 400

    entry = verification_codes.get(email)
    if not entry or not entry.get('verified'):
        return flask.jsonify({'success': False, 'message': 'Email not verified. Please start over.'}), 400

    if datetime.now() > entry['expires_at']:
        verification_codes.pop(email, None)
        return flask.jsonify({'success': False, 'message': 'Session expired. Please start over.'}), 400

    user_record = get_user_record_by_email(email, force_refresh=True)
    if not user_record:
        return flask.jsonify({'success': False, 'message': 'Account not found'}), 404

    new_hash = generate_password_hash(new_password, method='pbkdf2:sha256:100000')
    user_record['reference'].update({'password_hash': new_hash, 'updated_at': datetime.now()})
    invalidate_user_cache(email)
    verification_codes.pop(email, None)

    logger.info(f"Password reset successful for {email}")
    return flask.jsonify({'success': True, 'message': 'Password updated successfully'}), 200

# ─────────────────────────────────────────────────────────────
#  EMAIL VERIFICATION (after registration)
# ─────────────────────────────────────────────────────────────

@app.route('/verify-email')
@app.route('/verify-email.html')
def verify_email_page():
    return flask.render_template('verify-email.html', title='Verify Email')

@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    """Resend the registration verification code"""
    data  = flask.request.get_json(silent=True) or {}
    email = sanitize_input(data.get('email', '').strip().lower())

    if not email or email not in pending_registrations:
        return flask.jsonify({'success': False, 'message': 'No pending registration for that email'}), 400

    if datetime.now() > pending_registrations[email]['expires_at']:
        pending_registrations.pop(email, None)
        return flask.jsonify({'success': False, 'message': 'Registration expired. Please register again.'}), 400

    code = store_verification_code(email, 'registration')
    sent = send_verification_email(email, code, purpose='registration')
    if not sent:
        logger.warning(f"[DEV] Registration code for {email}: {code}")

    return flask.jsonify({'success': True, 'message': 'Code resent'}), 200

@app.route('/api/verify-registration', methods=['POST'])
def verify_registration():
    """Complete registration after email code is verified"""
    data  = flask.request.get_json(silent=True) or {}
    email = sanitize_input(data.get('email', '').strip().lower())
    code  = data.get('code', '').strip()

    if not email or not code:
        return flask.jsonify({'success': False, 'message': 'Email and code required'}), 400

    # Check code
    ok, msg = check_verification_code(email, code)
    if not ok:
        return flask.jsonify({'success': False, 'message': msg}), 400

    # Retrieve pending registration
    pending = pending_registrations.get(email)
    if not pending:
        return flask.jsonify({'success': False, 'message': 'No pending registration. Please register again.'}), 400

    if datetime.now() > pending['expires_at']:
        pending_registrations.pop(email, None)
        verification_codes.pop(email, None)
        return flask.jsonify({'success': False, 'message': 'Registration expired. Please register again.'}), 400

    try:
        patient_id = generate_patient_id()
        user_ref   = db.collection('users').document()
        user_ref.set({
            'patient_id':   patient_id,
            'full_name':    pending['full_name'],
            'email':        email,
            'phone':        pending['phone'],
            'age':          pending['age'],
            'gender':       pending['gender'],
            'password_hash': pending['password_hash'],
            'email_verified': True,
            'reg_date':     datetime.now(),
            'created_at':   datetime.now()
        })

        # Async doctor assignment
        threading.Thread(target=assign_doctor_to_patient, args=(email,)).start()

        # Cleanup
        pending_registrations.pop(email, None)
        verification_codes.pop(email, None)
        invalidate_user_cache(email)

        logger.info(f"Registration completed for {email} (patient_id={patient_id})")
        return flask.jsonify({
            'success':    True,
            'redirect':   '/login.html',
            'user_name':  pending['full_name'],
            'patient_id': patient_id
        }), 200

    except Exception as e:
        logger.error(f"Error completing registration for {email}: {e}")
        return flask.jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

@app.route('/check-session')
def check_session():
    """Check session without hitting Firebase"""
    is_admin = flask.session.get('admin_logged_in', False)

    if not is_admin and flask.session.get('user_email'):
        user_record = get_user_record_by_email(flask.session.get('user_email'), force_refresh=True)
        if not user_record:
            clear_deleted_user_session()
            return flask.jsonify({
                'logged_in': False,
                'is_admin': False,
                'user_email': '',
                'user_name': '',
                'patient_id': '',
                'age': '',
                'gender': ''
            }), 200

        user_data = user_record.get('data', {})
        flask.session['user_name'] = user_data.get('full_name', flask.session.get('user_name', ''))
        flask.session['patient_id'] = user_data.get('patient_id', flask.session.get('patient_id', ''))
        flask.session['age'] = str(user_data.get('age', '')) if user_data.get('age') is not None else ''
        flask.session['gender'] = user_data.get('gender', flask.session.get('gender', ''))

    session_data = {
        'logged_in': 'user_email' in flask.session or is_admin,
        'is_admin': is_admin,
        'user_email': flask.session.get('user_email', ''),
        'user_name': flask.session.get('user_name', '') if not is_admin else 'Administrator',
        'patient_id': flask.session.get('patient_id', ''),
        'age': flask.session.get('age', ''),
        'gender': flask.session.get('gender', '')
    }
    return flask.jsonify(session_data), 200

@app.route('/get-user-profile')
@login_required
def get_user_profile():
    if flask.session.get('admin_logged_in'):
        return flask.jsonify({'success': False, 'message': 'Not a user account'}), 400

    try:
        # DEMO MODE: Return demo profile
        if DEMO_MODE and flask.session.get('user_email') == DEMO_EMAIL:
            return flask.jsonify({
                'success': True,
                'age': flask.session.get('age', '30'),
                'gender': flask.session.get('gender', 'Male'),
                'full_name': flask.session.get('user_name', 'Demo User'),
                'patient_id': flask.session.get('patient_id', '#PT-00001')
            }), 200

        user_record = get_user_record_by_email(flask.session['user_email'])

        if not user_record:
            return flask.jsonify({'success': False, 'message': 'User not found'}), 404

        user_data = user_record['data']
        return flask.jsonify({
            'success': True,
            'age': user_data.get('age', ''),
            'gender': user_data.get('gender', ''),
            'full_name': user_data.get('full_name', ''),
            'patient_id': user_data.get('patient_id', '')
        })
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return flask.jsonify({'success': False, 'message': str(e)}), 500

#########################==================== API ROUTES ====================#########################

@app.route('/api/get-doctor-info')
@login_required
def get_doctor_info():
    """Get the assigned doctor for the current patient"""
    try:
        patient_email = flask.session.get('user_email')

        user_record = get_user_record_by_email(patient_email)

        if not user_record:
            return flask.jsonify({'success': False, 'message': 'Patient not found'}), 404

        patient_data = user_record['data']
        
        # Check if patient has assigned doctor
        if patient_data.get('assigned_doctor_id'):
            doctor_info = {
                'assigned': True,
                'doctor_id': patient_data.get('assigned_doctor_id'),
                'name': patient_data.get('assigned_doctor_name'),
                'email': patient_data.get('assigned_doctor_email'),
                'mobile_num': patient_data.get('assigned_doctor_mobile'),
                'specialization': patient_data.get('assigned_doctor_specialty')
            }
        else:
            # Auto-assign a doctor if not assigned (sync for first time)
            doctor = assign_doctor_to_patient(patient_email)
            if doctor:
                doctor_info = {
                    'assigned': True,
                    'doctor_id': doctor['doctor_id'],
                    'name': doctor['name'],
                    'email': doctor['email'],
                    'mobile_num': doctor['mobile_num'],
                    'specialization': doctor['specialization']
                }
            else:
                doctor_info = {'assigned': False}
        
        return flask.jsonify({'success': True, 'doctor': doctor_info})
        
    except Exception as e:
        logger.error(f"Get doctor info error: {e}")
        return flask.jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = flask.request.json
        user_question = sanitize_input(data.get('question', '').strip())
        
        if not user_question:
            answer = 'Please ask a question.'
            save_chat_log(user_question, answer, status='validation')
            return flask.jsonify({'answer': answer})
        
        if not is_medical_question(user_question):
            answer = "I'm a medical assistant specialized in liver health and can only answer medical questions. Please ask me about symptoms, treatments, diagnosis, or other health-related topics."
            save_chat_log(user_question, answer, status='filtered')
            return flask.jsonify({'answer': answer})

        if not hf_token_configured or client is None:
            answer = 'The AI chatbot is not configured yet. Please add a valid HF_TOKEN in the .env file and restart the server.'
            save_chat_log(user_question, answer, status='configuration_error')
            return flask.jsonify({'answer': answer}), 503
        
        system_prompt = """You are a helpful medical assistant specializing in liver health and liver cancer. 
        Only provide information related to medical topics. If asked about non-medical topics, politely redirect 
        to medical discussions. Be professional, accurate, and compassionate."""
        
        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Instruct-0905",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            timeout=30
        )
        
        answer = completion.choices[0].message.content
        save_chat_log(user_question, answer, status='success')
        return flask.jsonify({'answer': answer})
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        answer = f'Chat service error: {str(e)}'
        save_chat_log(flask.request.json.get('question', '') if flask.request.json else '', answer, status='error')
        return flask.jsonify({'answer': answer})

@app.route('/api/predict', methods=['POST'])
@login_required
def predict():
    # Check if admin is trying to upload
    if flask.session.get('admin_logged_in') or flask.session.get('is_admin'):
        return flask.jsonify({
            'success': False, 
            'message': 'Admin accounts cannot upload or analyze medical images. Please use a patient account.'
        }), 403
    try:
        if 'image' not in flask.request.files:
            return flask.jsonify({'success': False, 'message': 'No image provided'}), 400
        
        file = flask.request.files['image']
        
        if file.filename == '':
            return flask.jsonify({'success': False, 'message': 'No image selected'}), 400
        
        if not allowed_file(file.filename):
            return flask.jsonify({'success': False, 'message': 'File type not allowed (use PNG, JPG, JPEG)'}), 400
        
        image_data = file.read(5 * 1024 * 1024)
        if len(image_data) >= 5 * 1024 * 1024:
            return flask.jsonify({'success': False, 'message': 'File too large (max 5MB)'}), 400
        
        file.seek(0)
        image_hash = hashlib.md5(image_data).hexdigest()

        user_email = flask.session.get('user_email')

        # DEMO MODE: Return sample prediction without Firebase
        if DEMO_MODE and user_email == DEMO_EMAIL:
            prediction_id = str(uuid.uuid4())

            # Demo predictions (different based on image)
            demo_predictions_list = [
                {
                    "overall_status": "NORMAL",
                    "overall_message": "Analysis complete - No abnormalities detected",
                    "cancer_stage": {
                        "classification": "Benign",
                        "stage": "N/A",
                        "stage_num": 0,
                        "tumor_size": 0,
                        "confidence": 0.95
                    },
                    "tumor_location": {
                        "location": "N/A",
                        "confidence": 0
                    }
                },
                {
                    "overall_status": "ABNORMAL",
                    "overall_message": "Analysis complete - Abnormality detected",
                    "cancer_stage": {
                        "classification": "Malignant",
                        "stage": "Stage II",
                        "stage_num": 2,
                        "tumor_size": 45.5,
                        "confidence": 0.87
                    },
                    "tumor_location": {
                        "location": "Right Lobe",
                        "confidence": 0.92
                    }
                }
            ]

            # Randomly select prediction
            demo_pred = demo_predictions_list[len(image_hash) % 2]

            # Store in memory
            if user_email not in demo_predictions:
                demo_predictions[user_email] = []

            demo_predictions[user_email].insert(0, {
                'id': prediction_id,
                'predictions': demo_pred,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': 'Demo User',
                'patient_id': '#PT-00001',
                'age': '30',
                'gender': 'Male'
            })

            logger.info(f"DEMO MODE prediction created: {prediction_id}")
            return flask.jsonify({
                'success': True,
                'is_duplicate': False,
                'prediction_id': prediction_id,
                'predictions': demo_pred,
                'message': 'DEMO: Analysis complete (sample data)'
            }), 200

        existing_prediction = db.collection('predictions')\
            .where(filter=FieldFilter('user_email', '==', user_email))\
            .where(filter=FieldFilter('image_hash', '==', image_hash))\
            .limit(1)\
            .get()
        
        existing_list = list(existing_prediction)
        if existing_list:
            existing_doc = existing_list[0]
            existing_data = existing_doc.to_dict()
            logger.info(f"Duplicate prediction for user {user_email}")
            return flask.jsonify({
                'success': True,
                'is_duplicate': True,
                'prediction_id': existing_doc.id,
                'predictions': existing_data.get('predictions', {}),
                'message': 'This image has already been scanned. Showing previous result.'
            }), 200
        
        logger.info(f"Processing new image: {file.filename} for user {user_email}")
        predictions = get_full_prediction(image_data)
        
        if predictions.get('overall_status') == 'ERROR':
            return flask.jsonify({
                'success': False,
                'message': predictions.get('overall_message', 'Error processing image')
            }), 500
        
        prediction_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        user_record = get_user_record_by_email(flask.session.get('user_email'))
        user_data = user_record.get('data', {}) if user_record else {}

        # Ensure doctor assignment is available before saving the report
        if user_email and not user_data.get('assigned_doctor_id'):
            assign_doctor_to_patient(user_email)
            user_record = get_user_record_by_email(user_email, force_refresh=True)
            user_data = user_record.get('data', {}) if user_record else {}
        
        # Use the canonical patient ID from the user record
        current_patient_id = user_data.get('patient_id') or flask.session.get('patient_id', '')
        
        # Get doctor info for this patient
        doctor_info = {
            'doctor_name': user_data.get('assigned_doctor_name', 'Not Assigned'),
            'doctor_email': user_data.get('assigned_doctor_email', 'N/A'),
            'doctor_mobile': user_data.get('assigned_doctor_mobile', 'N/A'),
            'doctor_specialty': user_data.get('assigned_doctor_specialty', 'General')
        }
        
        db.collection('predictions').document(prediction_id).set({
            'user_email': flask.session.get('user_email', ''),
            'user_name': flask.session.get('user_name', ''),
            'patient_id': current_patient_id,
            'age': user_data.get('age', ''),
            'gender': user_data.get('gender', ''),
            'predictions': predictions,
            'image_hash': image_hash,
            'created_at': timestamp,
            'doctor_name': doctor_info['doctor_name'],
            'doctor_email': doctor_info['doctor_email'],
            'doctor_mobile': doctor_info['doctor_mobile'],
            'doctor_specialty': doctor_info['doctor_specialty']
        })
        
        logger.info(f"Prediction completed for {user_email}, ID: {prediction_id}")
        return flask.jsonify({
            'success': True,
            'is_duplicate': False,
            'prediction_id': prediction_id,
            'predictions': predictions,
            'message': 'Analysis complete'
        }), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return flask.jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/api/my-results')
@login_required
def get_my_results():
    if flask.session.get('admin_logged_in'):
        return flask.jsonify({'success': False, 'message': 'Not a user account'}), 400

    try:
        user_email = flask.session.get('user_email')
        canonical_patient_id = flask.session.get('patient_id', '')

        # DEMO MODE: Return demo predictions from memory
        if DEMO_MODE and user_email == DEMO_EMAIL:
            demo_results = demo_predictions.get(user_email, [])
            return flask.jsonify({'success': True, 'results': demo_results}), 200

        if not canonical_patient_id:
            user_record = get_user_record_by_email(user_email)
            if user_record:
                canonical_patient_id = user_record.get('data', {}).get('patient_id', '')

        predictions = db.collection('predictions')\
            .where(filter=FieldFilter('user_email', '==', user_email))\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(20)\
            .get()

        results = []
        for pred in predictions:
            data = pred.to_dict()
            created_at_str = ''
            if 'created_at' in data and data['created_at']:
                try:
                    if isinstance(data['created_at'], datetime):
                        created_at_str = data['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        created_at_str = str(data['created_at'])
                except:
                    created_at_str = str(data['created_at'])

            results.append({
                'id': pred.id,
                'user_name': data.get('user_name', ''),
                'patient_id': canonical_patient_id or data.get('patient_id', ''),
                'age': data.get('age', ''),
                'gender': data.get('gender', ''),
                'predictions': data.get('predictions', {}),
                'created_at': created_at_str,
                'doctor_name': data.get('doctor_name', ''),
                'doctor_email': data.get('doctor_email', ''),
                'doctor_mobile': data.get('doctor_mobile', ''),
                'doctor_specialty': data.get('doctor_specialty', '')
            })

        return flask.jsonify({'success': True, 'results': results})
    except Exception as e:
        logger.error(f"Get results error: {e}")
        return flask.jsonify({'success': False, 'message': 'Firebase quota exceeded. Please try again later.'}), 503

@app.route('/api/admin/analytics')
@admin_required
def get_admin_analytics():
    try:
        predictions = db.collection('predictions').get()
        users = db.collection('users').get()
        
        total_scans = 0
        benign_count = 0
        malignant_count = 0
        stage_distribution = {'Benign': 0, 'Stage I': 0, 'Stage II': 0, 'Stage III': 0, 'Stage IV': 0}
        total_tumor_size = 0
        tumor_size_count = 0
        unique_patients = set()
        
        male_scans = 0
        female_scans = 0
        male_benign = 0
        male_malignant = 0
        female_benign = 0
        female_malignant = 0
        
        age_0_18_benign = 0
        age_0_18_malignant = 0
        age_19_30_benign = 0
        age_19_30_malignant = 0
        age_31_45_benign = 0
        age_31_45_malignant = 0
        age_46_60_benign = 0
        age_46_60_malignant = 0
        age_60_plus_benign = 0
        age_60_plus_malignant = 0
        
        age_0_18_total = 0
        age_19_30_total = 0
        age_31_45_total = 0
        age_46_60_total = 0
        age_60_plus_total = 0
        
        daily_counts = {}
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_counts[date_str] = 0
        
        user_gender = {}
        user_age = {}
        
        for user in users:
            user_data = user.to_dict()
            email = user_data.get('email')
            if email:
                gender_val = user_data.get('gender', '')
                if gender_val and gender_val.lower() == 'male':
                    user_gender[email] = 'Male'
                elif gender_val and gender_val.lower() == 'female':
                    user_gender[email] = 'Female'
                else:
                    user_gender[email] = 'Other'
                
                age_val = user_data.get('age')
                if age_val:
                    try:
                        user_age[email] = int(age_val) if isinstance(age_val, str) else age_val
                    except (ValueError, TypeError):
                        user_age[email] = None
                else:
                    user_age[email] = None
        
        for pred in predictions:
            data = pred.to_dict()
            total_scans += 1
            
            email = data.get('user_email', '')
            if email:
                unique_patients.add(email)
            
            pred_data = data.get('predictions', {})
            cancer_stage = pred_data.get('cancer_stage', {})
            classification = cancer_stage.get('classification', '')
            stage = cancer_stage.get('stage', 'Stage I')
            tumor_size = cancer_stage.get('tumor_size', 0)
            
            created_at = data.get('created_at')
            if created_at and isinstance(created_at, datetime):
                date_str = created_at.strftime('%Y-%m-%d')
                if date_str in daily_counts:
                    daily_counts[date_str] += 1
            
            is_benign = (classification == 'Benign')
            if is_benign:
                benign_count += 1
                stage_distribution['Benign'] += 1
            else:
                malignant_count += 1
                if stage in stage_distribution:
                    stage_distribution[stage] += 1
            
            if tumor_size and tumor_size > 0:
                total_tumor_size += tumor_size
                tumor_size_count += 1
            
            gender = user_gender.get(email, 'Other')
            if gender == 'Male':
                male_scans += 1
                if is_benign:
                    male_benign += 1
                else:
                    male_malignant += 1
            elif gender == 'Female':
                female_scans += 1
                if is_benign:
                    female_benign += 1
                else:
                    female_malignant += 1
            
            age = user_age.get(email)
            if age:
                if age <= 18:
                    age_0_18_total += 1
                    if is_benign:
                        age_0_18_benign += 1
                    else:
                        age_0_18_malignant += 1
                elif age <= 30:
                    age_19_30_total += 1
                    if is_benign:
                        age_19_30_benign += 1
                    else:
                        age_19_30_malignant += 1
                elif age <= 45:
                    age_31_45_total += 1
                    if is_benign:
                        age_31_45_benign += 1
                    else:
                        age_31_45_malignant += 1
                elif age <= 60:
                    age_46_60_total += 1
                    if is_benign:
                        age_46_60_benign += 1
                    else:
                        age_46_60_malignant += 1
                else:
                    age_60_plus_total += 1
                    if is_benign:
                        age_60_plus_benign += 1
                    else:
                        age_60_plus_malignant += 1
        
        avg_tumor_size = total_tumor_size / tumor_size_count if tumor_size_count > 0 else 0
        
        sorted_dates = sorted(daily_counts.items())
        daily_labels = [date for date, _ in sorted_dates]
        daily_scans_data = [count for _, count in sorted_dates]
        
        analytics = {
            'total_scans': total_scans,
            'benign_count': benign_count,
            'malignant_count': malignant_count,
            'benign_percentage': round((benign_count / total_scans * 100) if total_scans > 0 else 0, 2),
            'malignant_percentage': round((malignant_count / total_scans * 100) if total_scans > 0 else 0, 2),
            'stage_distribution': stage_distribution,
            'average_tumor_size': round(avg_tumor_size, 2),
            'unique_patients': len(unique_patients),
            'gender_stats': {
                'scans': {'Male': male_scans, 'Female': female_scans, 'Other': 0},
                'benign': {'Male': male_benign, 'Female': female_benign, 'Other': 0},
                'malignant': {'Male': male_malignant, 'Female': female_malignant, 'Other': 0},
                'percentages': {
                    'Male': {
                        'total': male_scans,
                        'benign_percentage': round((male_benign / male_scans * 100) if male_scans > 0 else 0, 2),
                        'malignant_percentage': round((male_malignant / male_scans * 100) if male_scans > 0 else 0, 2)
                    },
                    'Female': {
                        'total': female_scans,
                        'benign_percentage': round((female_benign / female_scans * 100) if female_scans > 0 else 0, 2),
                        'malignant_percentage': round((female_malignant / female_scans * 100) if female_scans > 0 else 0, 2)
                    }
                }
            },
            'age_distribution': {
                'labels': ['0-18', '19-30', '31-45', '46-60', '60+'],
                'total': [age_0_18_total, age_19_30_total, age_31_45_total, age_46_60_total, age_60_plus_total],
                'benign': [age_0_18_benign, age_19_30_benign, age_31_45_benign, age_46_60_benign, age_60_plus_benign],
                'malignant': [age_0_18_malignant, age_19_30_malignant, age_31_45_malignant, age_46_60_malignant, age_60_plus_malignant]
            },
            'daily_trend': {
                'labels': daily_labels,
                'scans': daily_scans_data
            }
        }
        
        return flask.jsonify({'success': True, 'analytics': analytics})
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return flask.jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/debug-data')
@admin_required
def debug_data():
    """Debug endpoint to check what data exists"""
    predictions = db.collection('predictions').get()
    users = db.collection('users').get()
    
    result = {
        'total_predictions': len(list(predictions)),
        'total_users': len(list(users)),
        'predictions_with_email': 0,
        'users_with_gender': 0,
        'users_with_age': 0,
        'users_with_doctor': 0,
        'sample_predictions': [],
        'sample_users': []
    }
    
    for pred in predictions:
        data = pred.to_dict()
        if data.get('user_email'):
            result['predictions_with_email'] += 1
        if len(result['sample_predictions']) < 3:
            result['sample_predictions'].append({
                'id': pred.id,
                'user_email': data.get('user_email'),
                'patient_id': data.get('patient_id'),
                'classification': data.get('predictions', {}).get('cancer_stage', {}).get('classification')
            })
    
    for user in users:
        data = user.to_dict()
        if data.get('gender'):
            result['users_with_gender'] += 1
        if data.get('age'):
            result['users_with_age'] += 1
        if data.get('assigned_doctor_id'):
            result['users_with_doctor'] += 1
        if len(result['sample_users']) < 3:
            result['sample_users'].append({
                'email': data.get('email'),
                'gender': data.get('gender'),
                'age': data.get('age'),
                'patient_id': data.get('patient_id'),
                'assigned_doctor': data.get('assigned_doctor_name')
            })
    
    return flask.jsonify(result)

@app.route('/api/admin/logout')
def admin_logout():
    flask.session.pop('admin_logged_in', None)
    flask.session.pop('admin_username', None)
    return flask.jsonify({'success': True, 'redirect': '/login.html'})

########################==================== ERROR HANDLERS ====================########################

@app.errorhandler(404)
def not_found(error):
    return flask.jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return flask.jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return flask.jsonify({'error': 'File too large (max 5MB)'}), 413

@app.errorhandler(429)
def rate_limit_handler(error):
    return flask.jsonify({'error': 'Too many requests. Please try again later.'}), 429

########################==================== MAIN ====================########################
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info(f"Starting server on {host}:{port} (debug={debug_mode})")
    
    app.run(debug=debug_mode, host=host, port=port)
