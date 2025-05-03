import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

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

st.markdown("<h1 style='text-align: center;'>📈 Linear Regression</h1>", unsafe_allow_html=True)

# Load data
df = pd.read_csv('games.csv')

# Display name mapping
col_map = {
    "Reviews.Total": "Reviews Total",
    "Launch.Price": "Launch Price",
    "Revenue.Estimated": "Revenue Estimated"
}

# Feature selection
feature_display = st.selectbox("Select Feature", [col_map["Reviews.Total"], col_map["Launch.Price"]])
selected_feature = [k for k, v in col_map.items() if v == feature_display][0]

# IQR filtering
def iqr_filter(data, cols):
    for col in cols:
        Q1, Q3 = data[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        data = data[(data[col] >= Q1 - 1.5 * IQR) & (data[col] <= Q3 + 1.5 * IQR)]
    return data

cols = list(col_map.keys())
df_filtered = iqr_filter(df.copy(), cols)

# Regression
X = df_filtered[[selected_feature]]
y = df_filtered["Revenue.Estimated"]
model = LinearRegression().fit(X, y)
y_pred = model.predict(X)

# Sort X for proper dotted line plotting
sorted_idx = X[selected_feature].argsort().values
X_sorted = X.iloc[sorted_idx]
y_pred_sorted = y_pred[sorted_idx]
y_sorted = y.iloc[sorted_idx]

# Plot scatter + regression line
st.subheader(f"{feature_display} vs Revenue Estimated")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(X, y, alpha=0.5, color='blue', label='Data')
ax.plot(X_sorted, y_pred_sorted, linestyle='--', color='red', label='Regression Line')
ax.set_xlabel(feature_display)
ax.set_ylabel("Revenue Estimated")
ax.legend()
st.pyplot(fig)

# Show covariance
cov = np.cov(X[selected_feature], y)[0, 1]
st.markdown(f"**Covariance:** {cov:.4f}")

# Show correlation
corr = X[selected_feature].corr(y)
st.markdown(f"**Correlation:** {corr:.4f}")

# Correlation matrix
st.subheader("Correlation Matrix (Filtered)")
corr_matrix = df_filtered[cols].corr()
fig2, ax2 = plt.subplots()
cax = ax2.matshow(corr_matrix, cmap='coolwarm')
fig2.colorbar(cax)
ticks = range(len(corr_matrix.columns))
ax2.set_xticks(ticks); ax2.set_yticks(ticks)
ax2.set_xticklabels(corr_matrix.columns, rotation=90)
ax2.set_yticklabels(corr_matrix.columns)
for (i, j), val in np.ndenumerate(corr_matrix.values):
    ax2.text(j, i, f"{val:.2f}", ha='center', va='center')
st.pyplot(fig2)

# Display regression equation and interpretation
B0, B1 = model.intercept_, model.coef_[0]
st.subheader("Regression Equation")
st.markdown(f"`Revenue Estimated = {B0:.2f} + {B1:.2f} × {feature_display}`")

explanation = {
    "Reviews.Total": "each additional review is associated with",
    "Launch.Price": "each unit increase in price is associated with"
}
st.markdown(f"Based on the model, {explanation[selected_feature]} an estimated increase of **{B1:.2f}** in revenue.")