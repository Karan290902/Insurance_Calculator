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

.upload-box h1 {
    color: #0F172A !important;
}

.upload-box p {
    color: #334155 !important;
    font-size: 18px;
    line-height: 1.7;
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

<h1>💰 Group Insurance Premium Calculator</h1>

<p>

Upload any insurance Excel file and calculate:

<br><br>

✅ Premium Excl GST  
<br>
✅ GST Amount  
<br>
✅ Total Premium  

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
        # READ FILE
        # ============================================

        df = pd.read_excel(uploaded_file)

        # ============================================
# REMOVE COMPLETELY EMPTY ROWS
# ============================================

df.dropna(
    how='all',
    inplace=True
)

# REMOVE ROWS WHERE ALL VALUES ARE EMPTY STRINGS

df = df[
    ~(
        df.astype(str)
        .apply(
            lambda x: x.str.strip()
        )
        .eq('')
        .all(axis=1)
    )
]

        # ============================================
        # SHOW RAW DATA
        # ============================================

        with st.expander("📄 View Uploaded Data"):

            st.dataframe(df.head())

        # ============================================
        # AVAILABLE COLUMNS
        # ============================================

        all_columns = df.columns.tolist()

        # ============================================
        # AUTO DETECT FUNCTION
        # ============================================

        def detect_column(possible_names):

            for col in all_columns:

                cleaned_col = str(col).lower().strip()

                for keyword in possible_names:

                    if keyword in cleaned_col:

                        return col

            return all_columns[0]

        # ============================================
        # SAFE INDEX FUNCTION
        # ============================================

        def safe_index(value, columns):

            if value in columns:

                return columns.index(value)

            return 0

        # ============================================
        # AUTO DETECT IMPORTANT FIELDS
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

        detected_loan = detect_column([

            'loan account',
            'account no',
            'lan'

        ])

        detected_mobile = detect_column([

            'mobile',
            'phone',
            'contact'

        ])

        # ============================================
        # SIMPLE COLUMN MAPPING
        # ============================================

        st.subheader("🧠 Map Required Fields")

        col1, col2 = st.columns(2)

        with col1:

            name_col = st.selectbox(
                "👤 Customer Name",
                all_columns,
                index=safe_index(
                    detected_name,
                    all_columns
                )
            )

            sa_col = st.selectbox(
                "💰 Sum Assured",
                all_columns,
                index=safe_index(
                    detected_sa,
                    all_columns
                )
            )

        with col2:

            loan_col = st.selectbox(
                "🏦 Loan Account No",
                all_columns,
                index=safe_index(
                    detected_loan,
                    all_columns
                )
            )

            mobile_col = st.selectbox(
                "📱 Mobile Number",
                all_columns,
                index=safe_index(
                    detected_mobile,
                    all_columns
                )
            )

        # ============================================
        # STANDARDIZE IMPORTANT COLUMNS
        # ============================================

        df['Name'] = df[name_col]

        df['Sum Assured'] = df[sa_col]

        df['Loan Account No'] = df[loan_col]

        df['Mobile No'] = df[mobile_col]

        # ============================================
        # CLEAN NUMERIC DATA
        # ============================================

        df['Sum Assured'] = (

            df['Sum Assured']
            .astype(str)
            .str.replace(',', '')
            .str.replace('₹', '')

        )

        df['Sum Assured'] = pd.to_numeric(

            df['Sum Assured'],

            errors='coerce'

        ).fillna(0)

        # ============================================
        # PREMIUM CALCULATION
        # ============================================

        df['Premium Excl GST'] = (

            (df['Sum Assured'] / 100000)

            * RATE_PER_LAKH

        )

        # ============================================
        # GST CALCULATION
        # ============================================

        df['GST Amount'] = (

            df['Premium Excl GST']

            * GST_RATE

        )

        # ============================================
        # TOTAL PREMIUM
        # ============================================

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
