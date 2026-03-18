import streamlit as st
import pandas as pd
from manipulation import DataEngine
from visualization import Visualization

# ── Page setup
st.set_page_config(page_title="DataLens", layout="wide")
st.title("🔬 DataLens | Smart Data Analyzer")

# ── File Upload
uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "xls"])

if uploaded_file is None:
    st.info("Upload a file to begin.")
    st.stop()

# ── Load Engine
if "engine" not in st.session_state or st.session_state.file_name != uploaded_file.name:
    engine = DataEngine(uploaded_file)
    st.session_state.engine = engine
    st.session_state.df_orig = engine.get_df().copy()
    st.session_state.file_name = uploaded_file.name

engine = st.session_state.engine
df = engine.get_df()

st.success(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── Layout Split
left, right = st.columns([2, 1])

# =========================
# LEFT SIDE (DATA)
# =========================
with left:

    st.subheader("📊 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Missing Values
    st.subheader("⚠️ Missing Values")
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) > 0:
        st.dataframe(missing, use_container_width=True)
    else:
        st.success("No missing values 🎉")

    # Potential Numeric
    st.subheader("🧠 Potential Numeric Columns")

    potential_numeric = []
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        ratio = converted.notna().sum() / len(df)
        if ratio > 0.7:
            potential_numeric.append(col)

    st.write(potential_numeric if potential_numeric else "None")

# =========================
# RIGHT SIDE (ACTIONS)
# =========================
with right:

    st.subheader("⚙️ Actions")

    if st.button("🚀 Auto Clean Dataset"):
        report = engine.auto_clean()
        st.success("Dataset cleaned!")
        st.json(report)
        st.rerun()

    if st.button("🧹 Remove Duplicates"):
        removed = engine.remove_duplicates()
        st.success(f"Removed {removed} duplicates")
        st.rerun()

    if st.button("♻️ Reset Dataset"):
        engine.set_df(st.session_state.df_orig)
        st.success("Dataset reset")
        st.rerun()

    st.divider()

    # Convert Column
    st.subheader("🔢 Convert Column")
    col_convert = st.selectbox("Select column", df.columns, key="convert_col")

    if st.button("Convert to Numeric"):
        result = engine.convert_to_numeric(col_convert)
        st.write(result)

        if result["action"] == "converted":
            st.success("Converted successfully")
        else:
            st.warning("Skipped (not enough numeric values)")

        st.rerun()

    st.divider()

    # Drop Column
    st.subheader("🗑️ Drop Column")
    col_drop = st.selectbox("Column to drop", df.columns, key="drop_col")

    if st.button("Drop Column"):
        engine.drop_column(col_drop)
        st.success(f"Dropped {col_drop}")
        st.rerun()

# =========================
# STATISTICS
# =========================
st.subheader("📈 Column Analysis")

col = st.selectbox("Select column", df.columns, key="stats_col")

if pd.api.types.is_numeric_dtype(df[col]):
    stats = engine.get_column_stats(col)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean", stats["Mean"])
    c2.metric("Median", stats["Median"])
    c3.metric("Min", stats["Min"])
    c4.metric("Max", stats["Max"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Std", stats["Std Dev"])
    c6.metric("Skew", stats["Skewness"])
    c7.metric("Kurtosis", stats["Kurtosis"])
    c8.metric("Count", stats["Count"])
else:
    st.dataframe(engine.get_value_counts(col), use_container_width=True)

# =========================
# VISUALIZATION
# =========================
st.subheader("📊 Visualization")

viz = Visualization(df)
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

chart_type = st.selectbox(
    "Select Chart Type",
    ["Bar", "Scatter", "Line", "Pie", "Box", "Heatmap"],
    key="chart_type"
)

if chart_type == "Bar":
    x = st.selectbox("X axis", df.columns, key="bar_x")
    y = st.multiselect("Y axis", numeric_cols, key="bar_y")
    if y:
        st.image(viz.bar_graph(x, y), use_container_width=True)

elif chart_type == "Scatter":
    x = st.selectbox("X axis", numeric_cols, key="sc_x")
    y = st.multiselect("Y axis", numeric_cols, key="sc_y")
    if y:
        st.image(viz.scatter_plot(x, y), use_container_width=True)

elif chart_type == "Line":
    x = st.selectbox("X axis", df.columns, key="ln_x")
    y = st.multiselect("Y axis", numeric_cols, key="ln_y")
    if y:
        st.image(viz.line_plot(x, y), use_container_width=True)

elif chart_type == "Pie":
    x = st.selectbox("Column", df.columns, key="pie_x")
    st.image(viz.pie_chart(x), use_container_width=True)

elif chart_type == "Box":
    x = st.multiselect("Columns", numeric_cols, key="box_x")
    if x:
        st.image(viz.box_plot(x), use_container_width=True)

elif chart_type == "Heatmap":
    x = st.multiselect("Columns", numeric_cols, default=numeric_cols[:5], key="hm_x")
    if x:
        st.image(viz.heatmap(x), use_container_width=True)