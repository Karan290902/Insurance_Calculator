# ============================================
# IMPORT LIBRARIES
# ============================================

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Insurance Premium Calculator",
    page_icon="💰",
    layout="wide"
)

# ============================================
# TITLE
# ============================================

st.title("💰 Group Term Life Insurance Premium Calculator")

st.markdown(
    "Upload any insurance Excel file for automatic premium calculation"
)

# ============================================
# SETTINGS
# ============================================

RATE_PER_LAKH = 320.3

GST_RATE = 0.18

# ============================================
# FILE UPLOAD
# ============================================

uploaded_file = st.file_uploader(
    "📂 Upload Excel File",
    type=["xlsx"]
)

# ============================================
# PROCESS FILE
# ============================================

if uploaded_file is not None:

    try:

        # ============================================
        # READ EXCEL FILE
        # ============================================

        df = pd.read_excel(uploaded_file)

        # ============================================
        # CLEAN COLUMN NAMES
        # ============================================

        df.columns = df.columns.str.strip()

        # ============================================
        # SHOW UPLOADED DATA
        # ============================================

        st.subheader("📄 Uploaded Data")

        st.dataframe(df.head())

        # ============================================
        # DYNAMIC COLUMN DETECTION
        # ============================================

        column_mapping = {}

        for col in df.columns:

            lower_col = str(col).strip().lower()

            # NAME
            if (

                'name' in lower_col

                or 'customer' in lower_col

                or 'borrower' in lower_col

                or 'member' in lower_col

            ):

                column_mapping['Name'] = col

            # MOBILE
            elif (

                'mobile' in lower_col

                or 'phone' in lower_col

                or 'contact' in lower_col

                or 'mob no' in lower_col

            ):

                column_mapping['Mobile No'] = col

            # AGE
            elif (

                lower_col == 'age'

                or 'member age' in lower_col

                or 'main member age' in lower_col

            ):

                column_mapping['Age'] = col

            # SUM ASSURED
            elif (

                'sum assured' in lower_col

                or 'sum insured' in lower_col

                or lower_col == 'sa'

                or 'coverage amount' in lower_col

            ):

                column_mapping['Sum Assured'] = col

            # PREMIUM EXCL GST
            elif (

                'premium excl' in lower_col

                or 'premium without gst' in lower_col

                or 'premium excl gst' in lower_col

            ):

                column_mapping['Premium Excl GST'] = col

            # GST
            elif (

                lower_col == 'gst'

                or 'gst amount' in lower_col

                or 'tax' in lower_col

            ):

                column_mapping['GST Amount'] = col

            # TOTAL PREMIUM
            elif (

                'total premium' in lower_col

                or 'premium incl gst' in lower_col

                or 'gross premium' in lower_col

            ):

                column_mapping['Premium + GST'] = col

            # LOAN ACCOUNT NUMBER
            elif (

                'loan account' in lower_col

                or 'account no' in lower_col

                or 'loan no' in lower_col

            ):

                column_mapping['Loan Account No'] = col

            # LOAN OUTSTANDING
            elif (

                'loan outstanding' in lower_col

                or 'outstanding amount' in lower_col

            ):

                column_mapping['Loan Outstanding Amount'] = col

            # GENDER
            elif (

                'gender' in lower_col

                or 'sex' in lower_col

            ):

                column_mapping['Gender'] = col

            # DOB
            elif (

                'dob' in lower_col

                or 'date of birth' in lower_col

            ):

                column_mapping['DOB'] = col

            # RATE
            elif (

                lower_col == 'rate'

                or 'premium rate' in lower_col

            ):

                column_mapping['Rate'] = col

        # ============================================
        # CREATE STANDARD COLUMNS
        # ============================================

        standard_columns = [

            'Name',

            'Mobile No',

            'Age',

            'Sum Assured',

            'Premium Excl GST',

            'GST Amount',

            'Premium + GST',

            'Loan Account No',

            'Loan Outstanding Amount',

            'Gender',

            'DOB',

            'Rate'

        ]

        for std_col in standard_columns:

            if std_col in column_mapping:

                df[std_col] = df[
                    column_mapping[std_col]
                ]

            else:

                df[std_col] = ""

        # ============================================
        # CLEAN NUMERIC COLUMNS
        # ============================================

        numeric_cols = [

            'Sum Assured',

            'Premium Excl GST',

            'GST Amount',

            'Premium + GST',

            'Loan Outstanding Amount',

            'Rate',

            'Age'

        ]

        for col in numeric_cols:

            df[col] = pd.to_numeric(

                df[col],

                errors='coerce'

            ).fillna(0)

        # ============================================
        # CREATE SIMPLE ML RISK SCORE
        # ============================================

        df['Risk Score'] = (

            (df['Sum Assured'] / 100000)

            +

            (df['Loan Outstanding Amount'] / 100000)

        )

        # ============================================
        # ML MODEL
        # ============================================

        X = df[[

            'Sum Assured',

            'Loan Outstanding Amount'

        ]]

        y = df['Risk Score']

        X_train, X_test, y_train, y_test = train_test_split(

            X,

            y,

            test_size=0.2,

            random_state=42

        )

        model = RandomForestRegressor(
            random_state=42
        )

        model.fit(
            X_train,
            y_train
        )

        # ============================================
        # PREDICT RISK
        # ============================================

        df['Predicted Risk'] = model.predict(X)

        # ============================================
        # PREMIUM CALCULATION
        # ============================================

        df['Premium Excl GST'] = (

            (df['Sum Assured'] / 100000)

            *

            RATE_PER_LAKH

        )

        # ============================================
        # GST CALCULATION
        # ============================================

        df['GST Amount'] = (

            df['Premium Excl GST']

            *

            GST_RATE

        )

        df['Premium + GST'] = (

            df['Premium Excl GST']

            +

            df['GST Amount']

        )

        # ============================================
        # FINAL OUTPUT
        # ============================================

        final_df = df[[

            'Loan Account No',

            'Name',

            'Mobile No',

            'Age',

            'Gender',

            'Sum Assured',

            'Premium Excl GST',

            'GST Amount',

            'Premium + GST',

            'Predicted Risk'

        ]]

        # ============================================
        # PORTFOLIO SUMMARY
        # ============================================

        st.subheader("📊 Portfolio Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Members",
                len(final_df)
            )

        with col2:

            st.metric(
                "Total Sum Assured",
                f"₹ {final_df['Sum Assured'].sum():,.0f}"
            )

        with col3:

            st.metric(
                "Premium Excl GST",
                f"₹ {final_df['Premium Excl GST'].sum():,.2f}"
            )

        with col4:

            st.metric(
                "Premium Incl GST",
                f"₹ {final_df['Premium + GST'].sum():,.2f}"
            )

        # ============================================
        # SHOW OUTPUT
        # ============================================

        st.subheader("📋 Premium Calculation Output")

        st.dataframe(
            final_df,
            use_container_width=True
        )

        # ============================================
        # DOWNLOAD OUTPUT
        # ============================================

        output_file = "Premium_Output.xlsx"

        final_df.to_excel(
            output_file,
            index=False
        )

        with open(output_file, "rb") as file:

            st.download_button(
                label="⬇ Download Output Excel",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:

        st.error(f"Error: {e}")

# ============================================
# FOOTER
# ============================================

st.markdown("---")

st.caption(
    "Group Term Life Insurance Premium Calculator"
)