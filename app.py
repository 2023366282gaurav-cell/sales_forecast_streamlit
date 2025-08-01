import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Sales Forecast Dashboard", layout="wide")

# --- Sidebar ---
st.sidebar.title("🔧 Options")

uploaded_file = st.sidebar.file_uploader("Upload a Forecast CSV", type=["csv"])
show_bounds = st.sidebar.checkbox("Show Confidence Intervals", value=True)
show_table = st.sidebar.checkbox("Show Forecast Table", value=False)

# --- Load Data ---
@st.cache_data
def load_forecast_data(file):
    df = pd.read_csv(file)
    df['ds'] = pd.to_datetime(df['ds'])
    return df

try:
    if uploaded_file:
        df = load_forecast_data(uploaded_file)
    else:
        df = load_forecast_data("forecast.csv")  # fallback

    # --- Convert pandas Timestamp to native Python datetime for Streamlit slider ---
    min_date, max_date = df['ds'].min(), df['ds'].max()
    min_date_py = min_date.to_pydatetime()
    max_date_py = max_date.to_pydatetime()

    # --- Date Slider ---
    selected_range = st.slider(
        "📅 Select forecast date range:",
        min_value=min_date_py,
        max_value=max_date_py,
        value=(min_date_py, max_date_py)
    )

    df_range = df[(df['ds'] >= selected_range[0]) & (df['ds'] <= selected_range[1])]

    # --- Forecast Plot ---
    st.subheader("📊 Forecasted Sales")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_range['ds'],
        y=df_range['yhat'],
        name='Forecast',
        line=dict(color='royalblue')
    ))

    if show_bounds and 'yhat_lower' in df.columns and 'yhat_upper' in df.columns:
        fig.add_trace(go.Scatter(
            x=df_range['ds'],
            y=df_range['yhat_lower'],
            name='Lower Bound',
            line=dict(color='lightblue', dash='dot')
        ))
        fig.add_trace(go.Scatter(
            x=df_range['ds'],
            y=df_range['yhat_upper'],
            name='Upper Bound',
            line=dict(color='lightblue', dash='dot')
        ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- KPIs -
