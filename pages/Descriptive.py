import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats

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

# Title
st.markdown("<h1 style='text-align: center;'>🧾 Descriptive Statistics</h1>", unsafe_allow_html=True)

# Load and clean data
df = pd.read_csv("games.csv")
df.columns = df.columns.str.strip()

# Column selection
column_map = {
    "Revenue Estimated": "Revenue.Estimated",
    "Reviews Total": "Reviews.Total",
    "Launch Price": "Launch.Price"
}
display_col = st.selectbox("Select a variable:", list(column_map.keys()))
col = pd.to_numeric(df[column_map[display_col]], errors='coerce').dropna()

# Central Tendency and Dispersion
mean, median, std, var = col.mean(), col.median(), col.std(), col.var()
rng, q1, q3 = col.max() - col.min(), col.quantile(0.25), col.quantile(0.75)
iqr = q3 - q1

# Confidence Interval (95%)
n = len(col)
se = std / (n ** 0.5)
z = stats.norm.ppf(0.975)  # 95% confidence
ci_lower, ci_upper = mean - z * se, mean + z * se

# 3-Sigma and Outlier Bounds
lower_3sd, upper_3sd = mean - 3*std, mean + 3*std
lower_out, upper_out = q1 - 1.5*iqr, q3 + 1.5*iqr

# Central Tendency
st.subheader("📌 Central Tendency")
st.dataframe(pd.DataFrame({"Measure": ["Mean", "Median"], "Value": [f"{mean:,.2f}", f"{median:,.2f}"]}), use_container_width=True)

# Dispersion
st.subheader("📊 Dispersion")
st.dataframe(pd.DataFrame({
    "Measure": ["Range", "Variance", "Standard Deviation"],
    "Value": [f"{rng:,.2f}", f"{var:,.2f}", f"{std:,.2f}"]
}), use_container_width=True)

# 3-Sigma
st.markdown(f"### 3-Sigma Interval:\n- **{display_col} lies between:** {mean:,.2f} ± {3*std:,.2f}")

# IQR & Quartiles
st.subheader("📊 IQR and Outliers")
st.dataframe(pd.DataFrame({
    "Percentile": ["Q1 (25%)", "Q2 (Median)", "Q3 (75%)"],
    "Value": [f"{q1:,.2f}", f"{median:,.2f}", f"{q3:,.2f}"]
}), use_container_width=True)
st.markdown(f"- **IQR:** {iqr:,.2f}  \n- **Median ± IQR:** {median:,.2f} ± {iqr:,.2f}")

# Outlier Bounds
st.markdown(f"### Outlier Bounds:\n- **Lower:** {lower_out:,.2f}  \n- **Upper:** {upper_out:,.2f}")

# Confidence Interval
st.subheader("📐 Confidence Interval (95%)")
st.markdown(
    f"""
    The 95% confidence interval for the mean of **{display_col}** is:
    
    ### **{ci_lower:,.2f} to {ci_upper:,.2f}**

    This means we're 95% confident the true average of this variable lies within this range.
    """
)

# Box Plot
st.subheader("📊 Box Plot")
show_outliers = st.checkbox("Show outliers", value=False)
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(data=col, ax=ax, color='skyblue', showfliers=show_outliers)
ax.set_title(f"Box Plot of {display_col} ({'With' if show_outliers else 'Without'} Outliers)")
ax.set_ylabel(display_col)
st.pyplot(fig)