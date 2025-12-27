import os
import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="SkyLogix Weather Dashboard", layout="wide")

POSTGRES_URI = os.getenv("POSTGRES_URI") or os.getenv("PG_URI")  # handles both names

@st.cache_data(ttl=60)
def run_query(query: str, params=None) -> pd.DataFrame:
    conn = psycopg2.connect(POSTGRES_URI)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

st.title("🌦️ SkyLogix Weather Pipeline Dashboard")

# Sidebar controls
hours = st.sidebar.slider("Time window (hours)", min_value=1, max_value=48, value=24)
city_filter = st.sidebar.text_input("Filter by city (optional)").strip()

city_where = ""
params = {"hours": hours}
if city_filter:
    city_where = "AND city ILIKE %(city)s"
    params["city"] = f"%{city_filter}%"

# KPI row
kpi_df = run_query(
    f"""
    SELECT
        COUNT(*) AS rows_loaded,
        COUNT(DISTINCT city) AS cities,
        MAX(observed_at) AS latest_observation
    FROM weather_readings
    WHERE observed_at >= NOW() - (INTERVAL '1 hour' * %(hours)s)
    {city_where};
    """,
    params,
)

col1, col2, col3 = st.columns(3)
col1.metric("Rows (window)", int(kpi_df.loc[0, "rows_loaded"]))
col2.metric("Cities", int(kpi_df.loc[0, "cities"]))
col3.metric("Latest observation", str(kpi_df.loc[0, "latest_observation"]))

st.divider()

# Average temperature by city (last N hours)
avg_temp = run_query(
    f"""
    SELECT
        city,
        ROUND(AVG(temp_c), 2) AS avg_temp_c
    FROM weather_readings
    WHERE observed_at >= NOW() - (INTERVAL '1 hour' * %(hours)s)
    {city_where}
    GROUP BY city
    ORDER BY avg_temp_c DESC;
    """,
    params,
)

left, right = st.columns([1, 1])

with left:
    st.subheader("🌡️ Avg Temperature by City")
    st.dataframe(avg_temp, use_container_width=True)

with right:
    st.subheader("📈 Temperature Trend (per city)")
    trend = run_query(
        f"""
        SELECT
            city,
            date_trunc('hour', observed_at) AS observed_hour,
            ROUND(AVG(temp_c), 2) AS avg_temp_c
        FROM weather_readings
        WHERE observed_at >= NOW() - (INTERVAL '1 hour' * %(hours)s)
        {city_where}
        GROUP BY city, date_trunc('hour', observed_at)
        ORDER BY observed_hour ASC;
        """,
        params,
    )
    if not trend.empty:
        pivot = trend.pivot_table(index="observed_hour", columns="city", values="avg_temp_c")
        st.line_chart(pivot, height=320)
    else:
        st.info("No data available for the selected window/filter.")

st.divider()

# Extreme weather events
st.subheader("⚠️ Extreme Weather Events (Thresholds)")
wind_threshold = st.slider("High wind threshold (m/s)", 1.0, 30.0, 10.0, 0.5)
rain_threshold = st.slider("Heavy rain threshold (mm in 1h)", 0.0, 50.0, 5.0, 0.5)

events = run_query(
    f"""
    SELECT
        city,
        observed_at,
        wind_speed_ms,
        rain_1h_mm,
        condition_main,
        condition_description
    FROM weather_readings
    WHERE observed_at >= NOW() - (INTERVAL '1 hour' * %(hours)s)
      {city_where}
      AND (wind_speed_ms > %(wind)s OR rain_1h_mm > %(rain)s)
    ORDER BY observed_at DESC;
    """,
    {**params, "wind": wind_threshold, "rain": rain_threshold},
)

st.dataframe(events, use_container_width=True)

st.divider()

# Weather vs Logistics join (only if table exists)
st.subheader("🚚 Weather vs Logistics Delays (Join)")

join_df = run_query(
    f"""
    SELECT
        w.city,
        w.observed_at,
        w.condition_main,
        w.wind_speed_ms,
        w.rain_1h_mm,
        l.trip_id,
        l.delay_minutes
    FROM weather_readings w
    JOIN logistics_trips l
      ON w.city = l.city
     AND w.observed_at BETWEEN l.trip_time - INTERVAL '15 minutes'
                           AND l.trip_time + INTERVAL '15 minutes'
    WHERE w.observed_at >= NOW() - (INTERVAL '1 hour' * %(hours)s)
      { "AND w.city ILIKE %(city)s" if city_filter else "" }
    ORDER BY l.delay_minutes DESC;
    """,
    params,
)

if join_df.empty:
    st.info("No matching joined records found in the selected window/filter.")
else:
    st.dataframe(join_df, use_container_width=True)
