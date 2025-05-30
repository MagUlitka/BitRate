import streamlit as st
import plotly.express as px
from db import get_user
from rates import get_btc_7day_prices, get_btc_price
from db import update_user_balances, save_pending_tx, check_pending_transactions
from exchange import get_wallet_balance, get_rpc_connection
from transactions import transaction_ui, transation_history, pending_exchange_ui

st.markdown("""
    <style>
        .main .block-container {
            max-width: 95%;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)


username = st.session_state.get("username")
if not username:
    st.switch_page("main.py")

user = get_user(username)
user_wallet = get_rpc_connection(username)
update_user_balances(user["username"], user['pln'], user['usd'], get_wallet_balance(username))
check_pending_transactions()


st.title(f"👋 Welcome back, {username}!")

st.subheader("💼 Your Wallet")

st.markdown(f"""
- **PLN:** {user['pln']:.2f} zł  
- **BTC:** {user['btc']:.6f} ₿  
- **USD:** {user['usd']:.2f} $
""")
st.text_input("Wallet address (click to copy):", user['btc_wallet'], disabled=True)

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("main.py")

st.subheader("📈 Real-time Bitcoin Price")

btc_price = get_btc_price()


df_usd = get_btc_7day_prices("usd")
df_usd["price"] = df_usd["price"] / 1000
df_pln = get_btc_7day_prices("pln")
df_pln["price"] = df_pln["price"] / 1000

df_long = df_usd.reset_index().melt(id_vars=["Time"], var_name="Currency", value_name="Price")
df_long2 = df_pln.reset_index().melt(id_vars=["Time"], var_name="Currency", value_name="Price")

if btc_price["usd"] and btc_price["pln"]:
    st.metric(label="BTC → USD", value=f"${btc_price['usd']:,}")
    st.metric(label="BTC → PLN", value=f"{btc_price['pln']:,} zł")

st.caption("Prices auto-update when you refresh or rerun the app.")

transaction_ui(user["username"],user_wallet)

transation_history(user_wallet)

st.subheader("Buy Bitcoin")

bitcoins_available = get_wallet_balance("Master")
st.caption(f"Bitcoins available: {bitcoins_available}")
currency = st.selectbox("Spend which currency?", ["PLN", "USD"])
user_fiat_balance = user['pln'] if currency == "PLN" else user['usd']
btc_price_selected = btc_price[currency.lower()]

max_fiat_by_master_btc = bitcoins_available * btc_price_selected
final_max_spend = min(user_fiat_balance, max_fiat_by_master_btc)

amount_to_spend = st.number_input(
    f"Amount to spend ({currency}):",
    min_value=0.0,
    max_value=final_max_spend,
    step=1.0
)

btc_bought = amount_to_spend / btc_price[currency.lower()] if amount_to_spend > 0 else 0
st.info(f"You will receive approximately **{btc_bought:.8f} BTC**")

if st.button("Buy BTC"):
    master_wallet = get_rpc_connection(wallet="Master")
    if amount_to_spend <= 0:
        st.error("Enter a positive amount")
    else:
        try:
            user_wallet_address = user['btc_wallet']
            txid = master_wallet.sendtoaddress(user_wallet_address,  round(float(btc_bought), 8))
            if currency == "PLN":
                save_pending_tx(
                    txid=txid,
                    username=user['username'],
                    amount_btc=btc_bought,
                    pln=amount_to_spend,
                    usd=0,
                    tx_type="buy"
                )
            elif currency == "USD":
                save_pending_tx(
                    txid=txid,
                    username=user['username'],
                    amount_btc=btc_bought,
                    pln=0,
                    usd=amount_to_spend,
                    tx_type="buy"
                )
            st.success(f"BTC sent to wallet. TXID: {txid}")
            st.info("We'll update your balance once the transaction is confirmed.")
        except Exception as e:
            st.error(f"Failed to send BTC: {e}")

st.subheader("Sell Bitcoin")
master_balance = get_user("Master")
pln_available = master_balance['pln']
usd_available = master_balance['usd']
st.caption(f"PLN available: {pln_available:.2f}")
st.caption(f"USD available: {usd_available:.2f}")

receive_currency = st.selectbox("Receive currency:", ["PLN", "USD"])

btc_price_selected = btc_price[receive_currency.lower()]
max_btc_by_master_fiat = (pln_available if receive_currency == "PLN" else usd_available) / btc_price_selected
max_btc_to_sell = min(user['btc'], max_btc_by_master_fiat)

btc_to_sell = st.number_input(
    "Amount of BTC to sell:",
    min_value=0.0,
    max_value=max_btc_to_sell,
    step=0.0001,
    format="%.6f"
)

received_amount = btc_to_sell * btc_price[receive_currency.lower()] if btc_to_sell > 0 else 0
st.info(f"You will receive approximately **{received_amount:.2f} {receive_currency}**")

if st.button("Sell BTC"):
    if btc_to_sell <= 0:
        st.error("Enter a positive BTC amount")
    else:
        try:
            user_wallet = get_rpc_connection(wallet=user["username"])
            master_wallet_address = master_balance['btc_wallet']
            txid = user_wallet.sendtoaddress(master_wallet_address, round(float(btc_to_sell), 8))
            if receive_currency == "PLN":
                save_pending_tx(
                    txid=txid,
                    username=user['username'],
                    amount_btc=btc_to_sell,
                    pln=received_amount,
                    usd=0,
                    tx_type="sell"
                )
            elif receive_currency == "USD":
                save_pending_tx(
                    txid=txid,
                    username=user['username'],
                    amount_btc=btc_to_sell,
                    pln=0,
                    usd=received_amount,
                    tx_type="sell"
                )
            st.success(f"BTC sold. TXID: {txid}")
            st.info("We'll update your fiat balance once the transaction is confirmed.")
        except Exception as e:
            st.error(f"Failed to send BTC: {e}")

st.subheader("Pending exchange")
pending_exchange_ui(user)

st.subheader("📊 BTC Value in the Last Year")

if df_usd is not None:
    fig_usd = px.line(df_usd, x="Time", y="price", title="BTC → USD (Last 365 Days)")
    fig_usd.update_layout(
        yaxis=dict(range=[df_usd["price"].min() * 0.9, df_usd["price"].max() * 1.05], tickformat=".6f")
    )
    st.plotly_chart(fig_usd, use_container_width=True)
else:
    st.warning("Failed to load price data.")

if df_pln is not None:
    fig_pln = px.line(df_pln, x="Time", y="price", title="BTC → PLN (Last 365 Days)")
    fig_pln.update_layout(
        yaxis=dict(range=[df_pln["price"].min() * 0.95, df_pln["price"].max() * 1.05], tickformat=".6f")
    )
    st.plotly_chart(fig_pln, use_container_width=True)
else:
    st.warning("Failed to load price data.")