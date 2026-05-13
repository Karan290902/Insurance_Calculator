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
# CUSTOM CSS
# ============================================

st.markdown("""

<style>

.main {
    background-color: #f4f7fb;
}

.block-container {
    padding-top: 2rem;
}

/* HEADINGS */

h1 {
    color: #0F172A !important;
    font-weight: 800;
}

h2, h3 {
    color: #1E293B !important;
}

/* NORMAL TEXT */

p, label, div {
    color: #334155;
}

/* METRIC CARDS */

[data-testid="metric-container"] {
    background: white;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #dbeafe;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* DATAFRAME */

.stDataFrame {
    background-color: white;
    border-radius: 12px;
}

/* BUTTON */

div.stDownloadButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

/* HEADER BOX */

.upload-box {
    background: linear-gradient(
        135deg,
        #dbeafe,
        #eff6ff
    );

    padding: 25px;

    border-radius: 20px;

    border: 1px solid #bfdbfe;

    margin-bottom: 20px;
}

/* HEADER TEXT */

.upload-box h1 {
    color: #0F172A !important;
}

.upload-box p {
    color: #334155 !important;
    font-size: 18px;
    line-height: 1.7;
}

/* CHECKMARK TEXT */

.upload-box ul li {
    color: #1E293B !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #EFF6FF;
}

</style>

""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

st.markdown("""

<div class="upload-box">

<h1>💰 Group Term Life Insurance Premium Calculator</h1>

<p style="font-size:18px; color:#475569;">

Upload insurance Excel files and automatically calculate:

✅ Premium  
✅ GST  
✅ Total Premium  
✅ ML Risk Prediction  

</p>

</div>

""", unsafe_allow_html=True)

# ============================================
# SETTINGS
# ============================================

RATE_PER_LAKH = 320.3

GST_RATE = 0.18

# ============================================
# FILE UPLOAD
# ============================================

uploaded_file = st.file_uploader(
    "📂 Upload Insurance Excel File",
    type=["xlsx"]
)

# ============================================
# PROCESS FILE
# ============================================

if uploaded_file is not None:

    try:

        # ============================================
        # READ FILE
        # ============================================

        df = pd.read_excel(uploaded_file)

        # CLEAN COLUMN NAMES
        df.columns = df.columns.str.strip()

        # ============================================
        # SHOW RAW DATA
        # ============================================

        with st.expander("📄 View Uploaded Data"):

            st.dataframe(df.head())

        # ============================================
        # DYNAMIC COLUMN DETECTION
        # ============================================

        column_mapping = {}

        for col in df.columns:

            lower_col = str(col).strip().lower()

            # ============================================
            # NAME
            # ============================================

            if (

                'customer name' in lower_col

                or 'member name' in lower_col

                or 'borrower name' in lower_col

                or 'insured name' in lower_col

                or lower_col == 'name'

            ):

                column_mapping['Name'] = col

            # ============================================
            # MOBILE
            # ============================================

            elif (

                'mobile' in lower_col

                or 'phone' in lower_col

                or 'contact' in lower_col

            ):

                column_mapping['Mobile No'] = col

            # ============================================
            # AGE
            # ============================================

            elif (

                lower_col == 'age'

                or 'member age' in lower_col

                or 'main member age' in lower_col

                or 'customer age' in lower_col

            ):

                column_mapping['Age'] = col

            # ============================================
            # SUM ASSURED
            # ============================================

            elif (

                'sum assured' in lower_col

                or 'sum insured' in lower_col

                or lower_col == 'sa'

            ):

                column_mapping['Sum Assured'] = col

            # ============================================
            # LOAN ACCOUNT NUMBER
            # ============================================

            elif (

                'loan account' in lower_col

                or 'account no' in lower_col

                or 'loan no' in lower_col

            ):

                column_mapping['Loan Account No'] = col

            # ============================================
            # LOAN OUTSTANDING
            # ============================================

            elif (

                'loan outstanding' in lower_col

                or 'outstanding amount' in lower_col

            ):

                column_mapping['Loan Outstanding Amount'] = col

            # ============================================
            # GENDER
            # ============================================

            elif (

                'gender' in lower_col

                or 'sex' in lower_col

            ):

                column_mapping['Gender'] = col

        # ============================================
        # SHOW DETECTED COLUMNS
        # ============================================

        st.subheader("🧠 Detected Columns")

        st.write(column_mapping)

        # ============================================
        # CREATE STANDARD COLUMNS
        # ============================================

        standard_columns = [

            'Name',

            'Mobile No',

            'Age',

            'Sum Assured',

            'Loan Account No',

            'Loan Outstanding Amount',

            'Gender'

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

            'Loan Outstanding Amount',

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
        # DASHBOARD
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
        # SEARCH BAR
        # ============================================

        search = st.text_input(
            "🔍 Search Customer Name"
        )

        if search:

            final_df = final_df[
                final_df['Name']
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        # ============================================
        # OUTPUT TABLE
        # ============================================

        st.subheader("📋 Premium Calculation Output")

        st.dataframe(
            final_df,
            use_container_width=True
        )

        # ============================================
        # DOWNLOAD BUTTON
        # ============================================

        output_file = "Premium_Output.xlsx"

        final_df.to_excel(
            output_file,
            index=False
        )

        with open(output_file, "rb") as file:

            st.download_button(
                label="⬇ Download Premium Output",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:

        st.error(f"❌ Error: {e}")

# ============================================
# FOOTER
# ============================================

st.markdown("---")

st.caption(
    "Built for Group Term Life Insurance Premium Processing"
)
