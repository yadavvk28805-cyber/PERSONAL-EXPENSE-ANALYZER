import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Personal Finance Expense Analysis", page_icon="💰", layout="wide"
)

# Fix for Indian Rupee symbol rendering in Matplotlib charts
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


@st.cache_data
def load_sample_data():
    """Generates sample DataFrame directly if no file is uploaded."""
    sample_data = """Date,Category,Amount,Description
2026-09-01,Rent,15000.00,Monthly Apartment Rent
2026-09-02,Food,450.50,Grocery Store Run
2026-09-03,Utilities,1850.20,Electricity Bill
2026-09-05,Entertainment,500.00,Movie Tickets
2026-09-06,Food,250.75,Coffee & Snacks
2026-09-08,Transportation,1200.00,Fuel Refill
2026-09-10,Food,2680.40,Supermarket
2026-09-12,Utilities,450.00,Water Bill
2026-09-18,Food,320.10,Lunch
2026-09-20,Entertainment,1500.00,Concert Ticket
2026-09-22,Transportation,850.00,Metro / Train Pass
2026-09-25,Utilities,999.00,Internet Bill
2026-09-28,Food,1550.30,Dinner with Friends
"""
    from io import StringIO

    return pd.read_csv(StringIO(sample_data))


def main():
    st.title("💰 Personal Finance Expense Analysis (INR)")
    st.write(
        "Apni expenses CSV file upload karein ya default sample data ke sath dashboard dekhein."
    )

    # Sidebar for file upload
    st.sidebar.header("📁 Data Configuration")
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return
    else:
        df = load_sample_data()

    # Clean header whitespace and format column names
    df.columns = df.columns.str.strip().str.capitalize()

    # Validate required columns exist
    required_cols = {"Date", "Category", "Amount"}
    if not required_cols.issubset(df.columns):
        st.error(
            f"CSV file mein ye columns hone chahiye: {required_cols}. Aapki file mein ye columns hain: {list(df.columns)}"
        )
        return

    # Convert types and clean bad rows
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Date", "Category", "Amount"])
    df = df[df["Amount"] > 0]

    if df.empty:
        st.warning("Koi valid transaction data nahi mila!")
        return

    # Calculations (Pandas & NumPy)
    amounts = df["Amount"].to_numpy()
    total_spend = np.sum(amounts)
    mean_transaction = np.mean(amounts)
    median_transaction = np.median(amounts)
    std_dev_transaction = np.std(amounts)
    max_transaction = np.max(amounts)
    min_transaction = np.min(amounts)

    num_days = (df["Date"].max() - df["Date"].min()).days + 1
    avg_daily_spend = total_spend / num_days if num_days > 0 else total_spend

    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    category_amounts = category_totals.to_numpy()
    category_percentages = (category_amounts / total_spend) * 100

    # --- UI LAYOUT ---

    # Metrics Section (Top Cards)
    st.markdown("### 📊 Key Financial Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Expenditure", f"₹{total_spend:,.2f}")
    col2.metric("Tracking Period", f"{num_days} Days")
    col3.metric("Avg Daily Spend", f"₹{avg_daily_spend:,.2f}")
    col4.metric("Largest Expense", f"₹{max_transaction:,.2f}")

    st.markdown("---")

    # Detailed Transaction Metrics Expander
    with st.expander("🔍 View Advanced NumPy / Statistical Metrics"):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Mean Transaction", f"₹{mean_transaction:,.2f}")
        m2.metric("Median Transaction", f"₹{median_transaction:,.2f}")
        m3.metric("Std Deviation", f"₹{std_dev_transaction:,.2f}")
        m4.metric("Smallest Expense", f"₹{min_transaction:,.2f}")

    # Charts Section
    st.markdown("### 📈 Expense Visualizations")
    categories = category_totals.index.tolist()
    amounts_list = category_totals.values.tolist()
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Personal Finance Expense Analysis (INR)", fontsize=14, fontweight="bold"
    )

    # Chart 1: Pie Chart
    ax1.pie(
        amounts_list,
        labels=categories,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[: len(categories)],
        explode=[0.05] + [0] * (len(categories) - 1),
    )
    ax1.set_title("Expense Distribution by Category")

    # Chart 2: Bar Chart
    bars = ax2.bar(
        categories, amounts_list, color=colors[: len(categories)], edgecolor="black"
    )
    ax2.set_title("Total Spending per Category (₹)")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Amount (₹)")
    ax2.grid(axis="y", linestyle="--", alpha=0.7)

    # Add labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            yval + (max(amounts_list) * 0.01),
            f"₹{yval:,.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

    # Data Table View
    st.markdown("### 📋 Filtered Transactions Data")
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main() 