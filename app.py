import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Import our modules
from auth import requires_auth, login_user, logout_user, check_auth
from models import init_db, CaseVolume
from config_models import init_config_db, SystemConfig

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration for Supabase
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Convert to use the psycopg2 driver which is installed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app, model_class=Base)

# Initialize database tables
with app.app_context():
    init_db(db)
    init_config_db(db)
    logging.info("Database tables created")

@app.route('/')
def index():
    """Main dashboard page - display only"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if login_user(username, password):
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@requires_auth
def admin():
    """Admin interface for updating case volumes"""
    current_volumes = CaseVolume.get_current_volumes()
    return render_template('admin.html', current_volumes=current_volumes)

@app.route('/admin/config')
@requires_auth
def admin_config():
    """Admin interface for system configuration"""
    config = SystemConfig.get_config()

    return render_template('admin_config.html', config=config)



@app.route('/admin/update_volumes', methods=['POST'])
@requires_auth
def update_volumes():
    """Update case volumes from admin interface"""
    try:
        mri = int(request.form.get('mri', 0))
        ct = int(request.form.get('ct', 0))
        xray = int(request.form.get('xray', 0))
        nucmed = int(request.form.get('nucmed', 0))
        ultrasound = int(request.form.get('ultrasound', 0))
        radiologist_staffing = int(request.form.get('radiologist_staffing', 100))
        admin_name = session.get('admin_username', 'Admin')
        
        CaseVolume.update_volumes(
            mri=mri, 
            ct=ct, 
            xray=xray, 
            nucmed=nucmed, 
            ultrasound=ultrasound,
            radiologist_staffing=radiologist_staffing,
            admin_name=admin_name
        )
        
        flash('Case volumes updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating volumes: {str(e)}', 'error')
        logging.error(f"Error updating volumes: {e}")
    
    return redirect(url_for('admin'))

@app.route('/admin/update_config', methods=['POST'])
@requires_auth
def update_config():
    """Update system configuration"""
    try:
        config_data = {
            # MRI configuration
            'mri_radcon5_threshold': int(request.form.get('mri_radcon5_threshold', 5)),
            'mri_radcon3_threshold': int(request.form.get('mri_radcon3_threshold', 15)),
            'mri_radcon1_threshold': int(request.form.get('mri_radcon1_threshold', 30)),
            'mri_processing_rate': int(request.form.get('mri_processing_rate', 20)),
            
            # CT configuration
            'ct_radcon5_threshold': int(request.form.get('ct_radcon5_threshold', 5)),
            'ct_radcon3_threshold': int(request.form.get('ct_radcon3_threshold', 15)),
            'ct_radcon1_threshold': int(request.form.get('ct_radcon1_threshold', 30)),
            'ct_processing_rate': int(request.form.get('ct_processing_rate', 30)),
            
            # X-Ray configuration
            'xray_radcon5_threshold': int(request.form.get('xray_radcon5_threshold', 10)),
            'xray_radcon3_threshold': int(request.form.get('xray_radcon3_threshold', 25)),
            'xray_radcon1_threshold': int(request.form.get('xray_radcon1_threshold', 50)),
            'xray_processing_rate': int(request.form.get('xray_processing_rate', 50)),
            
            # Nuclear Medicine configuration
            'nucmed_radcon5_threshold': int(request.form.get('nucmed_radcon5_threshold', 3)),
            'nucmed_radcon3_threshold': int(request.form.get('nucmed_radcon3_threshold', 8)),
            'nucmed_radcon1_threshold': int(request.form.get('nucmed_radcon1_threshold', 15)),
            'nucmed_processing_rate': int(request.form.get('nucmed_processing_rate', 15)),
            
            # Ultrasound configuration
            'ultrasound_radcon5_threshold': int(request.form.get('ultrasound_radcon5_threshold', 12)),
            'ultrasound_radcon3_threshold': int(request.form.get('ultrasound_radcon3_threshold', 30)),
            'ultrasound_radcon1_threshold': int(request.form.get('ultrasound_radcon1_threshold', 60)),
            'ultrasound_processing_rate': int(request.form.get('ultrasound_processing_rate', 25))
        }
        
        admin_name = session.get('admin_username', 'Admin')
        SystemConfig.update_config(config_data, admin_name)
        
        flash('Configuration updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')
        logging.error(f"Error updating config: {e}")
    
    return redirect(url_for('admin_config'))

@app.route('/api/volumes')
def get_volumes():
    """API endpoint to get current case volumes"""
    try:
        volumes = CaseVolume.get_current_volumes()
        if volumes:
            return jsonify({
                'mri': volumes['mri'],
                'ct': volumes['ct'],
                'xray': volumes['xray'],
                'nucmed': volumes['nucmed'],
                'ultrasound': volumes['ultrasound'],
                'radiologist_staffing': volumes.get('radiologist_staffing', 100),
                'timestamp': volumes['timestamp'].isoformat() if volumes['timestamp'] else None,
                'updated_by': volumes['updated_by']
            })
        else:
            return jsonify({
                'mri': 0,
                'ct': 0,
                'xray': 0,
                'nucmed': 0,
                'ultrasound': 0,
                'radiologist_staffing': 100,
                'timestamp': None,
                'updated_by': None
            })
    except Exception as e:
        logging.error(f"Error getting volumes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def get_config():
    """API endpoint to get current system configuration"""
    try:
        config = SystemConfig.get_config()
        return jsonify(config)
    except Exception as e:
        logging.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)