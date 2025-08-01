import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📈 Sales Forecast Dashboard")

df = pd.read_csv("forecast.csv")
df['ds'] = pd.to_datetime(df['ds'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['ds'], y=df['yhat'], mode='lines', name='Forecast'))

if 'yhat_lower' in df.columns and 'yhat_upper' in df.columns:
    fig.add_trace(go.Scatter(x=df['ds'], y=df['yhat_upper'], mode='lines', name='Upper Bound', line=dict(color='lightblue', dash='dot')))
    fig.add_trace(go.Scatter(x=df['ds'], y=df['yhat_lower'], mode='lines', name='Lower Bound', line=dict(color='lightblue', dash='dot')))

fig.update_layout(title="Forecasted Sales", xaxis_title="Date", yaxis_title="Sales")
st.plotly_chart(fig, use_container_width=True)

# Summary Metric
latest = df.iloc[-1]
st.metric(label="Next Forecast", value=f"{latest['yhat']:.2f}", delta=f"{(latest['yhat'] - df['yhat'].iloc[-2]):.2f}")
