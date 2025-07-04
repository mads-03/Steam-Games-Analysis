import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression  # Imports the LinearRegression model class used to perform simple or multiple linear regression

st.markdown("<h1 style='text-align: center;'>📈 Linear Regression</h1>", unsafe_allow_html=True)    # Titles & Styling
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

# Load data & select feature
df = pd.read_csv('games.csv')
col_map = {
    "Reviews.Total": "Reviews Total",
    "Launch.Price": "Launch Price",
    "Revenue.Estimated": "Revenue Estimated"
}
features = list(col_map.keys())
display_feature = st.selectbox("Select Feature", [col_map[f] for f in features[:-1]])
selected_feature = [k for k, v in col_map.items() if v == display_feature][0]

# Apply IQR
def iqr_filter(data, cols):
    for col in cols:
        Q1, Q3 = data[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        data = data[(data[col] >= Q1 - 1.5 * IQR) & (data[col] <= Q3 + 1.5 * IQR)]
    return data
df_filtered = iqr_filter(df.copy(), features)

# Linear Regression & Plot
X = df_filtered[[selected_feature]]
y = df_filtered["Revenue.Estimated"]
model = LinearRegression().fit(X, y)
y_pred = model.predict(X)
sorted_idx = X[selected_feature].argsort()
X_sorted, y_sorted, y_pred_sorted = X.iloc[sorted_idx], y.iloc[sorted_idx], y_pred[sorted_idx]
st.subheader(f"{display_feature} vs Revenue Estimated (IQR Filtered)")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(X, y, alpha=0.5, color='blue', label='Data')
ax.plot(X_sorted, y_pred_sorted, '--', color='red', label='Regression Line')
ax.set_xlabel(display_feature)
ax.set_ylabel("Revenue Estimated")
ax.legend()
st.pyplot(fig)

# Covariance and Correlation
cov = np.cov(X[selected_feature], y)[0, 1]
corr = X[selected_feature].corr(y)
st.markdown(f"**Covariance:** {cov:.4f}")
st.markdown(f"**Correlation:** {corr:.4f}")

# Correlation Matrix
st.subheader("Correlation Matrix (IQR Filtered)")
corr_matrix = df_filtered[features].corr()
fig2, ax2 = plt.subplots()
cax = ax2.matshow(corr_matrix, cmap='coolwarm')
fig2.colorbar(cax)
ticks = range(len(features))
ax2.set_xticks(ticks); ax2.set_yticks(ticks)
ax2.set_xticklabels(features, rotation=90)
ax2.set_yticklabels(features)
for (i, j), val in np.ndenumerate(corr_matrix.values):
    ax2.text(j, i, f"{val:.2f}", ha='center', va='center')
st.pyplot(fig2)

# Linear Regression Equation
B0, B1 = model.intercept_, model.coef_[0]
st.subheader("Linear Regression Equation")
st.markdown(f"`Revenue Estimated = {B0:.2f} + {B1:.2f} × {display_feature}`")
explanation = {
    "Reviews.Total": "each additional review is associated with",
    "Launch.Price": "each unit increase in price is associated with"
}
st.markdown(f"Based on the model, {explanation[selected_feature]} an estimated increase of **{B1:.2f}** in revenue.")