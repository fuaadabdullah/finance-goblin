import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from pathlib import Path

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="🧟 Finance Goblin", layout="wide")
st.title("🧟 Finance Goblin")
st.markdown("📊 **Data-Driven Insights** – Upload your bank CSV and uncover spending patterns with statistical precision.")

# ------------------------------
# SAMPLE DATA GENERATOR (in-memory)
# ------------------------------
SAMPLE_DATA_PATH = Path("sample_data.csv")


def generate_sample_df(num_rows=45):
    """Fallback sample data if sample_data.csv is unavailable."""
    np.random.seed(42)
    random.seed(42)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)

    vendor_pool = {
        "Starbucks": (3, 15),
        "Walmart": (20, 150),
        "Uber": (8, 35),
        "Electric Co.": (60, 120),
        "Amazon": (10, 200),
        "Netflix": (15, 15),
        "Spotify": (10, 10),
        "Shell Gas": (25, 60),
        "DoorDash": (15, 45),
        "McDonald's": (8, 20),
        "CVS Pharmacy": (5, 40),
        "Trader Joe's": (30, 90),
        "Target": (15, 80),
        "Lyft": (9, 30),
        "Comcast": (70, 100),
        "Rent Payment": (1200, 1800),
        "Venmo Transfer": (20, 100),
        "Best Buy": (50, 300),
        "Apple": (1, 50),
        "Chevron": (20, 70),
        "Chipotle": (10, 18),
        "AMC Theatres": (15, 30),
        "United Airlines": (150, 400),
        "Airbnb": (80, 250),
        "Steam Games": (5, 60),
        "Etsy": (10, 50),
        "Zelle Payment": (30, 200),
        "Planet Fitness": (10, 25),
        "Doctor Visit": (25, 100),
        "Whole Foods": (20, 70),
    }

    vendors = list(vendor_pool.keys())
    weights = [5, 6, 4, 2, 8, 1, 1, 3, 4, 3, 3, 3, 4, 3, 1, 1, 2, 1, 1, 2, 3, 1, 1, 1, 2, 2, 2, 1, 1, 2]

    data = []
    for _ in range(num_rows):
        vendor = random.choices(vendors, weights=weights, k=1)[0]
        min_amt, max_amt = vendor_pool[vendor]
        amount = -round(random.uniform(min_amt, max_amt), 2)  # negative for expense

        days_ago = int(np.random.triangular(0, 90, 30))
        trans_date = end_date - timedelta(days=days_ago)

        if random.random() < 0.2:
            description = f"{vendor} #{random.randint(1000,9999)}"
        else:
            description = vendor

        data.append([trans_date.strftime("%m/%d/%Y"), description, amount])

    df = pd.DataFrame(data, columns=["Date", "Description", "Amount"])
    df = df.sort_values("Date", ascending=False).reset_index(drop=True)
    return df


def load_sample_df():
    """Load committed sample_data.csv; fallback to generated sample if missing."""
    if SAMPLE_DATA_PATH.exists():
        return pd.read_csv(SAMPLE_DATA_PATH)
    return generate_sample_df()


def get_sample_csv_bytes(sample_df):
    """Return CSV bytes for download while preserving committed file content."""
    if SAMPLE_DATA_PATH.exists():
        return SAMPLE_DATA_PATH.read_bytes()
    return sample_df.to_csv(index=False).encode("utf-8")


def find_default_column(columns, candidates, fallback_index=0):
    """Pick the first matching column name from candidates, else fallback index."""
    lowered = {col.lower(): col for col in columns}
    for name in candidates:
        if name in lowered:
            return columns.index(lowered[name])
    if not columns:
        return 0
    return min(fallback_index, len(columns) - 1)

# ------------------------------
# CATEGORIZATION RULES
# ------------------------------
CATEGORY_RULES = {
    "🍔 Food & Dining": ["restaurant", "cafe", "doordash", "ubereats", "grubhub", "mcdonald", "starbucks", "taco", "pizza", "chipotle", "dining"],
    "🚗 Transport": ["uber", "lyft", "gas", "shell", "exxon", "chevron", "parking", "metro", "transit", "united airlines"],
    "🛒 Groceries": ["walmart", "target", "costco", "safeway", "kroger", "trader joe", "whole foods"],
    "🎮 Entertainment": ["netflix", "spotify", "hulu", "amazon prime", "cinema", "concert", "steam", "amc theatres"],
    "🏠 Rent & Utilities": ["rent", "electric", "water", "internet", "comcast", "at&t", "utility"],
    "💊 Health": ["pharmacy", "cvs", "walgreens", "doctor", "medical", "dentist", "fitness"],
    "📦 Shopping": ["amazon", "etsy", "ebay", "best buy", "nike", "adidas", "apple"],
    "💰 Transfer": ["transfer", "zelle", "venmo", "paypal"],
    "🏦 Bank Fee": ["fee", "service charge", "overdraft"],
    "✈️ Travel": ["airbnb", "hotel", "flight", "united airlines"],
    "📌 Other": [],
}


def categorize(description):
    desc_lower = str(description).lower()
    for cat, keywords in CATEGORY_RULES.items():
        if cat == "📌 Other":
            continue
        if any(kw in desc_lower for kw in keywords):
            return cat
    return "📌 Other"


# ------------------------------
# DATA CLEANING & STANDARDIZATION
# ------------------------------
def clean_and_categorize(
    df,
    date_col,
    desc_col,
    amount_col=None,
    credit_col=None,
    debit_col=None,
    invert_sign=False,
):
    """Convert to standard columns, clean, and add Category."""
    df_clean = pd.DataFrame()
    df_clean["Date"] = pd.to_datetime(df[date_col], errors="coerce")
    df_clean["Description"] = df[desc_col].astype(str)

    if amount_col is not None:
        df_clean["Amount"] = pd.to_numeric(df[amount_col], errors="coerce")
    else:
        credits = pd.to_numeric(df[credit_col], errors="coerce").fillna(0).abs()
        debits = pd.to_numeric(df[debit_col], errors="coerce").fillna(0).abs()
        df_clean["Amount"] = credits - debits

    if invert_sign:
        df_clean["Amount"] = df_clean["Amount"] * -1

    # Drop invalid rows
    df_clean = df_clean.dropna(subset=["Date", "Amount"])

    # Categorize
    df_clean["Category"] = df_clean["Description"].apply(categorize)

    return df_clean


# ------------------------------
# SIDEBAR - UPLOAD & SAMPLE
# ------------------------------
st.sidebar.header("📂 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload your bank CSV", type=["csv"])
st.sidebar.caption("Supported: Date, Description, Amount OR Date, Description, Credit, Debit")

# Sample download button
sample_df = load_sample_df()
sample_csv = get_sample_csv_bytes(sample_df)
st.sidebar.download_button(
    label="📥 Download Sample CSV",
    data=sample_csv,
    file_name="sample_data.csv",
    mime="text/csv",
    help="Realistic demo dataset (~3 months of transactions).",
)

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        raw_df = pd.read_csv(uploaded_file, encoding="latin1")

    st.sidebar.success(f"Loaded {len(raw_df)} rows")

    # Column mapping
    columns = raw_df.columns.tolist()
    date_col = st.sidebar.selectbox(
        "Date column",
        columns,
        index=find_default_column(columns, ["date", "transaction date"], fallback_index=0),
    )
    desc_col = st.sidebar.selectbox(
        "Description column",
        columns,
        index=find_default_column(columns, ["description", "merchant", "memo", "details"], fallback_index=1),
    )
    has_credit_debit = "credit" in {c.lower() for c in columns} and "debit" in {c.lower() for c in columns}
    parse_mode = st.sidebar.radio(
        "CSV layout",
        options=["3-column (Amount)", "4-column (Credit/Debit)"],
        index=1 if has_credit_debit else 0,
    )

    amount_col = None
    credit_col = None
    debit_col = None

    if parse_mode == "3-column (Amount)":
        amount_col = st.sidebar.selectbox(
            "Amount column",
            columns,
            index=find_default_column(columns, ["amount", "transaction amount"], fallback_index=2),
        )
    else:
        credit_col = st.sidebar.selectbox(
            "Credit column",
            columns,
            index=find_default_column(columns, ["credit", "credits", "deposit"], fallback_index=2),
        )
        debit_col = st.sidebar.selectbox(
            "Debit column",
            columns,
            index=find_default_column(columns, ["debit", "debits", "withdrawal"], fallback_index=3),
        )

    invert_sign = st.sidebar.checkbox("Invert sign (if expenses are negative)", value=False)

    df = clean_and_categorize(
        raw_df,
        date_col,
        desc_col,
        amount_col=amount_col,
        credit_col=credit_col,
        debit_col=debit_col,
        invert_sign=invert_sign,
    )
    st.session_state["df"] = df
else:
    # Use sample data as default
    df = clean_and_categorize(sample_df, "Date", "Description", amount_col="Amount", invert_sign=False)
    st.session_state["df"] = df
    st.sidebar.info("Using sample_data.csv by default. Upload your own CSV to replace.")

# ------------------------------
# MAIN DASHBOARD
# ------------------------------
df = st.session_state["df"]

if df.empty:
    st.warning("No data available. Please upload a CSV or download the sample.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔍 Filters")
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", [min_date, max_date])

categories = sorted(df["Category"].unique())
selected_cats = st.sidebar.multiselect("Categories", categories, default=categories)

# Apply filters
if len(date_range) == 2:
    mask = (df["Date"].dt.date >= date_range[0]) & (df["Date"].dt.date <= date_range[1])
    df_filtered = df[mask]
else:
    df_filtered = df

df_filtered = df_filtered[df_filtered["Category"].isin(selected_cats)]

if df_filtered.empty:
    st.warning("No transactions match the selected filters.")
    st.stop()

# ------------------------------
# METRICS
# ------------------------------
total_spent = df_filtered["Amount"].sum()  # negative sum
total_spent_abs = abs(total_spent)
avg_transaction = df_filtered["Amount"].mean()
num_transactions = len(df_filtered)

col1, col2, col3 = st.columns(3)
col1.metric("💸 Total Spent", f"${total_spent_abs:,.2f}")
col2.metric("📊 Avg Transaction", f"${abs(avg_transaction):,.2f}")
col3.metric("🔢 Transactions", num_transactions)

# ------------------------------
# CHARTS
# ------------------------------
st.subheader("📈 Spending Analysis")

# 1. Monthly bar chart
df_filtered["Month"] = df_filtered["Date"].dt.to_period("M").astype(str)
monthly = df_filtered.groupby("Month")["Amount"].sum().reset_index()
monthly["Amount"] = monthly["Amount"].abs()  # positive for bar
fig_monthly = px.bar(
    monthly,
    x="Month",
    y="Amount",
    title="Monthly Spending",
    labels={"Amount": "Total Spent ($)", "Month": ""},
    color_discrete_sequence=["#1e3a5f"],  # Navy blue for trust & stability
)
fig_monthly.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
st.plotly_chart(fig_monthly, use_container_width=True)

# 2. Category pie chart
cat_sum = df_filtered.groupby("Category")["Amount"].sum().reset_index()
cat_sum["Amount"] = cat_sum["Amount"].abs()
# Professional financial color palette: navy, teal, coral, and professional grays
financial_colors = ["#1e3a5f", "#00a699", "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#34495e", "#e91e63", "#00bcd4"]
fig_pie = px.pie(
    cat_sum,
    values="Amount",
    names="Category",
    title="Spending by Category",
    hole=0.4,
    color_discrete_sequence=financial_colors,
)
fig_pie.update_traces(textposition="inside", textinfo="percent+label")
fig_pie.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
st.plotly_chart(fig_pie, use_container_width=True)

# 3. Daily spending trend (line)
daily = df_filtered.groupby(df_filtered["Date"].dt.date)["Amount"].sum().reset_index()
daily["Amount"] = daily["Amount"].abs()
fig_line = px.line(
    daily,
    x="Date",
    y="Amount",
    title="Daily Spending Trend",
    labels={"Amount": "Spent ($)", "Date": ""},
    color_discrete_sequence=["#00a699"],  # Teal for trend monitoring
)
fig_line.update_traces(line=dict(width=2.5))
fig_line.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12), hovermode="x unified")
st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------
# DATA TABLE
# ------------------------------
st.subheader("📋 Transaction Details")
with st.expander("View / search transactions", expanded=False):
    search = st.text_input("Search descriptions")
    if search:
        display_df = df_filtered[df_filtered["Description"].str.contains(search, case=False, na=False)]
    else:
        display_df = df_filtered

    st.dataframe(
        display_df[["Date", "Description", "Category", "Amount"]].sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn(format="$%.2f")},
    )

# ------------------------------
# DOWNLOAD TAGGED CSV
# ------------------------------
tagged_csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Tagged CSV",
    data=tagged_csv,
    file_name="tagged_expenses.csv",
    mime="text/csv",
)

# Footer
st.markdown("---")
st.caption("🧟 **Finance Goblin** – Built with Streamlit, Pandas & Plotly. Your data stays in your browser. No fees. No BS.")
