from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRACKER_FILE = PROJECT_ROOT / "data" / "Performance Tracker.xlsx"

def _excel_serial_to_datetime(series):
    """
    Handles Excel dates whether pandas/openpyxl returns them as
    actual datetime objects, date strings, or Excel serial numbers.
    """
    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    numeric_values = pd.to_numeric(series, errors="coerce")
    numeric_mask = numeric_values.notna()

    if numeric_mask.any():
        result.loc[numeric_mask] = pd.to_datetime(
            numeric_values.loc[numeric_mask],
            unit="D",
            origin="1899-12-30",
            errors="coerce"
        )

    non_numeric_mask = ~numeric_mask
    if non_numeric_mask.any():
        result.loc[non_numeric_mask] = pd.to_datetime(
            series.loc[non_numeric_mask],
            errors="coerce"
        )

    return result

def _numeric_clean(series):
    return pd.to_numeric(series.replace("-", np.nan), errors="coerce")

def load_performance_tracker(file_path=TRACKER_FILE):
    """
    Loads the Performance Tracker workbook.

    Expected workbook:
    - Sheet: Options
    - Main weekly tracker starts with headers on row 3 and data on row 4.
    """
    try:
        raw = pd.read_excel(file_path, sheet_name="Options", header=None, engine="openpyxl")
    except FileNotFoundError:
        return None, f"Could not find '{file_path}'. Upload it to the same folder as this app."
    except Exception as e:
        return None, f"Could not read '{file_path}': {e}"

    rows = raw.iloc[3:].copy()

    df = pd.DataFrame({
        "Week": rows.iloc[:, 1],
        "Week Start": rows.iloc[:, 2],
        "Year": rows.iloc[:, 3],
        "Budget Start Balance": rows.iloc[:, 4],
        "Budget Gains $": rows.iloc[:, 5],
        "Budget Gains %": rows.iloc[:, 6],
        "Budget Deposits": rows.iloc[:, 7],
        "Budget End Balance": rows.iloc[:, 8],
        "Forecast Gains $": rows.iloc[:, 10],
        "Forecast Gains %": rows.iloc[:, 11],
        "Forecast Deposits": rows.iloc[:, 12],
        "Forecast End Balance": rows.iloc[:, 13],
        "Actual Start Balance": rows.iloc[:, 15],
        "Actual Gains $": rows.iloc[:, 16],
        "Actual Gains %": rows.iloc[:, 17],
        "Actual Deposits": rows.iloc[:, 18],
        "Actual End Balance": rows.iloc[:, 19],
        "Variance vs Budget": rows.iloc[:, 21],
        "Variance vs Forecast": rows.iloc[:, 22],
        "Trend": rows.iloc[:, 23],
        "Win Rate": rows.iloc[:, 24],
        "Position % of Balance": rows.iloc[:, 26],
        "Position % of Position": rows.iloc[:, 27],
        "Total Costs": rows.iloc[:, 28],
        "Number of Trades": rows.iloc[:, 29],
        "Position Cost % of Balance": rows.iloc[:, 30],
        "Aggressive Max": rows.iloc[:, 31],
        "Aggressive %": rows.iloc[:, 32],
        "Fees": rows.iloc[:, 33],
        "Comments": rows.iloc[:, 34],
    })

    df = df[pd.to_numeric(df["Week"], errors="coerce").notna()].copy()

    numeric_cols = [
        "Week", "Year", "Budget Start Balance", "Budget Gains $", "Budget Gains %",
        "Budget Deposits", "Budget End Balance", "Forecast Gains $", "Forecast Gains %",
        "Forecast Deposits", "Forecast End Balance", "Actual Start Balance",
        "Actual Gains $", "Actual Gains %", "Actual Deposits", "Actual End Balance",
        "Variance vs Budget", "Variance vs Forecast", "Trend", "Win Rate",
        "Position % of Balance", "Position % of Position", "Total Costs",
        "Number of Trades", "Position Cost % of Balance", "Aggressive Max",
        "Aggressive %", "Fees"
    ]

    for col in numeric_cols:
        df[col] = _numeric_clean(df[col])

    df["Week Start"] = _excel_serial_to_datetime(df["Week Start"])
    df = df.sort_values("Week Start").reset_index(drop=True)

    ltd = raw.iloc[3:10, 37:39].copy()
    ltd.columns = ["Label", "Amount"]
    ltd = ltd.dropna(how="all")
    ltd["Amount"] = pd.to_numeric(ltd["Amount"], errors="coerce")

    return {"weekly": df, "ltd": ltd}, None

def make_performance_line_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Actual End Balance"],
        mode="lines+markers",
        name="Actual End Balance"
    ))

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Budget End Balance"],
        mode="lines",
        name="Budget End Balance"
    ))

    fig.add_trace(go.Scatter(
        x=df["Week Start"],
        y=df["Forecast End Balance"],
        mode="lines",
        name="Forecast End Balance"
    ))

    fig.update_layout(
        title="Ending Balance: Actual vs Budget vs Forecast",
        xaxis_title="Week",
        yaxis_title="Ending Balance",
        height=430,
        hovermode="x unified",
        dragmode="zoom",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig

def make_weekly_gains_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["Week Start"],
        y=df["Actual Gains $"],
        name="Actual Gains $"
    ))

    fig.update_layout(
        title="Weekly Actual Gains / Losses",
        xaxis_title="Week",
        yaxis_title="Actual Gains $",
        height=360,
        hovermode="x unified",
        dragmode="zoom"
    )

    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig

def display_performance_tracker_page():
    st.title("Performance Tracker")
    st.caption("Weekly trading account performance, budget, forecast, actuals, variance, and position sizing.")

    data, error = load_performance_tracker()

    if error:
        st.error(error)
        st.info("For deployment, upload `Performance Tracker.xlsx` to your GitHub repo beside the Streamlit `.py` file.")
        return

    df = data["weekly"]
    ltd = data["ltd"]

    actual_rows = df[df["Actual End Balance"].notna()].copy()

    if actual_rows.empty:
        st.warning("No actual performance rows found yet.")
        st.dataframe(df, use_container_width=True)
        return

    latest = actual_rows.iloc[-1]

    current_balance = latest["Actual End Balance"]
    latest_week = int(latest["Week"])
    ytd_gains = actual_rows["Actual Gains $"].sum(skipna=True)
    ytd_deposits = actual_rows["Actual Deposits"].sum(skipna=True)
    total_trades = actual_rows["Number of Trades"].sum(skipna=True)
    latest_win_rate = latest["Win Rate"]
    variance_vs_budget = latest["Variance vs Budget"]
    variance_vs_forecast = latest["Variance vs Forecast"]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Current Balance", f"${current_balance:,.2f}" if pd.notna(current_balance) else "-")
    kpi2.metric("YTD Actual Gains", f"${ytd_gains:,.2f}" if pd.notna(ytd_gains) else "-")
    kpi3.metric("YTD Deposits", f"${ytd_deposits:,.2f}" if pd.notna(ytd_deposits) else "-")
    kpi4.metric("Latest Week", f"Week {latest_week}")

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)

    kpi5.metric("Latest Win Rate", f"{latest_win_rate:.1%}" if pd.notna(latest_win_rate) else "-")
    kpi6.metric("Total Trades", f"{int(total_trades):,}" if pd.notna(total_trades) else "-")
    kpi7.metric("Variance vs Budget", f"${variance_vs_budget:,.2f}" if pd.notna(variance_vs_budget) else "-")
    kpi8.metric("Variance vs Forecast", f"${variance_vs_forecast:,.2f}" if pd.notna(variance_vs_forecast) else "-")

    st.divider()

    chart_col1, chart_col2 = st.columns([1.35, 1])

    with chart_col1:
        st.plotly_chart(
            make_performance_line_chart(actual_rows),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

    with chart_col2:
        st.plotly_chart(
            make_weekly_gains_chart(actual_rows),
            use_container_width=True,
            config={"scrollZoom": True, "displayModeBar": True}
        )

    st.subheader("Weekly Performance Table")

    display_cols = [
        "Week", "Week Start", "Budget End Balance", "Forecast End Balance",
        "Actual End Balance", "Actual Gains $", "Actual Gains %", "Actual Deposits",
        "Variance vs Budget", "Variance vs Forecast", "Win Rate",
        "Position % of Balance", "Total Costs", "Number of Trades", "Fees", "Comments"
    ]

    display_df = df[display_cols].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Week Start": st.column_config.DateColumn("Week Start", format="YYYY-MM-DD"),
            "Budget End Balance": st.column_config.NumberColumn("Budget End Balance", format="$%.2f"),
            "Forecast End Balance": st.column_config.NumberColumn("Forecast End Balance", format="$%.2f"),
            "Actual End Balance": st.column_config.NumberColumn("Actual End Balance", format="$%.2f"),
            "Actual Gains $": st.column_config.NumberColumn("Actual Gains $", format="$%.2f"),
            "Actual Gains %": st.column_config.NumberColumn("Actual Gains %", format="percent"),
            "Actual Deposits": st.column_config.NumberColumn("Actual Deposits", format="$%.2f"),
            "Variance vs Budget": st.column_config.NumberColumn("Variance vs Budget", format="$%.2f"),
            "Variance vs Forecast": st.column_config.NumberColumn("Variance vs Forecast", format="$%.2f"),
            "Win Rate": st.column_config.NumberColumn("Win Rate", format="percent"),
            "Position % of Balance": st.column_config.NumberColumn("Position % of Balance", format="percent"),
            "Total Costs": st.column_config.NumberColumn("Total Costs", format="$%.2f"),
            "Fees": st.column_config.NumberColumn("Fees", format="$%.2f"),
        }
    )

    if ltd is not None and not ltd.empty:
        st.subheader("LTD Losses / Net Gains-Losses")
        st.dataframe(
            ltd,
            use_container_width=True,
            hide_index=True,
            column_config={"Amount": st.column_config.NumberColumn("Amount", format="$%.2f")}
        )

