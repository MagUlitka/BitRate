from datetime import datetime
import streamlit as st
from exchange import get_wallet_balance, get_rpc_connection
from db import get_pending_transactions
import pandas as pd

def transaction_ui(current_user, rpc):
    st.subheader("Send BTC")
    recipient_address = st.text_input("Recipient BTC address")
    amount = st.number_input("Amount (BTC)", min_value=0.000001, format="%.6f")
    fee_rate = get_estimated_fee(rpc)
    fallback_fee = 0.0001
    if fee_rate:
        st.markdown(f"**Estimated fee:** `{fee_rate:.8f} BTC/kB` (target: 6 blocks)")
    else:
        st.markdown(f"**Estimated fee not available. Using fallback:** `{fallback_fee:.8f} BTC/kB`")
    note = st.text_input("Note (optional)")

    if st.button("Send BTC"):
        try:
            balance = get_wallet_balance(current_user)
            if amount > balance:
                st.error("Insufficient balance")
            else:
                is_valid = rpc.validateaddress(recipient_address)["isvalid"]
                if(is_valid):
                    txid = send_btc(current_user, recipient_address, amount)
                    st.success(f"Sent {amount:.6f} BTC to {recipient_address}")
                    st.write(f"Transaction ID: `{txid}`")
                else:
                    st.error(f"Wallet with this address doens't exist.")
        except Exception as e:
            st.error(f"Failed to send BTC: {e}")

def send_btc(from_user, to_address, amount):
    rpc = get_rpc_connection(wallet=from_user)
    txid = rpc.sendtoaddress(to_address, amount)
    return txid

def format_time(ts):
    if not ts:
        return "—"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def transation_history(rpc):
    st.subheader("📜 Transaction History")
    txs = rpc.listtransactions("*", 10)
    tx_data = []
    for tx in txs:
        tx_data.append({
            "TXID": tx.get("txid", "—"),
            "Address": tx.get("address", "—"),
            "Amount (BTC)": float(tx.get("amount", 0.0)),
            "Fee (BTC)": abs(round(tx.get("fee", 0.0), 8)) if "fee" in tx else 0.0,
            "Unspent Output Index": tx.get("vout", "—"),
            "Status": "✅ Confirmed" if tx.get("confirmations", 0) >= 1 else "🕒 Unconfirmed",
            "Sent": format_time(tx.get("time")),
            "Confirmed": format_time(tx.get("blocktime")) if tx.get("blocktime") else "—"
        })


    df = pd.DataFrame(tx_data)
    st.dataframe(df, use_container_width=True, hide_index=True, column_config=None)

def get_estimated_fee(rpc, conf_target=6):
    try:
        fee_estimate = rpc.estimatesmartfee(conf_target)
        if "feerate" in fee_estimate and fee_estimate["feerate"] is not None:
            return fee_estimate["feerate"]
        else:
            return None
    except Exception as e:
        print("Fee estimation error:", e)
        return None
    
def pending_exchange_ui(user):
    #TODO: also show type
    pending_txs = get_pending_transactions(user["username"])
    if pending_txs:
        st.warning("⏳ You have pending BTC exchange transactions waiting for confirmation:")
        for txid, amount, ts in pending_txs:
            st.write(f"• {amount:.6f} BTC – TXID: `{txid[:12]}...` (sent at {ts})")
            st.code(txid, language="text")
    else:
        st.success("✅ No pending BTC exchange transactions.")