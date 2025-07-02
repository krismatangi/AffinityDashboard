from datetime import datetime

# Will be set when app initializes
db = None

def init_db(database):
    global db
    db = database

class CaseVolume:
    @staticmethod
    def get_current_volumes():
        """Get the most recent case volume entry from database"""
        if not db:
            return None
        
        result = db.session.execute(
            db.text("SELECT id, mri_cases, ct_cases, xray_cases, COALESCE(nucmed_cases, 0) as nucmed_cases, updated_at, updated_by FROM case_volumes ORDER BY updated_at DESC LIMIT 1")
        ).fetchone()
        
        if result:
            return {
                'id': result[0],
                'mri_cases': result[1],
                'ct_cases': result[2], 
                'xray_cases': result[3],
                'nucmed_cases': result[4],
                'updated_at': result[5],
                'updated_by': result[6]
            }
        return None
    
    @staticmethod
    def update_volumes(mri=0, ct=0, xray=0, nucmed=0, admin_name=None):
        """Create a new case volume entry"""
        if not db:
            return None
            
        db.session.execute(
            db.text("""
                INSERT INTO case_volumes (mri_cases, ct_cases, xray_cases, nucmed_cases, updated_at, updated_by)
                VALUES (:mri, :ct, :xray, :nucmed, :updated_at, :admin_name)
            """),
            {
                'mri': mri,
                'ct': ct,
                'xray': xray,
                'nucmed': nucmed,
                'updated_at': datetime.utcnow(),
                'admin_name': admin_name
            }
        )
        db.session.commit()
        return True