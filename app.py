import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO


# Helper function to extract fields by finding markers in text
def extract_field(text, field_name, end_marker="\n"):
    try:
        start = text.index(field_name) + len(field_name)
        end = text.index(end_marker, start)
        extracted_text = text[start:end].strip()

        # Replace newlines with spaces to format multiline addresses properly
        extracted_text = extracted_text.replace("\n", ", ")
        return extracted_text
    except ValueError:
        return None


# Helper function to check for multiple possible field names (like "Ship to:" or "Shipping address:")
def extract_field_multiple(text, field_names, end_marker="\n"):
    for field_name in field_names:
        result = extract_field(text, field_name, end_marker)
        if result:
            return result
    return None


# Function to extract specific fields from the PDF text
def extract_bill_data(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        pages = pdf.pages
        text = ''
        for page in pages:
            text += page.extract_text()

    # Extract fields with fallback between "Ship to:" and "Shipping address:"
    return {
        "Ship to / Shipping Address:": extract_field_multiple(text, ["Ship to:", "Shipping address:"],
                                                              end_marker="Phone"),
        "Order ID:": extract_field(text, "Order ID:"),
        "Phone:": extract_field(text, "Phone :"),
        "Seller Name:": extract_field(text, "Seller Name:"),
        "SKU:": extract_field(text, "SKU:")
    }


# Streamlit App Code
def process_pdfs(uploaded_files):
    data = []
    for uploaded_file in uploaded_files:
        file_data = extract_bill_data(uploaded_file)
        data.append(file_data)
    return pd.DataFrame(data)


st.title("Bill Data Extractor")

# File uploader to upload multiple PDF bills
uploaded_files = st.file_uploader("Choose PDF Bills", accept_multiple_files=True, type="pdf")

if st.button("Extract Data"):
    if uploaded_files:
        df = process_pdfs(uploaded_files)
        st.write(df)

        # Save extracted data to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Download button for the Excel file
        st.download_button(label="Download Excel", data=output, file_name="bills_data.xlsx")
    else:
        st.write("Please upload some PDF files.")
