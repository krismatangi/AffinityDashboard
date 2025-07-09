from datetime import datetime
from sqlalchemy import text

def init_db(database):
    """Initialize the database with required tables"""
    try:
        # Create case_volumes table
        database.session.execute(text("""
            CREATE TABLE IF NOT EXISTS case_volumes (
                id SERIAL PRIMARY KEY,
                mri INTEGER DEFAULT 0,
                ct INTEGER DEFAULT 0,
                xray INTEGER DEFAULT 0,
                nucmed INTEGER DEFAULT 0,
                ultrasound INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by VARCHAR(100) DEFAULT 'System'
            )
        """))
        
        database.session.commit()
        print("Database tables created successfully")
    except Exception as e:
        database.session.rollback()
        print(f"Error creating tables: {e}")

class CaseVolume:
    def __init__(self, database):
        self.db = database
    
    @staticmethod
    def get_current_volumes():
        """Get the most recent case volume entry from database"""
        from app import db
        try:
            result = db.session.execute(text("""
                SELECT mri, ct, xray, nucmed, ultrasound, timestamp, updated_by 
                FROM case_volumes 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)).fetchone()
            
            if result:
                return {
                    'mri': result[0],
                    'ct': result[1], 
                    'xray': result[2],
                    'nucmed': result[3],
                    'ultrasound': result[4],
                    'timestamp': result[5],
                    'updated_by': result[6]
                }
            return None
        except Exception as e:
            print(f"Error getting current volumes: {e}")
            return None
    
    @staticmethod
    def update_volumes(mri=0, ct=0, xray=0, nucmed=0, ultrasound=0, admin_name=None):
        """Create a new case volume entry"""
        from app import db
        try:
            admin_name = admin_name or 'Admin'
            
            db.session.execute(text("""
                INSERT INTO case_volumes (mri, ct, xray, nucmed, ultrasound, updated_by, timestamp)
                VALUES (:mri, :ct, :xray, :nucmed, :ultrasound, :admin_name, :timestamp)
            """), {
                'mri': mri,
                'ct': ct,
                'xray': xray,
                'nucmed': nucmed,
                'ultrasound': ultrasound,
                'admin_name': admin_name,
                'timestamp': datetime.now()
            })
            
            db.session.commit()
            print(f"Volumes updated: MRI={mri}, CT={ct}, X-Ray={xray}, NucMed={nucmed}, Ultrasound={ultrasound}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating volumes: {e}")
            return False