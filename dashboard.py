import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_rentals_df(day_df):
    daily_rentals_df = day_df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    daily_rentals_df = daily_rentals_df.reset_index()
    daily_rentals_df.rename(columns={
        "instant": "record_index",
        "cnt": "rentals_count"
    }, inplace=True)
    return daily_rentals_df

def create_total_registered_df(day_df):
    total_registered_df = day_df.groupby(by="dteday").agg({
        "registered": "sum"
    })
    total_registered_df = total_registered_df.reset_index()
    total_registered_df.rename(columns={
        "registered": "total_registered",
    }, inplace=True)
    return total_registered_df

def create_total_casual_df(day_df):
    total_casual_df = day_df.groupby(by="dteday").agg({
        "casual": "sum"
    })
    total_casual_df = total_casual_df.reset_index()
    total_casual_df.rename(columns={
        "casual": "total_casual",
    }, inplace=True)
    return total_casual_df

def create_season_df(day_df):
    season_df = day_df.groupby(by="season").cnt.sum().reset_index()
    season_df.rename(columns={
        "cnt": "rentals_count"
    }, inplace=True)
    return season_df

def create_weather_df(day_df):
    weather_df = day_df.groupby(by="weathersit").cnt.sum().reset_index()
    weather_df.rename(columns={
        "cnt": "rentals_count"
    }, inplace=True)
    return weather_df

def create_rfm_df(day_df):
    today = max(day_df['dteday'])
    rfm_df = day_df.groupby('registered').agg({
        'dteday': lambda x: (today - x.max()).days,
        'instant': 'count',
        'cnt': 'sum'
    }).reset_index()
    rfm_df.columns = ['registered', 'Recency', 'Frequency', 'Monetary']
    return rfm_df

day_df = pd.read_csv("day_data.csv")

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()


with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/HallenNaafi/Proyek-Analisis-Data/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_day_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

daily_rentals_df = create_daily_rentals_df(main_day_df)
total_registered_df = create_total_registered_df(main_day_df)
total_casual_df = create_total_casual_df(main_day_df)
season_df = create_season_df(main_day_df)
weather_df = create_weather_df(main_day_df)
rfm_df = create_rfm_df(main_day_df)

st.header('Bike Sharing Dashboard :sparkles:')
total_rentals = daily_rentals_df.rentals_count.sum()
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.metric(":bike: Total Number of Bike Rentals", value=total_rentals)

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    total_casual_rentals = total_casual_df.total_casual.sum()
    st.metric(":large_blue_circle: Number of Rentals by Casual Users", value=total_casual_rentals)

with col2:
    total_registered_rentals = total_registered_df.total_registered.sum()
    st.metric(":large_green_circle: Number of Rentals by Registered Users", value=total_registered_rentals)

st.subheader(':chart_with_upwards_trend: Number of Daily Bike Rentals in 2011')
filtered_day_df = day_df[(day_df["dteday"] >= "2011-01-01") & (day_df["dteday"] < "2012-01-01")]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    filtered_day_df["dteday"],
    filtered_day_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#FF0000"
)
plt.ylabel("Rentals Count")
plt.xlabel("Year-Month")
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader(':chart_with_downwards_trend: Number of Daily Bike Rentals in 2012')
filtered_day_df = day_df[(day_df["dteday"] >= "2012-01-01") & (day_df["dteday"] < "2013-01-01")]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    filtered_day_df["dteday"],
    filtered_day_df["cnt"],
    marker='o', 
    linewidth=2,
    color="#0000CD"
)
plt.ylabel("Rentals Count")
plt.xlabel("Year-Month")
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader(':snowflake: Number of Bike Rentals by Season')
fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#90EE90", "#90EE90", "#32CD32", "#32CD32"]
sns.barplot(
    y="rentals_count", 
    x="season",
    data=season_df.sort_values(by="season", ascending=False),
    palette=colors,
    ax=ax
    )

plt.ylabel("Rentals Count")
plt.xlabel("Season")
plt.tick_params(axis='x', labelsize=15)
plt.tick_params(axis='y', labelsize=15)
plt.gca().set_yticklabels(['{:.0f}'.format(x/100) for x in plt.gca().get_yticks()])
st.pyplot(fig)

st.subheader(':sunny: Number of Bike Rentals by Weather')
fig, ax = plt.subplots(figsize=(6, 6))
colors = ["#FFD700", "#FF69B4", "#1E90FF", "#32CD32"]
plt.pie(weather_df["rentals_count"], labels=weather_df["weathersit"], colors=colors, autopct='%1.1f%%')
st.pyplot(fig)

st.subheader('Recency Distribution :bar_chart:')
fig, ax = plt.subplots(figsize=(12, 8))
sns.histplot(rfm_df['Recency'], bins=20, kde=True, color='orangered')
plt.xlabel('Recency (days)')
plt.ylabel('Rentals Count')
st.pyplot(fig)

st.subheader('Frequency Distribution :bar_chart:')
fig, ax = plt.subplots(figsize=(12, 8))
sns.histplot(rfm_df['Frequency'], bins=20, kde=True, color="yellow")
plt.xlabel('Frequency')
plt.ylabel('Rentals Count')
st.pyplot(fig)

st.subheader('Monetary Distribution :bar_chart:')
fig, ax = plt.subplots(figsize=(12, 8))
sns.histplot(rfm_df['Monetary'], bins=20, kde=True, color='dodgerblue')
plt.xlabel('Monetary')
plt.ylabel('Rentals Count')
st.pyplot(fig)

st.caption(':copyright: HallenNaafi')