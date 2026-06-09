
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

st.title("💰 Personal Finance Dashboard")

uploaded_file = st.file_uploader("Upload Transactions CSV", type=["csv"])

required_cols = ["Date", "Description", "Category", "Amount", "Transaction Type"]

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
            st.stop()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        if df["Date"].isna().any():
            st.warning("Some rows contain invalid dates and may affect reporting.")

        income = df[df["Transaction Type"].str.lower() == "credit"]["Amount"].sum()
        expense = df[df["Transaction Type"].str.lower() == "debit"]["Amount"].sum()
        savings = income - expense

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Income", f"₹{income:,.2f}")
        c2.metric("Total Expense", f"₹{expense:,.2f}")
        c3.metric("Net Savings", f"₹{savings:,.2f}")

        st.subheader("Budget Tracking")
        budget = st.number_input("Monthly Budget", min_value=0.0, value=10000.0)

        if budget > 0:
            utilization = (expense / budget) * 100
            st.progress(min(utilization / 100, 1.0))
            st.write(f"Budget Utilization: {utilization:.2f}%")

            if expense > budget:
                st.error(f"Budget exceeded by ₹{expense - budget:,.2f}")

        expense_df = df[df["Transaction Type"].str.lower() == "debit"]

        if not expense_df.empty:
            st.subheader("Expense by Category")
            cat = expense_df.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(cat, values="Amount", names="Category")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.bar(cat, x="Category", y="Amount")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Monthly Spending Trend")
        monthly = expense_df.copy()
        monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)
        monthly = monthly.groupby("Month")["Amount"].sum().reset_index()

        if not monthly.empty:
            fig3 = px.line(monthly, x="Month", y="Amount", markers=True)
            st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Transactions")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Upload a CSV file to begin.")
