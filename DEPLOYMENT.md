# 🚀 Finance Goblin — Deployment Guide

This guide walks you through deploying **Finance Goblin** to Streamlit Cloud for a live, publicly accessible demo.

---

## Phase 1: GitHub Setup (5 minutes)

### Step 1.1: Create GitHub Repository

1. Visit [github.com/new](https://github.com/new)
2. **Repository name**: `finance-goblin`
3. **Description**: *Data-driven expense tracker dashboard with Streamlit*
4. **Visibility**: Public (so Streamlit Cloud can access it)
5. **Initialize repo**: Leave unchecked (we already have commits locally)
6. Click **Create repository**

### Step 1.2: Connect Local Repository to GitHub

After creating the GitHub repo, run these commands:

```bash
cd /home/fuaadabdullah/personal-finance-dashboard

# Add GitHub remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/finance-goblin.git

# Verify remote is connected
git remote -v

# Push to GitHub
git push -u origin main
```

**Expected output:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
...
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

If you see a **credential prompt**:
- Use your GitHub username
- For password, use a **Personal Access Token** (PAT):
  1. Go to GitHub → Settings → Developer settings → Personal access tokens
  2. Click "Tokens (classic)" → "Generate new token"
  3. Select scopes: `repo`, `workflow`
  4. Copy token and paste when prompted

---

## Phase 2: Streamlit Cloud Deployment (3 minutes)

### Step 2.1: Sign In to Streamlit Cloud

1. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit to access your GitHub account
4. You'll be redirected to your Streamlit Cloud dashboard

### Step 2.2: Deploy App

1. Click **"New app"** button
2. Fill in deployment details:
   - **Repository**: `YOUR_USERNAME/finance-goblin`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. Click **"Deploy!"**

**What happens next:**
- Streamlit downloads your repo
- Installs dependencies from `requirements.txt`
- Launches your app
- Provides a **public URL** (e.g., `https://finance-goblin-YOUR_USERNAME.streamlit.app`)

⏳ **Deployment takes ~2-3 minutes** on first deploy.

### Step 2.3: Verify Live App

Once deployment is complete:
1. Copy the public URL from Streamlit Cloud
2. Open in browser
3. Test features:
   - Download sample CSV button
   - Upload the sample CSV
   - Filter by date and category
   - Check all 3 charts render
   - Search transactions
   - Download tagged CSV

✅ **If all features work → Deployment successful!**

---

## Phase 3: Share & Demo

### Update README with Live URL

Edit [README.md](README.md) and update this line:

```markdown
**Live Demo:** [https://finance-goblin-YOUR_USERNAME.streamlit.app](https://finance-goblin-YOUR_USERNAME.streamlit.app)
```

Then push:
```bash
git add README.md
git commit -m "docs: add live Streamlit Cloud URL"
git push
```

### 30-Second Demo Script

Use this in interviews:

> *"This is **Finance Goblin**, my data-driven expense tracker. Built with Python—Streamlit for the UI, Pandas for data processing, and Plotly for interactive charts.*
>
> *Users upload a bank CSV file, and the app automatically categorizes transactions into 10 spending categories using keyword matching. It shows three key visualizations: monthly spending trends, a breakdown by category, and daily spending patterns.*
>
> *All data stays in the browser—no backend servers, no data collection. It's stateless; once you close the tab, data is gone. Built to demonstrate data engineering, visualization, and financial analytics skills.*
>
> *Let me show you: [upload demo CSV] → categorize → filter → instant insights."*

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| GitHub auth fails | Use a Personal Access Token (see Step 1.2) |
| Streamlit Cloud can't find repo | Verify repository is Public, not Private |
| App crashes on deploy | Check `requirements.txt` for missing packages |
| Charts don't render | Verify Plotly version in `requirements.txt` ≥ 5.17 |
| Sample CSV download fails | Ensure `sample_data.csv` is in repo root |

---

## Auto-Redeployment

**Good news:** Streamlit Cloud automatically redeploys whenever you push to GitHub:

```bash
# Make a change to app.py
nano app.py

# Commit and push
git add app.py
git commit -m "feature: add new chart"
git push origin main

# Within ~1-2 minutes, live app updates automatically ✨
```

---

## Next Steps

1. ✅ Create GitHub repo → Deploy to Streamlit Cloud
2. 📱 Share live URL with recruiters / in your portfolio
3. 🎯 Use as conversation starter in interviews
4. 🔄 Iterate: add new features, push updates, auto-deploy

---

## Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Cloud Docs**: [docs.streamlit.io/deploy/streamlit-cloud](https://docs.streamlit.io/deploy/streamlit-cloud)
- **GitHub Personal Tokens**: [github.com/settings/tokens](https://github.com/settings/tokens)
- **Plotly Chart Reference**: [plotly.com/python](https://plotly.com/python)

---

## Credit & License

- **Author**: Fuaad Abdullah
- **License**: MIT License (see [LICENSE](LICENSE))

---

**Questions?** Feel free to debug locally with `streamlit run app.py` or check Streamlit Cloud logs in the dashboard.

Happy deploying! 🚀🧟
