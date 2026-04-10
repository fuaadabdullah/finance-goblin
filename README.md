# 🧟 Finance Goblin

**Data-Driven Expense Insights** — Upload your bank/credit card CSV and uncover spending patterns with statistical precision. Finance Goblin auto-categorizes transactions, visualizes trends, and empowers you with real data-driven insights.

**Tech Stack:** Streamlit • Pandas • Plotly | **Data Privacy:** Your data stays in your browser. No servers, no cloud storage, no fees.

## 🚀 Quick Start

### Local Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/finance-goblin.git
   cd finance-goblin
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open your browser to `http://localhost:8501`

### 🌐 Cloud Deployment (Streamlit Cloud)

Deploy for free to Streamlit Cloud:

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **"New app"** → Select your repo, branch, and `app.py`
4. Streamlit automatically installs dependencies and deploys
5. Share the live URL!

**Live Demo:** https://finance-goblin-fuaadabdullah.streamlit.app

## 📊 Features

- **CSV Upload**: Supports 3-column (Date, Description, Amount) and 4-column (Date, Description, Credit, Debit) formats
- **Auto-Categorization**: 10 spending categories with smart keyword matching
- **Interactive Charts**: Monthly trends, spending by category (donut), daily spending line
- **Filters**: Date range and category multiselect for custom analysis
- **Search & Export**: Find transactions by description and download tagged CSV
- **Sample Data**: Pre-built demo data (~3 months of realistic transactions)

## Supported CSV Schemas

The uploader supports two common layouts.

### 1) Three-column format

Columns:

- `Date`
- `Description`
- `Amount`

Rules:

- `Date` should be parseable as a date (sample uses `MM/DD/YYYY`)
- `Amount` must be numeric
- Expenses are typically negative values (recommended)

Example:

```csv
Date,Description,Amount
04/07/2026,Amazon,-42.55
04/08/2026,Starbucks #9174,-7.25
```

### 2) Four-column format

Columns:

- `Date`
- `Description`
- `Credit`
- `Debit`

Rules:

- `Credit` and `Debit` must be numeric (blank values are treated as 0)
- The app converts to a single amount using: `Amount = Credit - Debit`
- This keeps debits as negative spending and credits as positive inflows

Example:

```csv
Date,Description,Credit,Debit
04/07/2026,Paycheck,1800.00,
04/08/2026,Electric Co.,,90.11
```

## 🤝 Contributing

Feel free to fork, improve, and submit pull requests. Contributions welcome!

## 👤 Credit

Created and maintained by **Fuaad Abdullah**.

## 📄 License

MIT License. See LICENSE file for details.

---

**Built with ❤️ by Fuaad Abdullah for data-driven financial insights.** Questions? Reach out or open an issue on GitHub.
