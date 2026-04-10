# Quick Start: GitHub & Deployment

## Your Next Steps (Copy-Paste Ready)

### 1️⃣ Create GitHub Repo
- Go to: https://github.com/new
- Name: `finance-goblin`
- Visibility: **Public**
- Click "Create repository"

### 2️⃣ Push to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username, then copy & paste:

```bash
cd /home/fuaadabdullah/personal-finance-dashboard
git remote add origin https://github.com/YOUR_USERNAME/finance-goblin.git
git push -u origin main
```

**If credential prompt appears:** Use your GitHub username + Personal Access Token (PAT)
- Get PAT: https://github.com/settings/tokens → Generate new token → Select `repo` scope

### 3️⃣ Deploy to Streamlit Cloud

1. Go to: https://streamlit.io/cloud
2. Click "Sign in with GitHub" (authorize Streamlit)
3. Click "New app"
4. Select: Repository: `finance-goblin` | Branch: `main` | File: `app.py`
5. Click "Deploy!"
6. Wait ~2 minutes for deployment

### 4️⃣ Your Live URL

Once deployed, you'll get: `https://finance-goblin-YOUR_USERNAME.streamlit.app`

**Test it:**
- Download sample CSV
- Upload it
- Check charts render
- Try filters & export

### 5️⃣ Update README

Edit `README.md` line and replace:
```
**Live Demo:** [Your Streamlit Cloud URL]
```

Then push:
```bash
git add README.md
git commit -m "docs: add live URL"
git push origin main
```

---

## 📊 Project Ready For Deployment

- ✅ App code: `app.py` (Finance Goblin with professional color palette)
- ✅ Dependencies: `requirements.txt` (Streamlit, Pandas, Plotly, openpyxl)
- ✅ Sample data: `sample_data.csv` (46 realistic transactions)
- ✅ Documentation: `README.md` (updated with branding)
- ✅ Git setup: `.git` folder initialized, branch = `main`
- ✅ Deployment guide: `DEPLOYMENT.md` (full instructions)
- ✅ .gitignore: Excludes venv, __pycache__, .streamlit, etc.

---

## 🎯 What You Get After Deployment

✨ **Public URL** that you can:
- Share in interviews
- Add to resume/portfolio
- Demo to recruiters
- Link on LinkedIn

⚡ **Auto-redeployment:**
- Push code → Changes live in ~1-2 minutes
- No manual deployment needed

📱 **Mobile-friendly:**
- Works on phone, tablet, desktop
- Professional UI
- Data-driven insights theme

---

## 💡 Demo Talk

*"Here's Finance Goblin, my data-driven expense tracker. Built with Python using Streamlit for the UI, Pandas for data wrangling, and Plotly for interactive visualizations. Upload a bank CSV—it auto-categorizes 10 spending types using keyword matching. Shows trends, patterns, and insights instantly. Zero backend servers—all data stays in your browser. Built to showcase data engineering, visualization, and financial analysis skills."*

---

**Status: Ready for GitHub push!** 🚀
