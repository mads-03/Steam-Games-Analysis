import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import norm

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

# Load and clean dataset
df = pd.read_csv("games.csv")
df.columns = df.columns.str.strip()
df["Revenue.Estimated"] = pd.to_numeric(df["Revenue.Estimated"], errors="coerce")
df["Reviews.Total"] = pd.to_numeric(df["Reviews.Total"], errors="coerce")
df.dropna(subset=["Revenue.Estimated", "Reviews.Total"], inplace=True)

# Log transform
df["Transformed_Revenue"] = np.log1p(df["Revenue.Estimated"])
df["Transformed_Reviews"] = np.log1p(df["Reviews.Total"])

st.markdown("<h1 style='text-align: center;'>📊 Probability Distributions</h1>", unsafe_allow_html=True)

# Reusable plot + stats display
def plot_and_display_distribution(data, title, label):
    mean, std = norm.fit(data)
    x = np.linspace(data.min(), data.max(), 100)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(data, bins=50, stat="density", color="#007bb3", ax=ax)
    ax.plot(x, norm.pdf(x, mean, std), 'k', lw=2)
    ax.set(title=title, xlabel=label, ylabel="Density")
    st.pyplot(fig)
    stats_df = pd.DataFrame({"Measure": ["Mean (μ)", "Standard Deviation (σ)"],
                             "Value": [f"{mean:.2f}", f"{std:.2f}"]})
    st.dataframe(stats_df, use_container_width=True)
    return mean, std

# Revenue distribution
st.subheader("📈 Log-Transformed Revenue Estimated Distribution")
mean_rev, std_rev = plot_and_display_distribution(df["Transformed_Revenue"],
                                                  "Revenue Distribution with Normal Fit",
                                                  "Log Revenue")

# Revenue probability estimates
p1 = norm.cdf(np.log1p(1_000_000), loc=mean_rev, scale=std_rev)
p2 = 1 - p1
p3 = norm.cdf(np.log1p(7_500_000), loc=mean_rev, scale=std_rev) - norm.cdf(np.log1p(2_500_000), loc=mean_rev, scale=std_rev)
st.write("### Revenue Probability Estimates (based on log-normal distribution)")
st.write(f"1. **P(Revenue < `$1.00M`)** ≈ {p1:.4f}")
st.write(f"2. **P(Revenue > `$1.00M`)** ≈ {p2:.4f}")
st.write(f"3. **P(`$2.50M` < Revenue < `$7.50M`)** ≈ {p3:.4f}")

# Reviews distribution
st.subheader("📝 Log-Transformed Reviews Total Distribution")
plot_and_display_distribution(df["Transformed_Reviews"],
                              "Reviews Distribution with Normal Fit",
                              "Log Reviews")