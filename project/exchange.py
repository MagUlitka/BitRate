from bitcoinrpc.authproxy import AuthServiceProxy

RPC_USER = "student26997"
RPC_PASSWORD = "pjatk26997"
RPC_PORT = 18332
RPC_URL = f"http://172.19.100.39:{RPC_PORT}/"

def get_rpc_connection(wallet=None):
    url = f"http://{RPC_USER}:{RPC_PASSWORD}@172.19.100.39:{RPC_PORT}/"
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
        rpc.createwallet(wallet_name=username, descriptors=True)
    except Exception as e:
        if "already exists" in str(e):
            print(f"Wallet already exists for {username}")
        else:
            raise

    user_wallet = get_rpc_connection(wallet=username)
    address = user_wallet.getnewaddress(label=username)
    return address

def get_wallet_balance(username):
    wallet = get_rpc_connection(wallet=username)
    return wallet.getbalance()
