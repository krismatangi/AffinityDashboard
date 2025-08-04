from datetime import datetime
from sqlalchemy import text

def init_config_db(database):
    """Initialize the configuration database"""
    try:
        # Create system_config table
        database.session.execute(text("""
            CREATE TABLE IF NOT EXISTS system_config (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value VARCHAR(200) NOT NULL,
                updated_by VARCHAR(100) DEFAULT 'System',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        database.session.commit()
        
        # Insert default configuration if not exists
        default_config = SystemConfig.get_default_config()
        for key, value in default_config.items():
            try:
                database.session.execute(text("""
                    INSERT INTO system_config (config_key, config_value, updated_by)
                    VALUES (:key, :value, 'System')
                    ON CONFLICT (config_key) DO NOTHING
                """), {'key': key, 'value': str(value)})
                database.session.commit()
            except Exception as e:
                database.session.rollback()
                print(f"Error inserting default config {key}: {e}")
        
        print("Configuration database initialized successfully")
    except Exception as e:
        database.session.rollback()
        print(f"Error creating config tables: {e}")

class SystemConfig:
    @staticmethod
    def get_config():
        """Get current system configuration"""
        from app import db
        try:
            results = db.session.execute(text("""
                SELECT config_key, config_value 
                FROM system_config
            """)).fetchall()
            
            config = {}
            for key, value in results:
                # Convert string values back to appropriate types
                try:
                    config[key] = int(value)
                except ValueError:
                    config[key] = value
            
            # Ensure all default keys exist
            default_config = SystemConfig.get_default_config()
            for key, default_value in default_config.items():
                if key not in config:
                    config[key] = default_value
            
            return config
        except Exception as e:
            print(f"Error getting config: {e}")
            return SystemConfig.get_default_config()
    
    @staticmethod
    def get_default_config():
        """Get default configuration values"""
        return {
            # MRI configuration
            'mri_radcon5_threshold': 5,
            'mri_radcon3_threshold': 15,
            'mri_radcon1_threshold': 30,
            'mri_processing_rate': 20,
            
            # CT configuration
            'ct_radcon5_threshold': 5,
            'ct_radcon3_threshold': 15,
            'ct_radcon1_threshold': 30,
            'ct_processing_rate': 30,
            
            # X-Ray configuration
            'xray_radcon5_threshold': 10,
            'xray_radcon3_threshold': 25,
            'xray_radcon1_threshold': 50,
            'xray_processing_rate': 50,
            
            # Nuclear Medicine configuration
            'nucmed_radcon5_threshold': 3,
            'nucmed_radcon3_threshold': 8,
            'nucmed_radcon1_threshold': 15,
            'nucmed_processing_rate': 15,
            
            # Ultrasound configuration
            'ultrasound_radcon5_threshold': 12,
            'ultrasound_radcon3_threshold': 30,
            'ultrasound_radcon1_threshold': 60,
            'ultrasound_processing_rate': 25
        }
    
    @staticmethod
    def update_config(config_data, admin_name=None):
        """Update system configuration"""
        from app import db
        try:
            admin_name = admin_name or 'Admin'
            
            for key, value in config_data.items():
                db.session.execute(text("""
                    INSERT INTO system_config (config_key, config_value, updated_by, timestamp)
                    VALUES (:key, :value, :admin_name, :timestamp)
                    ON CONFLICT (config_key) 
                    DO UPDATE SET 
                        config_value = EXCLUDED.config_value,
                        updated_by = EXCLUDED.updated_by,
                        timestamp = EXCLUDED.timestamp
                """), {
                    'key': key,
                    'value': str(value),
                    'admin_name': admin_name,
                    'timestamp': datetime.now()
                })
            
            db.session.commit()
            print(f"Configuration updated by {admin_name}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating config: {e}")
            return False