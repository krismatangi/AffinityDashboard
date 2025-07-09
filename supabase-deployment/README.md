# Affinity Medical Imaging Dashboard - Supabase Deployment

This is the Supabase deployment version of the Affinity Medical Imaging Status Dashboard. This version provides permanent free hosting with no database expiration.

## Features

- **Medical Imaging Dashboard**: Track unreported cases across 5 modalities (MRI, CT, X-Ray, Nuclear Medicine, Ultrasound)
- **Radcon Level System**: 5-level criticality scale (5=normal, 1=critical)
- **Real-time Updates**: Shared database ensures all viewers see the same data
- **Admin Interface**: Secure login for case volume management and system configuration
- **Professional Design**: Affinity brand colors with responsive mobile-friendly layout

## Quick Deployment Guide

### Step 1: Set Up Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Click "New Project"
3. Choose your organization and fill in:
   - **Project Name**: `affinity-dashboard`
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait for the project to initialize (takes ~2 minutes)

### Step 2: Get Database Connection String

1. In your Supabase project dashboard, click "Settings" in the sidebar
2. Click "Database"
3. Scroll down to "Connection string"
4. Copy the "URI" connection string (starts with `postgresql://`)
5. Replace `[YOUR-PASSWORD]` with the database password you created

Example:
```
postgresql://postgres:your-password@db.abcdefghijk.supabase.co:5432/postgres
```

### Step 3: Deploy to Render

1. Upload all files to a GitHub repository
2. Go to [render.com](https://render.com) and sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure the service:
   - **Name**: `affinity-dashboard`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`

### Step 4: Set Environment Variables

In Render, go to "Environment" tab and add:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Your Supabase connection string |
| `ADMIN_USERNAME` | `admin` (or your preferred username) |
| `ADMIN_PASSWORD` | Your secure admin password |
| `SESSION_SECRET` | Random string (e.g., `your-secret-key-here`) |

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your dashboard will be live at the Render URL

## Admin Access

- **URL**: `https://your-app.onrender.com/login`
- **Username**: Value you set for `ADMIN_USERNAME`
- **Password**: Value you set for `ADMIN_PASSWORD`

## Database Tables

The application automatically creates these tables:

1. **case_volumes**: Stores case counts for each modality
2. **system_config**: Stores configurable thresholds and processing rates

## API Endpoints

- `GET /api/volumes` - Get current case volumes
- `GET /api/config` - Get system configuration

## Benefits of Supabase

✅ **Free Forever**: No 90-day expiration like Render PostgreSQL  
✅ **500MB Storage**: More than enough for dashboard data  
✅ **High Availability**: Built on AWS with 99.9% uptime  
✅ **Automatic Backups**: Daily backups included  
✅ **Real-time**: Perfect for shared dashboard functionality  

## Support

For issues with deployment or configuration, check:
1. Render build logs for deployment errors
2. Supabase dashboard for database connectivity
3. Environment variables are correctly set

The dashboard automatically initializes all required database tables on first run.