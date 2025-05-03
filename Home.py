import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Steam Games Analysis", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main, .css-18e3th9, .css-1d391kg, .stApp {
        background-color: #599cba;
        color: white;
    }
    h1, h3 { color: white; }
    .nav-item { font-size: 18px; margin-right: 20px; display: inline-block; }
    .nav-item a { color: white; text-decoration: none; }
    .nav-item a:hover { color: #ffa500; }
    </style>
""", unsafe_allow_html=True)

# Title & Subtitle
st.markdown("<h1 style='text-align: center;'>🎮 Steam Games Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>🏠 Homepage</h3>", unsafe_allow_html=True)

# Load and clean data
df = pd.read_csv("games.csv")
for col in ['Launch.Price', 'Reviews.Total', 'Revenue.Estimated']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['Release Year'] = pd.to_datetime(df['Release.Date'], errors='coerce').dt.year
df = df[(df['Release Year'] >= 1990) & (df['Release Year'] <= 2025)]
df.dropna(subset=['Launch.Price', 'Reviews.Total', 'Revenue.Estimated'], inplace=True)

# Frequency Distribution
def display_distribution(column, step, max_val, prefix="$"):
    def fmt(val): return f"{prefix}{val / 1_000_000:.1f}M" if val >= 1e6 else f"{prefix}{val / 1_000:.0f}K" if val >= 1e3 else f"{prefix}{val}"
    
    bins = list(range(0, max_val + step, step)) + [np.inf]
    labels = [f"{fmt(bins[i])} - {fmt(bins[i+1])}" for i in range(len(bins)-2)] + [f">{fmt(max_val)}"]

    df[f"{column}_bin"] = pd.cut(df[column], bins=bins, labels=labels, right=False)
    freq = df[f"{column}_bin"].value_counts().sort_index()
    table = pd.DataFrame({
        "Range": freq.index.astype(str),
        "Frequency": freq.values,
        "Cumulative Frequency": freq.cumsum().values,
        "Relative Frequency (%)": (freq / freq.sum() * 100).round(2)
    })

    st.markdown("<h3 style='text-align: center;'>📊 Frequency Distribution Table</h3>", unsafe_allow_html=True)
    st.dataframe(table, use_container_width=True)

# Selection
col_options = {
    "Launch Price": ("Launch.Price", 10, 60, "$"),
    "Reviews Total": ("Reviews.Total", 50000, 300000, ""),
    "Revenue Estimated": ("Revenue.Estimated", 1500000, 9000000, "$")
}

choice = st.radio("Select a column to view distribution:", list(col_options))
col, step, max_val, prefix = col_options[choice]
display_distribution(col, step, max_val, prefix)

# Bar Chart
st.markdown("<h3 style='text-align: center; color: white;'>📈 Bar Chart</h3>", unsafe_allow_html=True)

# Select Option
bar_option = st.selectbox("Select metric for bar chart:", [
    "Revenue Estimated", 
    "Reviews Total", 
    "Total Games Released Per Year", 
    "Total Revenue Per Year",
    "Total Games Released Per Month",
    "Total Revenue Per Month",
    "Launch Price"
], index=0)

# Determine if time-based metric
time_metrics = [
    "Total Games Released Per Year",
    "Total Revenue Per Year",
    "Total Games Released Per Month",
    "Total Revenue Per Month"
]
is_line_chart = st.toggle("Line Chart") if bar_option in time_metrics else False
chart_func = px.line if is_line_chart else px.bar

# Plot settings
def apply_dark_layout(fig, title, xaxis_title, yaxis_title):
    fig.update_layout(
        title=title,
        template='plotly_dark',
        plot_bgcolor='#599cba',
        paper_bgcolor='#599cba',
        font_color='white',
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )
    fig.update_traces(marker=dict(color='white'))  # Set the bar color to white
    return fig

# 1. Revenue Estimated
if bar_option == "Revenue Estimated":
    revenue_bins = [0, 1.5e6, 3e6, 4.5e6, 6e6, 7.5e6, 9e6, 10.5e6, 12e6, 13.5e6, 15e6]
    revenue_labels = [f"${int(b/1e6)}M - ${int(revenue_bins[i+1]/1e6)}M" for i, b in enumerate(revenue_bins[:-1])]
    df['Revenue.Bin'] = pd.cut(df['Revenue.Estimated'], bins=revenue_bins, labels=revenue_labels, right=False)
    data = df.groupby('Revenue.Bin').Title.count().reset_index(name="Total_Games")
    fig = px.bar(data, x='Revenue.Bin', y='Total_Games', labels={'Revenue.Bin': 'Revenue Range', 'Total_Games': 'Total Number of Games'})
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(apply_dark_layout(fig, "Number of Games vs Revenue Estimated", "Revenue Range ($)", "Total Number of Games"), use_container_width=True)

# 2. Reviews Total
elif bar_option == "Reviews Total":
    review_bins = list(range(0, 550000, 50000))
    review_labels = [f"{i//1000}k - {j//1000}k" for i, j in zip(review_bins[:-1], review_bins[1:])]
    df['Reviews.Bin'] = pd.cut(df['Reviews.Total'], bins=review_bins, labels=review_labels, right=False)
    data = df.groupby('Reviews.Bin').Title.count().reset_index(name="Total_Games")
    fig = px.bar(data, x='Reviews.Bin', y='Total_Games', labels={'Reviews.Bin': 'Reviews Range', 'Total_Games': 'Total Number of Games'})
    st.plotly_chart(apply_dark_layout(fig, "Number of Games vs Reviews Total", "Reviews Range", "Total Number of Games"), use_container_width=True)

# 3. Total Games Released Per Year
elif bar_option == "Total Games Released Per Year":
    year_counts = df['Release Year'].value_counts().reindex(range(1990, 2026), fill_value=0).sort_index()
    fig = chart_func(x=year_counts.index, y=year_counts.values, labels={'x': 'Year', 'y': 'Total Games Released'})
    st.plotly_chart(apply_dark_layout(fig, "Total Games Released Per Year", "Year", "Total Games Released"), use_container_width=True)

# 4. Total Revenue Per Year
elif bar_option == "Total Revenue Per Year":
    data = df.groupby('Release Year')['Revenue.Estimated'].sum().reindex(range(1990, 2026), fill_value=0).reset_index()
    fig = chart_func(data, x='Release Year', y='Revenue.Estimated', labels={'Release Year': 'Year', 'Revenue.Estimated': 'Total Revenue'})
    st.plotly_chart(apply_dark_layout(fig, "Total Revenue Per Year", "Year", "Total Revenue"), use_container_width=True)

# 5. Total Games Released Per Month
elif bar_option == "Total Games Released Per Month":
    df['Release Month'] = pd.to_datetime(df['Release.Date'], errors='coerce').dt.month
    month_counts = df['Release Month'].value_counts().reindex(range(1, 13), fill_value=0).sort_index()
    fig = chart_func(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                     y=month_counts.values, labels={'x': 'Month', 'y': 'Total Games Released'})
    st.plotly_chart(apply_dark_layout(fig, "Total Games Released Per Month", "Month", "Total Games Released"), use_container_width=True)

# 6. Total Revenue Per Month
elif bar_option == "Total Revenue Per Month":
    df['Release Month'] = pd.to_datetime(df['Release.Date'], errors='coerce').dt.month
    revenue_per_month = df.groupby('Release Month')['Revenue.Estimated'].sum().reindex(range(1, 13), fill_value=0)
    fig = chart_func(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                     y=revenue_per_month.values, labels={'x': 'Month', 'y': 'Total Revenue ($)'})
    st.plotly_chart(apply_dark_layout(fig, "Total Revenue Per Month", "Month", "Total Revenue ($)"), use_container_width=True)

# 7. Launch Price
elif bar_option == "Launch Price":
    price_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80]
    price_labels = [f"${price_bins[i]} - ${price_bins[i+1]}" for i in range(len(price_bins)-1)]
    df['Launch.Price.Bin'] = pd.cut(df['Launch.Price'], bins=price_bins, labels=price_labels, right=False)
    data = df.groupby('Launch.Price.Bin').Title.count().reset_index(name="Total_Games")
    fig = px.bar(data, x='Launch.Price.Bin', y='Total_Games',
                 labels={'Launch.Price.Bin': 'Launch Price Range', 'Total_Games': 'Total Number of Games'})
    st.plotly_chart(apply_dark_layout(fig, "Number of Games vs Launch Price", "Launch Price Range ($)", "Total Number of Games"), use_container_width=True)

# Pie Chart
st.markdown("<h3 style='text-align: center; color: white;'>🍰 Pie Charts</h3>", unsafe_allow_html=True)

chart_option = st.selectbox("Select a metric to visualize (Top 10 / Bottom 10 games):", [
    "Top 10 - Revenue Estimated", "Bottom 10 - Revenue Estimated",
    "Top 10 - Reviews Total", "Bottom 10 - Reviews Total"
], index=0)

# Define mapping for pie chart options
metric_map = {
    "Top 10 - Revenue Estimated": ('Revenue.Estimated', False, "Revenue Distribution of Top 10 Games"),
    "Bottom 10 - Revenue Estimated": ('Revenue.Estimated', True, "Revenue Distribution of Bottom 10 Games"),
    "Top 10 - Reviews Total": ('Reviews.Total', False, "Reviews Total Distribution of Top 10 Games"),
    "Bottom 10 - Reviews Total": ('Reviews.Total', True, "Reviews Total Distribution of Bottom 10 Games")
}

col, asc, title = metric_map[chart_option]
pie_data = df.sort_values(by=col, ascending=asc).head(10)
fig_pie = px.pie(pie_data, names='Title', values=col, title=title, template='plotly_dark')
fig_pie.update_layout(plot_bgcolor='#599cba', paper_bgcolor='#599cba', font_color='white')
st.plotly_chart(fig_pie, use_container_width=True)

# Histogram Section
st.markdown("<h3 style='text-align: center; color: white;'>📊 Histograms</h3>", unsafe_allow_html=True)

hist_option = st.selectbox("Select a metric to visualize in histogram:", [
    "Launch Price", "Revenue Estimated", "Reviews Total"
], index=0)

if hist_option == "Launch Price":
    bin_size = 5
    fig_hist = px.histogram(df, x='Launch.Price', 
                            nbins=int((df['Launch.Price'].max() - df['Launch.Price'].min()) / bin_size),
                            title="Histogram of Launch Price",
                            labels={'Launch.Price': 'Launch Price'}, 
                            template='plotly_dark')
    fig_hist.update_traces(xbins=dict(start=0, end=80, size=bin_size), marker=dict(color='white'))
elif hist_option == "Revenue Estimated":
    col_log = "Revenue.Estimated.Log"
    df[col_log] = np.log(df['Revenue.Estimated'] + 1)
    fig_hist = px.histogram(df, x=col_log, nbins=50,
                            title="Histogram of Revenue Estimated (Log Scale)",
                            labels={col_log: 'Log(Revenue Estimated)'}, 
                            template='plotly_dark')
    fig_hist.update_traces(marker=dict(color='white'))
else:  # Reviews Total
    col_log = "Reviews.Total.Log"
    df[col_log] = np.log(df['Reviews.Total'] + 1)
    fig_hist = px.histogram(df, x=col_log, nbins=50,
                            title="Histogram of Reviews Total (Log Scale)",
                            labels={col_log: 'Log(Reviews Total)'}, 
                            template='plotly_dark')
    fig_hist.update_traces(marker=dict(color='white'))

fig_hist.update_layout(plot_bgcolor='#599cba', paper_bgcolor='#599cba', font_color='white')
st.plotly_chart(fig_hist, use_container_width=True)