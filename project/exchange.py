from bitcoinrpc.authproxy import AuthServiceProxy
import time

RPC_USER = ""
RPC_PASSWORD = ""
RPC_PORT = 18332
RPC_URL = f"http://x:{RPC_PORT}/"

def get_rpc_connection(wallet=None):
    url = f"http://{RPC_USER}:{RPC_PASSWORD}@x:{RPC_PORT}/"
    if wallet:
        url += f"wallet/{wallet}"
    return AuthServiceProxy(url)

def create_wallet_for_user(username):
    rpc = get_rpc_connection()
    try:
#wallet_name = username
# disable_private_keys = False
# blank = False
# passphrase = ""
# avoid_reuse = False
# descriptors = False
# load_on_startup = True
        rpc.createwallet(username, False, False, "", False, True, True)
    except Exception as e:
        if "already exists" in str(e):
            print(f"Wallet already exists for {username}")
        else:
            raise

    user_wallet = get_rpc_connection(wallet=username)
    address = user_wallet.getnewaddress(username)
    addresses = user_wallet.getaddressesbylabel(username)
    print(addresses)
    return address

def get_wallet_balance(username):
    wallet = get_rpc_connection(wallet=username)
    return float(wallet.getbalance())

def wait_for_confirmation(wallet_name, txid, timeout=120):
    wallet = get_rpc_connection(wallet=wallet_name)
    start = time.time()
    
    while time.time() - start < timeout:
        tx = wallet.gettransaction(txid)
        confirmations = tx.get("confirmations", 0)
        if confirmations >= 1:
            print(f"Transaction {txid} confirmed with {confirmations} confirmations.")
            return True
        print(f"Waiting for confirmation... ({confirmations})")
        time.sleep(10)
    
    print(f"Timeout: Transaction {txid} not confirmed within {timeout} seconds.")
    return False
