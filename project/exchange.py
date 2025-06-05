from bitcoinrpc.authproxy import AuthServiceProxy

RPC_USER = ""
RPC_PASSWORD = ""
RPC_PORT = 18332
RPC_URL = f"http://x:{RPC_PORT}/"

def get_rpc_connection(wallet=None):
    url = f"http://{RPC_USER}:{RPC_PASSWORD}@x:{RPC_PORT}/"
    if wallet:
        url += f"wallet/{wallet}"
    return AuthServiceProxy(url)

def create_wallet_for_user(username, password):
    rpc = get_rpc_connection()
    try:
#wallet_name = username
# disable_private_keys = False
# blank = False
# passphrase = ""
# avoid_reuse = False
# descriptors = True
# load_on_startup = True
        if password is not None:
            rpc.createwallet(username, False, False, f"{password}", False, True, True)
        else:
            rpc.createwallet(username, False, False, "", False, True, True)
    except Exception as e:
        if "already exists" in str(e):
            print(f"Wallet already exists for {username}")
        else:
            raise

    user_wallet = get_rpc_connection(wallet=username)
    address = user_wallet.getnewaddress(username)
    return address

def get_wallet_balance(username):
    wallet = get_rpc_connection(wallet=username)
    return float(wallet.getbalance())