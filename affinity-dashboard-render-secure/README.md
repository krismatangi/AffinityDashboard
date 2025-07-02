# Affinity Medical Imaging Status Dashboard - Flask Version

A professional medical imaging dashboard application that tracks unreported cases across five imaging modalities (MRI, CT, X-Ray, Nuclear Medicine, and Ultrasound) with real-time status monitoring and Radcon level criticality system.

## Features

- **Real-time Data Sharing**: PostgreSQL database ensures all viewers see the same data
- **5 Imaging Modalities**: MRI, CT, X-Ray, Nuclear Medicine, and Ultrasound
- **Radcon Level System**: 5-level criticality scale (5=normal, 1=critical)
- **Admin Interface**: Password-protected case volume management
- **Professional Design**: Affinity brand colors with responsive layout
- **Automatic Calculations**: Turnaround time estimates and status indicators

## Deployment

### Environment Variables Required

```
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=your-secure-session-secret-here
```

### For Heroku Deployment

1. Create a new Heroku app
2. Add PostgreSQL addon: `heroku addons:create heroku-postgresql:mini`
3. Set session secret: `heroku config:set SESSION_SECRET="your-secure-key"`
4. Deploy this code

### For Railway/Render Deployment

1. Connect your repository
2. Add PostgreSQL database service
3. Set environment variables:
   - `DATABASE_URL` (from database service)
   - `SESSION_SECRET` (generate secure random string)

### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables in `.env` file
3. Run: `python main.py`

## Admin Access

- **URL**: `/admin`
- **Username**: `admin`
- **Password**: `!Aff1n1ty#`

## Configuration

Access system configuration at `/admin/config` to adjust:
- Case count thresholds for each modality
- Processing rates for turnaround calculations
- Radcon level thresholds

## Technical Details

- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with connection pooling
- **Authentication**: Session-based with SHA256 password hashing
- **Frontend**: Bootstrap 5 with responsive design
- **Deployment**: Gunicorn WSGI server