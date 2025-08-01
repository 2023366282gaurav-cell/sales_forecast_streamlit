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

    # --- KPIs ---
    st.markdown("### 🔢 Forecast Summary")

    latest = df_range.iloc[-1]
    prev = df_range.iloc[-2] if len(df_range) > 1 else latest
    delta = latest['yhat'] - prev['yhat']

    col1, col2 = st.columns(2)
    col1.metric("Latest Prediction", f"{latest['yhat']:,.2f}", f"{delta:,.2f}")
    col2.metric("Forecast Date", latest['ds'].strftime('%b %Y'))

    # --- Table ---
    if show_table:
        st.markdown("### 📋 Forecast Table")
        st.dataframe(df_range[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={
            'ds': 'Date', 'yhat': 'Prediction', 'yhat_lower': 'Lower Bound', 'yhat_upper': 'Upper Bound'
        }), use_container_width=True)

    # --- Download Forecast Button ---
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇️ Download Forecast CSV",
        data=convert_df_to_csv(df),
        file_name="sales_forecast.csv",
        mime='text/csv',
    )

except Exception as e:
    st.error("⚠️ Could not load forecast. Make sure `forecast.csv` exists or upload a valid file.")
    st.exception(e)
