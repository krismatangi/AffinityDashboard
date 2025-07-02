import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from auth import requires_auth, login_user, logout_user

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

with app.app_context():
    # Create the case_volumes table
    db.session.execute(db.text("""
        CREATE TABLE IF NOT EXISTS case_volumes (
            id SERIAL PRIMARY KEY,
            mri_cases INTEGER DEFAULT 0 NOT NULL,
            ct_cases INTEGER DEFAULT 0 NOT NULL,
            xray_cases INTEGER DEFAULT 0 NOT NULL,
            nucmed_cases INTEGER DEFAULT 0 NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(100)
        )
    """))
    
    # Add nucmed_cases column if it doesn't exist (for existing databases)
    try:
        db.session.execute(db.text("""
            ALTER TABLE case_volumes ADD COLUMN IF NOT EXISTS nucmed_cases INTEGER DEFAULT 0 NOT NULL
        """))
    except Exception:
        pass  # Column might already exist
    
    # Create system configuration table
    db.session.execute(db.text("""
        CREATE TABLE IF NOT EXISTS system_config (
            id SERIAL PRIMARY KEY,
            mri_yellow INTEGER DEFAULT 10 NOT NULL,
            mri_orange INTEGER DEFAULT 25 NOT NULL,
            mri_red INTEGER DEFAULT 50 NOT NULL,
            ct_yellow INTEGER DEFAULT 15 NOT NULL,
            ct_orange INTEGER DEFAULT 35 NOT NULL,
            ct_red INTEGER DEFAULT 70 NOT NULL,
            xray_yellow INTEGER DEFAULT 25 NOT NULL,
            xray_orange INTEGER DEFAULT 60 NOT NULL,
            xray_red INTEGER DEFAULT 120 NOT NULL,
            nucmed_yellow INTEGER DEFAULT 8 NOT NULL,
            nucmed_orange INTEGER DEFAULT 20 NOT NULL,
            nucmed_red INTEGER DEFAULT 40 NOT NULL,
            mri_rate INTEGER DEFAULT 8 NOT NULL,
            ct_rate INTEGER DEFAULT 12 NOT NULL,
            xray_rate INTEGER DEFAULT 20 NOT NULL,
            nucmed_rate INTEGER DEFAULT 6 NOT NULL,
            radcon_4_threshold INTEGER DEFAULT 30 NOT NULL,
            radcon_3_threshold INTEGER DEFAULT 60 NOT NULL,
            radcon_2_threshold INTEGER DEFAULT 100 NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(100)
        )
    """))
    
    db.session.commit()
    
    # Initialize models with db reference
    from models import init_db
    from config_models import init_config_db
    init_db(db)
    init_config_db(db)

@app.route('/')
def index():
    """Main dashboard page - display only"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if login_user(username, password):
            flash('Login successful', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@requires_auth
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@requires_auth
def admin():
    """Admin interface for updating case volumes"""
    from models import CaseVolume
    current_volumes = CaseVolume.get_current_volumes()
    return render_template('admin.html', current_volumes=current_volumes)

@app.route('/admin/config')
@requires_auth
def admin_config():
    """Admin interface for system configuration"""
    from config_models import SystemConfig
    config = SystemConfig.get_config()
    if not config:
        config = SystemConfig.get_default_config()
    return render_template('admin_config.html', config=config)

@app.route('/admin/update', methods=['POST'])
@requires_auth
def update_volumes():
    """Update case volumes from admin interface"""
    from models import CaseVolume
    
    try:
        mri_cases = int(request.form.get('mri_cases', 0))
        ct_cases = int(request.form.get('ct_cases', 0))
        xray_cases = int(request.form.get('xray_cases', 0))
        nucmed_cases = int(request.form.get('nucmed_cases', 0))
        admin_name = request.form.get('admin_name', 'Admin').strip()
        
        # Validate inputs
        if mri_cases < 0 or ct_cases < 0 or xray_cases < 0 or nucmed_cases < 0:
            flash('Case counts cannot be negative', 'error')
            return redirect(url_for('admin'))
        
        if mri_cases > 9999 or ct_cases > 9999 or xray_cases > 9999 or nucmed_cases > 9999:
            flash('Case counts cannot exceed 9999', 'error')
            return redirect(url_for('admin'))
        
        CaseVolume.update_volumes(mri_cases, ct_cases, xray_cases, nucmed_cases, admin_name)
        flash(f'Case volumes updated successfully by {admin_name}', 'success')
        
    except ValueError:
        flash('Please enter valid numbers for case counts', 'error')
    except Exception as e:
        flash(f'Error updating volumes: {str(e)}', 'error')
    
    return redirect(url_for('admin'))

@app.route('/admin/config/update', methods=['POST'])
@requires_auth
def update_config():
    """Update system configuration"""
    from config_models import SystemConfig
    
    try:
        config_data = {
            'mri_yellow': int(request.form.get('mri_yellow', 10)),
            'mri_orange': int(request.form.get('mri_orange', 25)),
            'mri_red': int(request.form.get('mri_red', 50)),
            'ct_yellow': int(request.form.get('ct_yellow', 15)),
            'ct_orange': int(request.form.get('ct_orange', 35)),
            'ct_red': int(request.form.get('ct_red', 70)),
            'xray_yellow': int(request.form.get('xray_yellow', 25)),
            'xray_orange': int(request.form.get('xray_orange', 60)),
            'xray_red': int(request.form.get('xray_red', 120)),
            'nucmed_yellow': int(request.form.get('nucmed_yellow', 8)),
            'nucmed_orange': int(request.form.get('nucmed_orange', 20)),
            'nucmed_red': int(request.form.get('nucmed_red', 40)),
            'mri_rate': int(request.form.get('mri_rate', 8)),
            'ct_rate': int(request.form.get('ct_rate', 12)),
            'xray_rate': int(request.form.get('xray_rate', 20)),
            'nucmed_rate': int(request.form.get('nucmed_rate', 6)),
            'radcon_4_threshold': int(request.form.get('radcon_4_threshold', 30)),
            'radcon_3_threshold': int(request.form.get('radcon_3_threshold', 60)),
            'radcon_2_threshold': int(request.form.get('radcon_2_threshold', 100))
        }
        
        admin_name = session.get('username', 'Admin')
        
        # Validate inputs
        for key, value in config_data.items():
            if value < 0:
                flash(f'{key} cannot be negative', 'error')
                return redirect(url_for('admin_config'))
            if value > 9999:
                flash(f'{key} cannot exceed 9999', 'error')
                return redirect(url_for('admin_config'))
        
        SystemConfig.update_config(config_data, admin_name)
        flash(f'System configuration updated successfully by {admin_name}', 'success')
        
    except ValueError:
        flash('Please enter valid numbers for all configuration values', 'error')
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')
    
    return redirect(url_for('admin_config'))

@app.route('/api/volumes')
def get_volumes():
    """API endpoint to get current case volumes"""
    from models import CaseVolume
    current_volumes = CaseVolume.get_current_volumes()
    
    if current_volumes:
        return jsonify(current_volumes)
    else:
        return jsonify({
            'mri_cases': 0,
            'ct_cases': 0,
            'xray_cases': 0,
            'nucmed_cases': 0,
            'updated_at': None,
            'updated_by': None
        })

@app.route('/api/config')
def get_config():
    """API endpoint to get current system configuration"""
    from config_models import SystemConfig
    config = SystemConfig.get_config()
    
    if config:
        return jsonify(config)
    else:
        return jsonify(SystemConfig.get_default_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
