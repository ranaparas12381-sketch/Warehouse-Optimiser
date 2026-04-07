RENDER DEPLOYMENT QUICK START GUIDE

Your project is ready to deploy! Follow these steps to get your live demo URL.

STEP 1: GO TO RENDER

Open your web browser and navigate to:
https://render.com

Click "Get Started for Free" or "Sign In" if you already have an account.

STEP 2: SIGN UP OR LOG IN

You can sign up using:
- GitHub account (RECOMMENDED - makes connecting repository easier)
- GitLab account
- Email address

Choose GitHub for the easiest experience.

STEP 3: CREATE NEW WEB SERVICE

Once logged in:
1. Click the "New +" button in the top right corner
2. Select "Web Service" from the dropdown menu

STEP 4: CONNECT YOUR GITHUB REPOSITORY

You will see options to connect a repository:

Option A: If this is your first time
- Click "Connect account" next to GitHub
- Authorize Render to access your GitHub account
- You can choose to give access to all repositories or select specific ones

Option B: If already connected
- Click "Connect repository"
- Search for: Warehouse-Optimiser
- Click "Connect" next to your repository

Your repository URL: https://github.com/ranaparas12381-sketch/Warehouse-Optimiser

STEP 5: VERIFY AUTO CONFIGURATION

Render will automatically detect your render.yaml file and show:

Name: warehouse-optimization
Environment: Docker
Region: Oregon (US West) - or choose closest to you
Branch: main
Root Directory: (leave empty)

Important: Render will use the settings from your render.yaml file automatically!

STEP 6: REVIEW SETTINGS

Scroll down to review the auto-detected settings:

Docker Configuration:
- Dockerfile Path: ./warehouse_openenv/Dockerfile
- Docker Context: ./warehouse_openenv

Plan: Free (perfect for hackathon demo)

Health Check: /_stcore/health (already configured)

STEP 7: CREATE WEB SERVICE

Click the "Create Web Service" button at the bottom.

STEP 8: WAIT FOR DEPLOYMENT

Render will now:
1. Clone your repository
2. Build the Docker image (takes 3-5 minutes)
3. Install all Python dependencies
4. Start your Streamlit application
5. Run health checks

You will see a live build log showing:
- Building Docker image
- Installing requirements
- Starting Streamlit server
- Service is live

STEP 9: GET YOUR LIVE URL

Once deployment succeeds (status shows "Live"):

Your URL will be: https://warehouse-optimization-XXXX.onrender.com

Click the URL at the top of the page to open your live application!

STEP 10: TEST YOUR APPLICATION

1. Open the live URL in your browser
2. You should see the professional Warehouse Operations dashboard
3. Test it:
   - Select a Task Difficulty (Easy, Medium, or Hard)
   - Adjust the Random Seed if desired
   - Click "RUN SIMULATION"
   - Watch the KPI cards, charts, and logs populate

TROUBLESHOOTING

If build fails:
- Check the build logs for specific errors
- Verify your GitHub repository has all necessary files
- Make sure render.yaml is in the repository root

If application doesn't start:
- Check application logs in Render dashboard
- Verify health check is passing
- Look for any Python errors in the logs

If health check fails:
- Wait 1-2 minutes for Streamlit to fully initialize
- Refresh the Render dashboard
- Check that port 8501 is correctly exposed

IMPORTANT NOTES FOR FREE TIER

Your application on the free tier will:
- Spin down after 15 minutes of inactivity
- Take 30-60 seconds to spin up on first request after idle
- Have 750 hours per month of runtime
- Be perfect for hackathon demonstrations

Pro tip: Keep the tab open or refresh it during your presentation to avoid spin-up delay!

SHARING YOUR DEMO

For your hackathon submission:
1. Copy your live URL from Render
2. Test it in an incognito/private browser window
3. Share the URL in your hackathon submission
4. Add the URL to your GitHub README

Example URL to share:
https://warehouse-optimization-xxxx.onrender.com

UPDATING YOUR DEPLOYMENT

If you need to make changes:
1. Push updates to your GitHub repository
2. Render will automatically detect changes
3. New deployment will start automatically
4. Zero downtime updates

Or manually trigger:
1. Go to your service in Render dashboard
2. Click "Manual Deploy"
3. Select "Deploy latest commit"

MONITORING YOUR APPLICATION

In the Render dashboard you can:
- View real-time logs
- Monitor health check status
- See deployment history
- Check resource usage
- Configure custom domains (paid plans)

SUPPORT

If you encounter issues:
- Render documentation: https://render.com/docs
- Check build logs in Render dashboard
- Review application logs
- GitHub repository: https://github.com/ranaparas12381-sketch/Warehouse-Optimiser

