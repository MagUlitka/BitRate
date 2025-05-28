import streamlit as st
import plotly.express as px
from db import get_user
from rates import get_btc_7day_prices, get_btc_price
from db import update_user_balances
from exchange import get_wallet_balance, get_rpc_connection, wait_for_confirmation
from transactions import transaction_ui, transation_history

username = st.session_state.get("username")
if not username:
    st.switch_page("main.py")

user = get_user(username)
user_wallet = get_rpc_connection(username)
update_user_balances(user["username"], user['pln'], user['usd'], get_wallet_balance(username))


st.title(f"👋 Welcome back, {username}!")

st.subheader("💼 Your Wallet")

st.markdown(f"""
- **PLN:** {user['pln']} zł  
- **BTC:** {user['btc']:.6f} ₿  
- **USD:** {user['usd']} $
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

currency = st.selectbox("Spend which currency?", ["PLN", "USD"])
amount_to_spend = st.number_input(f"Amount to spend ({currency}):", min_value=0.0, max_value=(user['pln'] if currency=="PLN" else user['usd']), step=1.0)

if st.button("Buy BTC"):
    master_wallet = get_rpc_connection(wallet="Master")
    st.caption("Bitcoins available: {bitcoins}", get_wallet_balance("Master"))
    if amount_to_spend <= 0:
        st.error("Enter a positive amount")
    else:
        if currency == "PLN":
            btc_bought = amount_to_spend / btc_price["pln"]
            user['pln'] -= amount_to_spend
        else:
            btc_bought = amount_to_spend / btc_price["usd"]
            user['usd'] -= amount_to_spend
        try:
            user_wallet_address = user['btc_wallet']
            txid = master_wallet.sendtoaddress(user_wallet_address, btc_bought)
            if wait_for_confirmation("Master", txid):
                update_user_balances(
                    user["username"],
                    user["pln"],
                    user["usd"],
                    float(get_wallet_balance(user["username"]))
                )
                st.success("Transaction confirmed and balance updated.")
            else:
                st.error("Transaction not confirmed in time.")
            st.success(f"Sent {btc_bought:.6f} BTC to {user['username']}. TXID: {txid}")
        except Exception as e:
            st.error(f"Failed to send BTC: {e}")
        update_user_balances(user["username"], user['pln'], user['usd'], float(get_wallet_balance(user["username"])))

st.subheader("Sell Bitcoin")

btc_to_sell = st.number_input("Amount of BTC to sell:", min_value=0.0, max_value=user['btc'], step=0.0001, format="%.6f")
receive_currency = st.selectbox("Receive currency:", ["PLN", "USD"])

if st.button("Sell BTC"):
    if btc_to_sell <= 0:
        st.error("Enter a positive BTC amount")
    else:
        if receive_currency == "PLN":
            received_amount = btc_to_sell * btc_price["pln"]
            user['pln'] += received_amount
        else:
            received_amount = btc_to_sell * btc_price["usd"]
            user['usd'] += received_amount
        user['btc'] -= btc_to_sell
        update_user_balances(user["username"], user['pln'], user['usd'], user['btc'])
        st.success(f"Sold {btc_to_sell:.6f} BTC for {received_amount:.2f} {receive_currency}")

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