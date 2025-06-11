import streamlit as st
import pandas as pd
import io


class Founder:
    def __init__(self, name, shares):
        self.name = name
        self.shares = shares
        self.final_holding = 0


class Investor:
    def __init__(self, name, invested_amount, holding_percentage):
        self.name = name
        self.invested_amount = invested_amount
        self.holding_percentage = holding_percentage
        self.shares = 0
        self.actual_amount = 0


if "founders" not in st.session_state:
    st.session_state.founders = []
if "show_founder_inputs" not in st.session_state:
    st.session_state.show_founder_inputs = False
if "investors" not in st.session_state:
    st.session_state.investors = []
if "show_investor_inputs" not in st.session_state:
    st.session_state.show_investor_inputs = False

st.title("Cap Table Calculator")
st.write("**Note**: Please use this app for pre-seed round calculations only.")

st.subheader("Founders List")
if st.button("Add Founder"):
    st.session_state.show_founder_inputs = True

if st.session_state.show_founder_inputs:
    with st.form(key="founder_form"):
        name = st.text_input("Founder's name", key="founder_name")
        shares = st.number_input("number of shares", min_value=0, key="founder_shares")
        submitted = st.form_submit_button("Submit")
        if submitted and name and shares >= 0:
            st.session_state.founders.append(Founder(name, shares))
            st.session_state.show_founder_inputs = False
            st.rerun()
            # st.session_state.founder_name=""
            # st.session_state.founder_shares=0


total_founders_shares = sum(f.shares for f in st.session_state.founders)

cols = st.columns([4, 3, 3, 2])
cols[0].write("**Shareholder**")
cols[1].write("**Number of shares**")
cols[2].write("**% holding**")
cols[3].write("**Delete**")

# Table Rows
for i, f in enumerate(st.session_state.founders):
    holding = (
        f"{round((f.shares / total_founders_shares) * 100, 1)}%"
        if total_founders_shares > 0
        else "0%"
    )
    cols = st.columns([4, 3, 3, 2])
    cols[0].write(f.name)
    cols[1].write(f.shares)
    cols[2].write(holding)
    if cols[3].button("❌", key=f"delete_founder_{i}"):
        st.session_state.founders.pop(i)
        st.rerun()

df1 = pd.DataFrame(
    {
        "Shareholder": [f.name for f in st.session_state.founders],
        "Number of shares": [f.shares for f in st.session_state.founders],
        "% holding": [
            f"{round((f.shares / total_founders_shares) * 100, 1)}%"
            if total_founders_shares > 0
            else "0%"
            for f in st.session_state.founders
        ],
    }
)

df1.loc[len(df1)] = ["Total", round(total_founders_shares), "100.0%"]
csv_df1 = df1.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Founder List as CSV",
    data=csv_df1,
    file_name="founders_list.csv",
    mime="text/csv",
    key="df1_download",
)
st.subheader("Post-money valuation")
post_money_valuation = st.number_input("", min_value=0)
st.subheader("Investors List")
if st.button("Add Investor"):
    st.session_state.show_investor_inputs = True

if st.session_state.show_investor_inputs:
    with st.form(key="investor_form"):
        name = st.text_input("Investor name", key="investor_name")
        amount = st.number_input(
            "Investment Amount", min_value=0, key="investor_amount"
        )
        holding_percentage = round((amount / post_money_valuation) * 100, 1)
        submitted = st.form_submit_button("Submit")
        if submitted and name and amount >= 0:
            st.session_state.investors.append(
                Investor(name, amount, holding_percentage=holding_percentage)
            )
            st.session_state.show_investor_inputs = False
            st.rerun()


total_invested_amount = sum(f.invested_amount for f in st.session_state.investors)
total_investor_percentage = sum(
    f.holding_percentage for f in st.session_state.investors
)

cols = st.columns([4, 4, 2])
cols[0].write("**Investor**")
cols[1].write("**Invested amount**")
cols[2].write("**Delete**")

# Table Rows
for i, f in enumerate(st.session_state.investors):
    cols = st.columns([4, 4, 2])
    cols[0].write(f.name)
    cols[1].write(f.invested_amount)
    if cols[2].button("❌", key=f"delete_investor_{i}"):
        st.session_state.investors.pop(i)
        st.rerun()

df4 = pd.DataFrame(
    {
        "Investor": [f.name for f in st.session_state.investors],
        "Amount": [f.invested_amount for f in st.session_state.investors],
    }
)

df4.loc[len(df4)] = ["Total", total_invested_amount]
csv_df4 = df4.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Investor commitments as CSV",
    data=csv_df4,
    file_name="investor_commitments.csv",
    mime="text/csv",
    key="df4_download",
)

ESOP_percentage = st.number_input(
    "How much percentage of ESOP you want after first round of investment?", min_value=0
)
percentage_of_founders_shares = 100 - (ESOP_percentage + total_investor_percentage)
total_shares = round((total_founders_shares * 100) / percentage_of_founders_shares)
esop_shares = round(total_shares * ESOP_percentage / 100 if ESOP_percentage > 0 else 0)

pre_money_valuation = post_money_valuation - total_invested_amount
share_price = round(
    pre_money_valuation / (total_founders_shares + esop_shares)
    if (total_founders_shares + esop_shares) > 0
    else 0
)

total_actual_amount = 0
total_investors_shares = 0

for f in st.session_state.investors:
    f.shares = round(f.invested_amount / share_price)
    f.actual_amount = f.shares * share_price
    total_actual_amount += f.actual_amount
    total_investors_shares += f.shares
for f in st.session_state.founders:
    f.final_holding = round((f.shares / total_shares) * 100, 1)

df2 = pd.DataFrame(
    {
        "Shareholder": [f.name for f in st.session_state.founders],
        "Number of shares": [f.shares for f in st.session_state.founders],
        "% holding": [
            f"{round((f.shares / (total_founders_shares + esop_shares)) * 100, 1)}%"
            for f in st.session_state.founders
        ],
    }
)

df2.loc[len(df2)] = [
    "ESOP Pool",
    round(esop_shares),
    f"{round((esop_shares / (total_founders_shares + esop_shares)) * 100 if (total_founders_shares + esop_shares) > 0 else 0,1)}%" ,
]
df2.loc[len(df2)] = ["Total", round(total_founders_shares + esop_shares), "100.0%"]
# Initialize session state key
# Initialize toggle state
if "show_pre_table" not in st.session_state:
    st.session_state.show_pre_table = False

# Button with dynamic label
button_label = (
    "Hide table" if st.session_state.show_pre_table else "Show Pre-investment cap table"
)
if st.button(button_label, key="pre_button"):
    st.session_state.show_pre_table = not st.session_state.show_pre_table
    st.rerun()

# Conditionally display the table
if st.session_state.show_pre_table:
    st.write("Pre-investment cap table (creation of ESOPs)")
    st.write(
        df2.style.set_table_styles(
            [{"selector": "td", "props": [("font-weight", "bold")]}]
        )
    )  # Replace with your actual DataFrame

df3 = pd.DataFrame(
    {
        "Pre-seed round": [
            "Pre-money valuation",
            "Investment amount",
            "Post-money valuation",
            "Share price",
        ],
        "Amount": [
            pre_money_valuation if pre_money_valuation>0 else 0,
            total_invested_amount,
            post_money_valuation,
            share_price if share_price >0 else 0,
        ],
    }
)

if "show_preseed_table" not in st.session_state:
    st.session_state.show_preseed_table = False

# Button with dynamic label
button_label = (
    "Hide table" if st.session_state.show_preseed_table else "Show Pre-seed round table"
)
if st.button(button_label, key="preseed_button"):
    st.session_state.show_preseed_table = not st.session_state.show_preseed_table
    st.rerun()

# Conditionally display the table
if st.session_state.show_preseed_table:
    st.write("Pre-seed round table")
    st.write(df3)  # Replace with your actual DataFrame

df5 = pd.DataFrame(
    {
        "Investor": [f.name for f in st.session_state.investors],
        "Number of shares": [f.shares if f.shares>0 else 0 for f in st.session_state.investors],
        "Actual amount": [f.actual_amount if share_price>0 else 0 for f in st.session_state.investors],
    }
)

df5.loc[len(df5)] = ["Total", total_investors_shares if total_investors_shares>0 else 0, total_actual_amount if share_price>0 else 0]

if "show_subscription_table" not in st.session_state:
    st.session_state.show_subscription_table = False

# Button with dynamic label
button_label = (
    "Hide table"
    if st.session_state.show_subscription_table
    else "Show actual subscription table"
)
if st.button(button_label, key="subscription_button"):
    st.session_state.show_subscription_table = (
        not st.session_state.show_subscription_table
    )
    st.rerun()

# Conditionally display the table
if st.session_state.show_subscription_table:
    st.write("Actual subscription amount & number of shares to be alloted")
    st.write(df5)  # Replace with your actual DataFrame

df6 = pd.DataFrame(
    {
        "Shareholder": [],
        "Eq shares": [],
        "Pref shares": [],
        "Total shares": [],
        "% holding": [],
    }
)

for f in st.session_state.founders:
    df6.loc[len(df6)] = [f.name, f.shares, "", f.shares, f"{f.final_holding}%"]
df6.loc[len(df6)] = ["ESOP Pool", esop_shares, "", esop_shares, f"{ESOP_percentage}%"]
for f in st.session_state.investors:
    df6.loc[len(df6)] = [f.name, "", f.shares if f.shares>0 else 0, f.shares if f.shares>0 else 0, f"{f.holding_percentage}%"]
df6.loc[len(df6)] = [
    "Total",
    (total_founders_shares + esop_shares),
    total_investors_shares if total_investors_shares>0 else 0,
    (total_founders_shares + esop_shares + (total_investors_shares if total_investors_shares>0 else 0)),
    "100%",
]

if "show_postcap_table" not in st.session_state:
    st.session_state.show_postcap_table = False

button_label = (
    "Hide table"
    if st.session_state.show_postcap_table
    else "Show post-investment cap table"
)
if st.button(button_label, key="postcap_button"):
    st.session_state.show_postcap_table = not st.session_state.show_postcap_table
    st.rerun()

# Conditionally display the table
if st.session_state.show_postcap_table:
    st.write("Post-investment cap table (fully diluted basis)")
    st.write(df6)


output = io.StringIO()

output.write("Founders List\n")
df1.to_csv(output, index=False)
output.write("\nPre-Investment Cap Table\n")
df2.to_csv(output, index=False)
output.write("\nPre-seed Round Table\n")
df3.to_csv(output, index=False)
output.write("\nInvestor Commitments\n")
df4.to_csv(output, index=False)
output.write("\nActual subscription amount & number of shares to be alloted\n")
df5.to_csv(output, index=False)
output.write("\nPost-Investment Cap Table\n")
df6.to_csv(output, index=False)

csv_data = output.getvalue().encode("utf-8")

st.download_button(
    label="📥 Download All Tables as a Single .csv File",
    data=csv_data,
    file_name="cap_tables.csv",
    mime="text/csv"
)