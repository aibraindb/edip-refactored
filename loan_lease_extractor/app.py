
import streamlit as st
import json
import tempfile
from extractor import extract

st.set_page_config(page_title="Loan/Lease Dynamic Extractor", page_icon="📄", layout="wide")

st.title("📄 Loan/Lease Dynamic Schema Extractor")
st.caption("Upload a PDF (loan or lease agreement). The app will extract key–value fields and build a dynamic schema.")

with st.sidebar:
    st.header("Settings")
    hints_file = st.file_uploader("Optional: Hints JSON", type=["json"], help="Upload a JSON with regex hints for fields.")
    show_text = st.checkbox("Show extracted text", value=False)

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded is not None:
    # persist uploaded file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded.read())
        pdf_path = tmp.name
    # persist hints if provided
    hints_path = ""
    if hints_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as hj:
            hj.write(hints_file.read())
            hints_path = hj.name
    try:
        result = extract(pdf_path, hints_path)
        st.success("Extraction complete.")
        col1, col2 = st.columns([1,1])
        with col1:
            st.subheader("Dynamic Schema")
            st.json(result.dynamic_schema)
        with col2:
            st.subheader("Fields (flat list)")
            as_rows = [f.__dict__ for f in result.fields]
            st.dataframe(as_rows, use_container_width=True)
        if show_text:
            st.subheader("Raw Text by Page")
            for i, t in enumerate(result.text_by_page, start=1):
                with st.expander(f"Page {i}"):
                    st.text(t or "")
        st.info("Tip: Provide a custom hints JSON to improve recall/precision for your templates.")
    except Exception as e:
        st.error(f"Extraction failed: {e}")
else:
    st.markdown("> Upload a PDF from the sample docs or your own. For best results, provide a hints JSON.")

st.markdown("---")
st.caption("Next: Extend to invoices by adding invoice-specific hints and post-processing.")
