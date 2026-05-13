# ============================================
# IMPORT LIBRARIES
# ============================================

import streamlit as st
import pandas as pd
import numpy as np

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

h1 {
    color: #0F172A !important;
    font-weight: 800;
}

h2, h3 {
    color: #1E293B !important;
}

p, label, div {
    color: #334155;
}

[data-testid="metric-container"] {
    background: white;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #dbeafe;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stDataFrame {
    background-color: white;
    border-radius: 12px;
}

div.stDownloadButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}

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

.upload-box h1 {
    color: #0F172A !important;
}

.upload-box p {
    color: #334155 !important;
    font-size: 18px;
    line-height: 1.7;
}

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

<h1>💰 Group Insurance Premium Calculator</h1>

<p>

Upload any insurance/member Excel file and calculate:

<br><br>

✅ Premium Excl GST  
<br>
✅ GST Amount  
<br>
✅ Total Premium  
<br>
✅ Portfolio Summary  

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
    "📂 Upload Excel File",
    type=["xlsx"]
)

# ============================================
# PROCESS FILE
# ============================================

if uploaded_file is not None:

    try:

        # ============================================
        # READ EXCEL
        # ============================================

        df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()

        # ============================================
        # SHOW DATA
        # ============================================

        with st.expander("📄 View Uploaded Data"):

            st.dataframe(df.head())

        # ============================================
        # SHOW COLUMNS
        # ============================================

        st.subheader("📋 Uploaded Columns")

        st.write(df.columns.tolist())

        all_columns = df.columns.tolist()

        # ============================================
        # AUTO DETECTION FUNCTION
        # ============================================

        def detect_column(possible_names):

            for col in all_columns:

                cleaned_col = str(col).lower().strip()

                for keyword in possible_names:

                    if keyword in cleaned_col:

                        return col

            return None

        # ============================================
        # AUTO DETECT COLUMNS
        # ============================================

        detected_name = detect_column([

            'name',

            'borrower',

            'member',

            'customer'

        ])

        detected_sa = detect_column([

            'sum assured',

            'sum insured',

            'sa',

            'coverage'

        ])

        detected_mobile = detect_column([

            'mobile',

            'phone',

            'contact'

        ])

        detected_age = detect_column([

            'age'

        ])

        detected_loan = detect_column([

            'loan account',

            'account no',

            'lan'

        ])

        detected_gender = detect_column([

            'gender',

            'sex'

        ])

        # ============================================
        # USER COLUMN MAPPING
        # ============================================

        st.subheader("🧠 Map Your Columns")

        name_col = st.selectbox(
            "Select Name Column",
            all_columns,
            index=all_columns.index(detected_name)
            if detected_name in all_columns
            else 0
        )

        sa_col = st.selectbox(
            "Select Sum Assured Column",
            all_columns,
            index=all_columns.index(detected_sa)
            if detected_sa in all_columns
            else 0
        )

        mobile_col = st.selectbox(
            "Select Mobile Number Column",
            all_columns,
            index=all_columns.index(detected_mobile)
            if detected_mobile in all_columns
            else 0
        )

        age_col = st.selectbox(
            "Select Age Column",
            all_columns,
            index=all_columns.index(detected_age)
            if detected_age in all_columns
            else 0
        )

        loan_col = st.selectbox(
            "Select Loan Account Column",
            all_columns,
            index=all_columns.index(detected_loan)
            if detected_loan in all_columns
            else 0
        )

        gender_col = st.selectbox(
            "Select Gender Column",
            all_columns,
            index=all_columns.index(detected_gender)
            if detected_gender in all_columns
            else 0
        )

        # ============================================
        # STANDARDIZE COLUMNS
        # ============================================

        df['Name'] = df[name_col]

        df['Sum Assured'] = df[sa_col]

        df['Mobile No'] = df[mobile_col]

        df['Age'] = df[age_col]

        df['Loan Account No'] = df[loan_col]

        df['Gender'] = df[gender_col]

        # ============================================
        # CLEAN NUMERIC DATA
        # ============================================

        df['Sum Assured'] = (

            df['Sum Assured']
            .astype(str)
            .str.replace(',', '')

        )

        df['Sum Assured'] = pd.to_numeric(

            df['Sum Assured'],

            errors='coerce'

        ).fillna(0)

        df['Age'] = pd.to_numeric(

            df['Age'],

            errors='coerce'

        ).fillna(0)

        # ============================================
        # PREMIUM CALCULATION
        # ============================================

        df['Premium Excl GST'] = (

            (df['Sum Assured'] / 100000)

            * RATE_PER_LAKH

        )

        df['GST Amount'] = (

            df['Premium Excl GST']

            * GST_RATE

        )

        df['Premium + GST'] = (

            df['Premium Excl GST']

            + df['GST Amount']

        )

        # ============================================
        # VALIDATION
        # ============================================

        df['Validation Status'] = np.where(

            df['Sum Assured'] <= 0,

            '❌ Invalid SA',

            '✅ Valid'

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

            'Validation Status'

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
        # DOWNLOAD OUTPUT
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
    "Built for Group Insurance & Member-to-Trust Processing"
)
