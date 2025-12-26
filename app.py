# app.py - Full Streamlit Deployment (Single File)

import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
import tempfile
from openpyxl import Workbook

# -------------------------------------------------
# PAGE SETTINGS
# -------------------------------------------------
st.set_page_config(page_title="TAX Report Generator", layout="wide")

st.title("📄 TAX REPORT GENERATOR")
st.write("Upload your files below and click **Generate Report** to create Tax Summary.")

# -------------------------------------------------
# FILE UPLOAD SECTION
# -------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload CSV / XLSX / ZIP / PDF files",
    type=["csv", "xlsx", "zip", "pdf"],
    accept_multiple_files=True
)

# -------------------------------------------------
# MAIN PROCESSING FUNCTION
# -------------------------------------------------
def generate_tax_report(file_storage):
    """Processes all uploaded files and outputs a single Excel Tax Report."""

    temp_dir = tempfile.mkdtemp()
    extracted_files = []

    # STEP A: Save uploaded files / Extract ZIPs
    for filename, content in file_storage.items():
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)

        if filename.lower().endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

    # STEP B: Collect CSV/XLSX file paths for processing
    source_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
                    if f.lower().endswith((".csv", ".xlsx"))]

    all_data = []

    # STEP C: Load files & clean
    for file in source_files:
        try:
            if file.lower().endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            # BASIC NORMALIZATION EXAMPLES
            df.columns = df.columns.str.strip().str.title()
            all_data.append(df)

        except Exception as e:
            print("File processing skipped:", file, e)

    if not all_data:
        raise ValueError("No usable CSV/XLSX found after upload.")

    master = pd.concat(all_data, ignore_index=True)

    # -------------------------------------------------
    # *** YOUR CUSTOM LOGIC AREA ***
    # Replace/extend based on your notebook logic:
    # -------------------------------------------------
    # Example transformation (change this to your own rules):
    if "Date" in master.columns:
        master["Date"] = pd.to_datetime(master["Date"], errors="coerce")

    # example cleanup
    numeric_cols = master.select_dtypes(include=["float", "int"]).columns
    master[numeric_cols] = master[numeric_cols].fillna(0)

    # -------------------------------------------------
    # RETURN FINAL REPORT AS BYTES
    # -------------------------------------------------
    output = BytesIO()
    master.to_excel(output, index=False, sheet_name="Tax Report")
    output.seek(0)
    return output, master

# -------------------------------------------------
# PROCESS BUTTON
# -------------------------------------------------
if st.button("🚀 Generate Report"):
    if not uploaded_files:
        st.error("❌ Please upload files first!")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    # Convert uploads to dict
    status.write("📥 Reading files...")
    file_storage = {file.name: file.read() for file in uploaded_files}
    progress.progress(25)

    # Run main logic
    status.write("⚙️ Processing... please wait.")
    try:
        report_bytes, preview_df = generate_tax_report(file_storage)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.stop()

    progress.progress(75)
    status.write("📦 Preparing download...")

    # Download Button
    st.success("🎉 Report successfully generated!")
    st.download_button(
        label="📥 Download TAX_REPORT.xlsx",
        data=report_bytes,
        file_name="TAX_REPORT.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    progress.progress(100)
    status.write("✅ Done!")
    st.dataframe(preview_df.head(20))  # Quick preview table

