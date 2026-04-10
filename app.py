import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects
from datetime import datetime, timedelta
import re
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


def normalize_description_text(description):
    """Normalize merchant text for categorization and merchant grouping."""
    normalized = str(description).lower()
    normalized = normalized.replace("&", " and ")
    normalized = normalized.replace("'", "")
    normalized = normalized.replace("-", " ")
    normalized = re.sub(r"\b\d+\b", " ", normalized)
    normalized = re.sub(r"[^a-z\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


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

        data.append([trans_date, description, amount])

    df = pd.DataFrame(data, columns=["Date", "Description", "Amount"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values("Date", ascending=False).reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%m/%d/%Y")
    return df


@st.cache_data(show_spinner=False)
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


def parse_amount_series(series):
    """Parse amount-like strings (currency, commas, parentheses) to numeric."""
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"\$", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def detect_amount_sign_profile(series):
    """Return quick sign profile stats for user guidance."""
    amounts = parse_amount_series(series).dropna()
    if amounts.empty:
        return {"negative_ratio": 0.0, "positive_ratio": 0.0, "count": 0}

    negative_ratio = float((amounts < 0).mean())
    positive_ratio = float((amounts > 0).mean())
    return {
        "negative_ratio": negative_ratio,
        "positive_ratio": positive_ratio,
        "count": int(len(amounts)),
    }


def detect_credit_debit_profile(df, credit_col, debit_col):
    """Return sign profile stats for separate credit/debit columns."""
    credits = parse_amount_series(df[credit_col]).dropna()
    debits = parse_amount_series(df[debit_col]).dropna()
    credit_negative_ratio = float((credits < 0).mean()) if not credits.empty else 0.0
    debit_negative_ratio = float((debits < 0).mean()) if not debits.empty else 0.0
    return {
        "credit_negative_ratio": credit_negative_ratio,
        "debit_negative_ratio": debit_negative_ratio,
        "credit_count": int(len(credits)),
        "debit_count": int(len(debits)),
    }

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
    desc_lower = normalize_description_text(description)
    alias_map = {
        "mcd": "mcdonald",
        "mcds": "mcdonald",
        "mcdonalds": "mcdonald",
        "mcdonald s": "mcdonald",
        "wholefoods": "whole foods",
        "traderjoes": "trader joe",
        "amazon marketplace": "amazon",
        "apple com": "apple",
    }
    for alias, canonical in alias_map.items():
        if alias in desc_lower:
            desc_lower = desc_lower.replace(alias, canonical)
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
    """Convert to standard columns and normalize to canonical direction.

    Canonical format:
    - Expenses / outflows are negative
    - Income / inflows are positive
    """
    df_clean = pd.DataFrame()
    df_clean["Date"] = pd.to_datetime(df[date_col], errors="coerce")
    df_clean["Description"] = df[desc_col].astype(str)
    df_clean["Merchant"] = df_clean["Description"].apply(normalize_description_text)

    if amount_col is not None:
        df_clean["Amount"] = parse_amount_series(df[amount_col])
    else:
        credits = parse_amount_series(df[credit_col]).fillna(0).abs()
        debits = parse_amount_series(df[debit_col]).fillna(0).abs()
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

analysis_view = "Expenses only"

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

    analysis_view = st.sidebar.radio(
        "Analysis view",
        options=["Expenses only", "All transactions", "Income vs expenses"],
        index=0,
    )

    invert_sign = False

    if parse_mode == "3-column (Amount)" and amount_col is not None:
        sign_profile = detect_amount_sign_profile(raw_df[amount_col])
        if sign_profile["count"] > 0:
            if sign_profile["positive_ratio"] >= 0.95:
                invert_sign = True
                st.sidebar.info(
                    "Detected positive amounts. Treating them as expenses and flipping signs automatically."
                )
            elif sign_profile["negative_ratio"] >= 0.95:
                st.sidebar.info("Detected negative amounts. Using them as-is.")
            else:
                invert_sign = st.sidebar.checkbox(
                    "Treat positive amounts as expenses",
                    value=False,
                    help="Use this when your CSV stores outflows as positive numbers.",
                )
                if invert_sign:
                    st.sidebar.warning("Positive amounts will be treated as spending.")
    elif parse_mode == "4-column (Credit/Debit)" and credit_col is not None and debit_col is not None:
        st.sidebar.info("Credit/Debit layout detected. Debits are treated as negative automatically.")
        cd_profile = detect_credit_debit_profile(raw_df, credit_col, debit_col)
        if cd_profile["credit_negative_ratio"] > 0 or cd_profile["debit_negative_ratio"] > 0:
            st.sidebar.warning(
                "Credit/Debit columns contain signed values. "
                "They will be normalized to canonical direction during import."
            )

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

st.subheader("🧼 Cleaned Data Preview")
st.caption("Parsed columns after normalization so you can verify the import before exploring the dashboard.")
st.dataframe(
    df[["Date", "Description", "Merchant", "Category", "Amount"]].head(10),
    use_container_width=True,
    hide_index=True,
    column_config={"Amount": st.column_config.NumberColumn(format="$%.2f")},
)

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
expense_df = df_filtered[df_filtered["Amount"] < 0].copy()
income_df = df_filtered[df_filtered["Amount"] > 0].copy()

total_income = income_df["Amount"].sum()
total_expenses = expense_df["Amount"].abs().sum()
net_cash_flow = total_income - total_expenses
avg_expense = expense_df["Amount"].abs().mean() if not expense_df.empty else 0.0
num_transactions = len(df_filtered)

col1, col2, col3 = st.columns(3)
if analysis_view == "Expenses only":
    col1.metric("💸 Total Spent", f"${total_expenses:,.2f}")
    col2.metric("📊 Avg Expense", f"${avg_expense:,.2f}")
    col3.metric("🔢 Transactions", num_transactions)
else:
    col1.metric("💰 Total Income", f"${total_income:,.2f}")
    col2.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("🧾 Net Cash Flow", f"${net_cash_flow:,.2f}")

# ------------------------------
# CHARTS
# ------------------------------
st.subheader("📈 Spending Analysis")

if analysis_view == "Expenses only":
    chart_df = expense_df.copy()
    if chart_df.empty:
        st.info("No expense transactions in the selected filters. Charts show spending only.")
    else:
        chart_df["MonthPeriod"] = chart_df["Date"].dt.to_period("M")
        monthly = chart_df.groupby("MonthPeriod", as_index=False)["Amount"].sum().sort_values("MonthPeriod")
        monthly["Month"] = monthly["MonthPeriod"].astype(str)
        monthly["Amount"] = monthly["Amount"].abs()
        fig_monthly = px.bar(
            monthly,
            x="Month",
            y="Amount",
            title="Monthly Spending",
            labels={"Amount": "Total Spent ($)", "Month": ""},
            color_discrete_sequence=["#1e3a5f"],
        )
        fig_monthly.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
        st.plotly_chart(fig_monthly, use_container_width=True)

        cat_sum = chart_df.groupby("Category")["Amount"].sum().reset_index()
        cat_sum["Amount"] = cat_sum["Amount"].abs()
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

        daily = chart_df.groupby(chart_df["Date"].dt.date)["Amount"].sum().reset_index()
        daily["Amount"] = daily["Amount"].abs()
        fig_line = px.line(
            daily,
            x="Date",
            y="Amount",
            title="Daily Spending Trend",
            labels={"Amount": "Spent ($)", "Date": ""},
            color_discrete_sequence=["#00a699"],
        )
        fig_line.update_traces(line=dict(width=2.5))
        fig_line.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12), hovermode="x unified")
        st.plotly_chart(fig_line, use_container_width=True)

elif analysis_view == "All transactions":
    chart_df = df_filtered.copy()
    chart_df["MonthPeriod"] = chart_df["Date"].dt.to_period("M")
    monthly_net = chart_df.groupby("MonthPeriod", as_index=False)["Amount"].sum().sort_values("MonthPeriod")
    monthly_net["Month"] = monthly_net["MonthPeriod"].astype(str)
    fig_monthly = px.bar(
        monthly_net,
        x="Month",
        y="Amount",
        title="Monthly Net Cash Flow",
        labels={"Amount": "Net Cash Flow ($)", "Month": ""},
        color_discrete_sequence=["#1e3a5f"],
    )
    fig_monthly.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
    st.plotly_chart(fig_monthly, use_container_width=True)

    daily = chart_df.groupby(chart_df["Date"].dt.date)["Amount"].sum().reset_index()
    fig_line = px.line(
        daily,
        x="Date",
        y="Amount",
        title="Daily Net Cash Flow",
        labels={"Amount": "Net Cash Flow ($)", "Date": ""},
        color_discrete_sequence=["#00a699"],
    )
    fig_line.update_traces(line=dict(width=2.5))
    fig_line.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12), hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

else:
    chart_df = df_filtered.copy()
    chart_df["MonthPeriod"] = chart_df["Date"].dt.to_period("M")
    monthly_flow = (
        chart_df.assign(FlowType=np.where(chart_df["Amount"] >= 0, "Income", "Expenses"))
        .assign(Amount=chart_df["Amount"].abs())
        .groupby(["MonthPeriod", "FlowType"], as_index=False)["Amount"]
        .sum()
        .sort_values("MonthPeriod")
    )
    monthly_flow["Month"] = monthly_flow["MonthPeriod"].astype(str)
    fig_monthly = px.bar(
        monthly_flow,
        x="Month",
        y="Amount",
        color="FlowType",
        barmode="group",
        title="Income vs Expenses by Month",
        labels={"Amount": "Amount ($)", "Month": ""},
        color_discrete_map={"Income": "#2ecc71", "Expenses": "#e74c3c"},
    )
    fig_monthly.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
    st.plotly_chart(fig_monthly, use_container_width=True)

    flow_summary = (
        chart_df.assign(FlowType=np.where(chart_df["Amount"] >= 0, "Income", "Expenses"))
        .assign(Amount=chart_df["Amount"].abs())
        .groupby("FlowType", as_index=False)["Amount"]
        .sum()
    )
    fig_pie = px.pie(
        flow_summary,
        values="Amount",
        names="FlowType",
        title="Income vs Expenses",
        hole=0.4,
        color_discrete_map={"Income": "#2ecc71", "Expenses": "#e74c3c"},
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
    st.plotly_chart(fig_pie, use_container_width=True)

top_merchants = (
    expense_df.groupby("Merchant", as_index=False)["Amount"].sum()
    .assign(Amount=lambda frame: frame["Amount"].abs())
    .sort_values("Amount", ascending=False)
    .head(10)
)

if not top_merchants.empty:
    fig_merchants = px.bar(
        top_merchants.sort_values("Amount", ascending=True),
        x="Amount",
        y="Merchant",
        orientation="h",
        title="Top 10 Merchants by Spend",
        labels={"Amount": "Spent ($)", "Merchant": ""},
        color_discrete_sequence=["#1e3a5f"],
    )
    fig_merchants.update_layout(template="plotly_white", font=dict(family="sans-serif", size=12))
    st.plotly_chart(fig_merchants, use_container_width=True)
else:
    st.info("No merchant spend data available for the selected filters.")

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
st.caption(
    "🧟 **Finance Goblin** – Built by Fuaad Abdullah "
    "Uploaded files are processed in-session and not saved permanently. Licensed under MIT."
)
