import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Load JSON data (Replace this with actual data loading)
with open("gcp_inventory.json", "r") as f:
    data = json.load(f)

df = pd.json_normalize(data)
df.columns = df.columns.str.lower()  # Standardize column names

# Convert numeric columns
num_cols = ["vcpu", "ram", "daily_cost"]
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Sidebar filters with search & select
st.sidebar.header("Filters")

# Add "Select All" option by default (meaning no filter applied)
selected_project = st.sidebar.multiselect(
    "Select Project", options=["All"] + list(df["project_name"].unique()), default=["All"]
)

selected_type = st.sidebar.multiselect(
    "Select Type", options=["All"] + list(df["type"].unique()), default=["All"]
)

selected_machine = st.sidebar.multiselect(
    "Select Machine Type", options=["All"] + list(df["machine_type"].unique()), default=["All"]
)

selected_hod = st.sidebar.multiselect(
    "Select HOD", options=["All"] + list(df["hod"].unique()), default=["All"]
)

# Apply filters dynamically
filtered_df = df.copy()

# If "All" is selected, use the entire set of available values
if "All" not in selected_project:
    filtered_df = filtered_df[filtered_df["project_name"].isin(selected_project)]

if "All" not in selected_type:
    filtered_df = filtered_df[filtered_df["type"].isin(selected_type)]

if "All" not in selected_machine:
    filtered_df = filtered_df[filtered_df["machine_type"].isin(selected_machine)]

if "All" not in selected_hod:
    filtered_df = filtered_df[filtered_df["hod"].isin(selected_hod)]

# Convert costs to INR (1 USD = 83 INR, adjust as necessary)
filtered_df['daily_cost_inr'] = filtered_df['daily_cost'] * 83

# Display filtered data
st.write(f"Showing {len(filtered_df)} results")
st.dataframe(filtered_df)

# Display top VMs by Cost, vCPU, RAM
st.subheader("Top 10 VMs by Cost")
st.dataframe(filtered_df.nlargest(10, "daily_cost_inr")[["instance_name", "daily_cost_inr"]])

st.subheader("Top 10 VMs by vCPU & RAM")
st.dataframe(filtered_df.nlargest(10, "vcpu")[["instance_name", "vcpu", "ram"]])

# Metrics & Summary
st.sidebar.metric("Total VMs", len(filtered_df))
st.sidebar.metric("Total Cost (INR)", f"₹{filtered_df['daily_cost_inr'].sum():,.2f}")

# Add the charts in a two-column layout
# VMs per Type (Pie Chart)
st.write("### 🖥️ VMs per Type")
fig_type = px.pie(filtered_df, names="type", title="VM Distribution by Type", color_discrete_sequence=px.colors.qualitative.Set3)
st.plotly_chart(fig_type)

# VMs per Machine Type (Bar Chart)
st.write("### ⚙️ VMs per Machine Type")
fig_machine = px.bar(filtered_df, x="machine_type", title="VM Count per Machine Type", color="machine_type", text_auto=True)
st.plotly_chart(fig_machine)

 # VMs Cost per HOD (Bar Chart)
st.write("### 💰 VMs Cost per HOD")
fig_cost_hod = px.bar(filtered_df, x="hod", y="daily_cost", title="Daily Cost per HOD", color="hod", text_auto=True)
st.plotly_chart(fig_cost_hod)

# Total Costs per Machine Type per HOD (Sunburst Chart)
st.write("### 🏷️ Total Costs per Machine Type per HOD")
fig_cost_machine_hod = px.sunburst(filtered_df, path=["hod", "machine_type"], values="daily_cost", title="Cost Breakdown by HOD & Machine Type")
st.plotly_chart(fig_cost_machine_hod)
