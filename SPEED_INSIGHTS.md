# Vercel Speed Insights Integration

This project now includes Vercel Speed Insights to track performance metrics for the Pi MR-NFT Agent dashboard.

## What was added

### 1. HTML Templates with Speed Insights

Created `app/templates/` directory with:
- `base.html` - Base template with Speed Insights script included
- `index.html` - Dashboard page that extends the base template

The Speed Insights tracking script is included in `base.html`:

```html
<!-- Vercel Speed Insights -->
<script>
    window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
```

### 2. Updated FastAPI Application

Modified `app/main.py` to:
- Import Jinja2Templates for HTML rendering
- Configure template directory
- Add root endpoint (`/`) that displays an HTML dashboard with Speed Insights enabled
- Maintain all existing API endpoints

### 3. Updated Dependencies

Added to `requirements.txt`:
- `jinja2>=3.1.2` - Required for HTML template rendering in FastAPI

### 4. Vercel Configuration

Created `vercel.json` to configure deployment settings for Python/FastAPI on Vercel.

## How to Enable Speed Insights

### Step 1: Enable in Vercel Dashboard

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project (pi-mr-nft-agent)
3. Navigate to the **Speed Insights** tab
4. Click **Enable**

> **Note:** Enabling Speed Insights will add new routes (scoped at `/_vercel/speed-insights/*`) after your next deployment.

### Step 2: Deploy to Vercel

Deploy your application to Vercel:

```bash
vercel deploy
```

Or connect your GitHub repository to enable automatic deployments.

### Step 3: View Your Data

Once deployed and users visit your site:

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Click the **Speed Insights** tab
4. View performance metrics after a few days of traffic

## What Gets Tracked

Speed Insights automatically tracks:
- **First Contentful Paint (FCP)** - Time until first content renders
- **Largest Contentful Paint (LCP)** - Time until largest content element renders
- **First Input Delay (FID)** - Time until page responds to first user interaction
- **Cumulative Layout Shift (CLS)** - Visual stability score
- **Time to First Byte (TTFB)** - Server response time

## Dashboard Features

The new HTML dashboard at the root URL (`/`) displays:
- Service status and version
- Catalyst Pool status (capacity, multiplier, inferences)
- Maintainer information (GitHub handle, reputation score, phase)
- Quick links to API endpoints
- Links to documentation

All JSON API endpoints remain unchanged:
- `/health` - Health check
- `/catalyst/status` - Catalyst pool data
- `/models` - Model list
- `/maintainer/status` - Maintainer info
- `/docs` - FastAPI automatic documentation

## Testing Locally

To test the integration locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app/main.py
   ```

3. Visit http://localhost:8000 to see the dashboard

> **Note:** The Speed Insights script will only load properly when deployed to Vercel. Locally, the script tag will be present but won't track metrics.

## Privacy and Compliance

Vercel Speed Insights is compliant with privacy regulations. Learn more:
- [Speed Insights Privacy Policy](https://vercel.com/docs/speed-insights/privacy-policy)
- [Metrics Documentation](https://vercel.com/docs/speed-insights/metrics)

## Resources

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)
- [Speed Insights Package Documentation](https://vercel.com/docs/speed-insights/package)
- [Troubleshooting Guide](https://vercel.com/docs/speed-insights/troubleshooting)
- [Limits and Pricing](https://vercel.com/docs/speed-insights/limits-and-pricing)

## Compatibility

This implementation uses the HTML method for Speed Insights, which is framework-agnostic and works perfectly with FastAPI serving HTML templates. The script is loaded asynchronously and doesn't impact page load performance.
