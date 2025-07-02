# Render Deployment Guide - Affinity Dashboard (FREE FOREVER)

## 🆓 Completely Free Deployment

**Render Free Tier (Permanent):**
- Web service: Free forever
- PostgreSQL database: Free forever  
- 750 hours/month compute (31 days × 24 hours = 744 hours)
- Automatic SSL certificates
- Custom domain support

## 🚀 Quick Deploy (10 minutes)

1. **Create GitHub Repository**
   - Upload all files from this folder to GitHub
   - Make repository public (required for free tier)

2. **Create Database on Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (free)
   - Click "New" → "PostgreSQL"
   - Name: `affinity-dashboard-db`
   - Leave all defaults, click "Create Database"
   - **Copy the Internal Database URL** (starts with `postgresql://`)

3. **Deploy Web Service**
   - Click "New" → "Web Service"  
   - Connect your GitHub repository
   - Settings:
     - **Name**: `affinity-dashboard`
     - **Region**: Choose closest to your users
     - **Branch**: `main`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`

4. **Set Environment Variables**
   - In web service settings, add Environment Variables:
     - `DATABASE_URL` = (paste the Internal Database URL from step 2)
     - `SESSION_SECRET` = `your-secure-random-string-here`
     - `ADMIN_USERNAME` = `admin` (or your preferred username)
     - `ADMIN_PASSWORD` = `your-secure-password` (choose a strong password)

5. **Deploy**
   - Click "Create Web Service"
   - Render builds and deploys automatically
   - Your app will be live at `yourapp.onrender.com`

## ✅ Free Tier Limits
- **Compute**: 750 hours/month (enough for 24/7 operation)
- **Database**: 1GB storage, 100 connections
- **Bandwidth**: 100GB/month
- **Custom domains**: Supported
- **Auto-sleep**: Services sleep after 15min inactivity (wake on first request)

## 🔑 Admin Access
- **URL**: `yourapp.onrender.com/admin`
- **Username**: Whatever you set in `ADMIN_USERNAME` environment variable
- **Password**: Whatever you set in `ADMIN_PASSWORD` environment variable

## 📊 Perfect for Medical Dashboard
- All viewers see the same data instantly
- Admin updates sync across all users
- Professional design with Affinity branding
- Mobile responsive
- Automatic database backups

## 💡 Pro Tips
- Services may take 30-60 seconds to wake from sleep
- Database never sleeps (always available)
- Render automatically manages SSL certificates
- GitHub integration means easy updates