from datetime import datetime

# Will be set when app initializes
db = None

def init_config_db(database):
    global db
    db = database

class SystemConfig:
    @staticmethod
    def get_config():
        """Get current system configuration"""
        if not db:
            return None
        
        result = db.session.execute(
            db.text("SELECT * FROM system_config ORDER BY updated_at DESC LIMIT 1")
        ).fetchone()
        
        if result:
            return {
                'id': result[0],
                'mri_yellow': result[1],
                'mri_orange': result[2],
                'mri_red': result[3],
                'ct_yellow': result[4],
                'ct_orange': result[5],
                'ct_red': result[6],
                'xray_yellow': result[7],
                'xray_orange': result[8],
                'xray_red': result[9],
                'nucmed_yellow': result[10],
                'nucmed_orange': result[11],
                'nucmed_red': result[12],
                'mri_rate': result[13],
                'ct_rate': result[14],
                'xray_rate': result[15],
                'nucmed_rate': result[16],
                'radcon_4_threshold': result[17],
                'radcon_3_threshold': result[18],
                'radcon_2_threshold': result[19],
                'updated_at': result[20],
                'updated_by': result[21]
            }
        return None
    
    @staticmethod
    def get_default_config():
        """Get default configuration values"""
        return {
            'mri_yellow': 10,
            'mri_orange': 25,
            'mri_red': 50,
            'ct_yellow': 15,
            'ct_orange': 35,
            'ct_red': 70,
            'xray_yellow': 25,
            'xray_orange': 60,
            'xray_red': 120,
            'nucmed_yellow': 8,
            'nucmed_orange': 20,
            'nucmed_red': 40,
            'ultrasound_yellow': 12,
            'ultrasound_orange': 30,
            'ultrasound_red': 60,
            'mri_rate': 8,
            'ct_rate': 12,
            'xray_rate': 20,
            'nucmed_rate': 6,
            'ultrasound_rate': 10,
            'radcon_4_threshold': 30,
            'radcon_3_threshold': 60,
            'radcon_2_threshold': 100
        }
    
    @staticmethod
    def update_config(config_data, admin_name=None):
        """Update system configuration"""
        if not db:
            return None
        
        db.session.execute(
            db.text("""
                INSERT INTO system_config (
                    mri_yellow, mri_orange, mri_red,
                    ct_yellow, ct_orange, ct_red,
                    xray_yellow, xray_orange, xray_red,
                    nucmed_yellow, nucmed_orange, nucmed_red,
                    mri_rate, ct_rate, xray_rate, nucmed_rate,
                    radcon_4_threshold, radcon_3_threshold, radcon_2_threshold,
                    updated_at, updated_by
                ) VALUES (
                    :mri_yellow, :mri_orange, :mri_red,
                    :ct_yellow, :ct_orange, :ct_red,
                    :xray_yellow, :xray_orange, :xray_red,
                    :nucmed_yellow, :nucmed_orange, :nucmed_red,
                    :mri_rate, :ct_rate, :xray_rate, :nucmed_rate,
                    :radcon_4_threshold, :radcon_3_threshold, :radcon_2_threshold,
                    :updated_at, :admin_name
                )
            """),
            {
                **config_data,
                'updated_at': datetime.utcnow(),
                'admin_name': admin_name
            }
        )
        db.session.commit()
        return True