import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

# Page settings
st.set_page_config(page_title="Zomato Dashboard", layout="wide")

# Load data
df = pd.read_csv("zomato.csv", encoding="latin-1")
df.dropna(subset=["Cuisines"], inplace=True)
df.columns = df.columns.str.lower().str.replace(" ", "_")

st.title("🍽️ Zomato Restaurant Rating Dashboard")

# ──────────────────────────────
# Sidebar Filters
# ──────────────────────────────
st.sidebar.header("🔍 Filters")

# 1. City Selection
selected_city = st.sidebar.selectbox("Choose City", sorted(df["city"].unique()))
df_city = df[df["city"] == selected_city]

# 2. Rating Filter
min_rating = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=3.5, step=0.1)

# 3. Cost Filter
max_cost = int(df_city["average_cost_for_two"].max())
cost_range = st.sidebar.slider("Cost for Two (₹)", 0, max_cost, (200, 1000))

# 4. Cuisine Filter
all_cuisines = df_city["cuisines"].dropna().apply(lambda x: [c.strip() for c in x.split(",")])
flat_cuisines = sorted(set([c for sublist in all_cuisines for c in sublist]))
selected_cuisines = st.sidebar.multiselect("Choose Cuisines", flat_cuisines, default=flat_cuisines[:3])

# Filtering function
def cuisine_match(cuisine_str):
    try:
        return any(c in cuisine_str for c in selected_cuisines)
    except:
        return False

# Apply all filters
filtered_df = df_city[
    (df_city["aggregate_rating"] >= min_rating) &
    (df_city["average_cost_for_two"].between(cost_range[0], cost_range[1])) &
    (df_city["cuisines"].apply(cuisine_match))
]

# Show warning if empty
if filtered_df.empty:
    st.warning("🚫 No data matches the selected filters. Try changing filter values.")
else:
    # ──────────────────────────────
    # Top Cuisines Chart
    # ──────────────────────────────
    st.subheader(f"🍛 Top 10 Cuisines in {selected_city}")

    cuisines_split = filtered_df['cuisines'].apply(lambda x: x.split(','))
    flat_list = [item.strip() for sublist in cuisines_split for item in sublist]
    top_cuisines = pd.Series(Counter(flat_list)).sort_values(ascending=False).head(10)

    fig1, ax1 = plt.subplots()
    sns.barplot(x=top_cuisines.values, y=top_cuisines.index, ax=ax1)
    ax1.set_xlabel("Count")
    ax1.set_ylabel("Cuisine")
    st.pyplot(fig1)

    # ──────────────────────────────
    # Cost vs Rating
    # ──────────────────────────────
    st.subheader("💰 Cost for Two vs Rating")
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=filtered_df, x="average_cost_for_two", y="aggregate_rating", ax=ax2)
    ax2.set_xlabel("Average Cost for Two (₹)")
    ax2.set_ylabel("Aggregate Rating")
    st.pyplot(fig2)

    # ──────────────────────────────
    # Online Delivery vs Rating
    # ──────────────────────────────
    st.subheader("🛵 Online Delivery vs Ratings")
    fig3, ax3 = plt.subplots()
    sns.boxplot(data=filtered_df, x="has_online_delivery", y="aggregate_rating", ax=ax3)
    st.pyplot(fig3)

    # ──────────────────────────────
    # Votes vs Rating
    # ──────────────────────────────
    st.subheader("👍 Votes vs Aggregate Rating")
    fig4, ax4 = plt.subplots()
    sns.scatterplot(data=filtered_df, x="votes", y="aggregate_rating", ax=ax4)
    ax4.set_xlabel("Votes")
    ax4.set_ylabel("Rating")
    st.pyplot(fig4)

    # ──────────────────────────────
    # Data Table Preview
    # ──────────────────────────────
    st.subheader("📄 Filtered Data Preview")
    st.dataframe(filtered_df.head(20))

# Footer
st.markdown("---")
st.markdown("✅ Built using Python • Streamlit • Pandas • Seaborn • Matplotlib")
