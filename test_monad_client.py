import os
import sys
from dotenv import load_dotenv
from monad_client import MonadMarketClient
from formatter import format_dashboard

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "https://rpc.monad.xyz")
WALLET = os.getenv("WALLET_ADDRESS")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not WALLET:
        print("Error: WALLET_ADDRESS is not set in .env")
        raise SystemExit(1)

    client = MonadMarketClient(RPC_URL)
    data = client.get_dashboard(WALLET)

    print(f"Net worth: ${data['net_worth_usd']:,.2f}")
    print(f"Net APY:   {data['net_apy']:.2f}%")
    print(f"Health Factor: {data['health_factor']:.2f}")
    print(f"Collateral: ${data['total_collateral_usd']:,.2f}")
    print(f"Debt:       ${data['total_debt_usd']:,.2f}")
    print()
    print(format_dashboard(data))
