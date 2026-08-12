import json
from web3 import Web3

SECONDS_PER_YEAR = 31536000
RAY = 10 ** 27
BASE_UNIT = 10 ** 8  # Aave base currency (USD) has 8 decimals

POOL_ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"user","type":"address"}],
     "name":"getUserAccountData",
     "outputs":[
        {"internalType":"uint256","name":"totalCollateralBase","type":"uint256"},
        {"internalType":"uint256","name":"totalDebtBase","type":"uint256"},
        {"internalType":"uint256","name":"availableBorrowsBase","type":"uint256"},
        {"internalType":"uint256","name":"currentLiquidationThreshold","type":"uint256"},
        {"internalType":"uint256","name":"ltv","type":"uint256"},
        {"internalType":"uint256","name":"healthFactor","type":"uint256"}
     ],"stateMutability":"view","type":"function"}
]''')

DATA_PROVIDER_ABI = json.loads('''[
    {"inputs":[],"name":"getAllReservesTokens",
     "outputs":[{"components":[
        {"internalType":"string","name":"symbol","type":"string"},
        {"internalType":"address","name":"tokenAddress","type":"address"}
     ],"internalType":"struct IPoolDataProvider.TokenData[]","name":"","type":"tuple[]"}],
     "stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"},
               {"internalType":"address","name":"user","type":"address"}],
     "name":"getUserReserveData",
     "outputs":[
        {"internalType":"uint256","name":"currentATokenBalance","type":"uint256"},
        {"internalType":"uint256","name":"currentStableDebt","type":"uint256"},
        {"internalType":"uint256","name":"currentVariableDebt","type":"uint256"},
        {"internalType":"uint256","name":"principalStableDebt","type":"uint256"},
        {"internalType":"uint256","name":"scaledVariableDebt","type":"uint256"},
        {"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},
        {"internalType":"uint256","name":"liquidityRate","type":"uint256"},
        {"internalType":"uint40","name":"stableRateLastUpdated","type":"uint40"},
        {"internalType":"bool","name":"usageAsCollateralEnabled","type":"bool"}
     ],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"}],
     "name":"getReserveConfigurationData",
     "outputs":[
        {"internalType":"uint256","name":"decimals","type":"uint256"},
        {"internalType":"uint256","name":"ltv","type":"uint256"},
        {"internalType":"uint256","name":"liquidationThreshold","type":"uint256"},
        {"internalType":"uint256","name":"liquidationBonus","type":"uint256"},
        {"internalType":"uint256","name":"reserveFactor","type":"uint256"},
        {"internalType":"bool","name":"usageAsCollateralEnabled","type":"bool"},
        {"internalType":"bool","name":"borrowingEnabled","type":"bool"},
        {"internalType":"bool","name":"stableBorrowRateEnabled","type":"bool"},
        {"internalType":"bool","name":"isActive","type":"bool"},
        {"internalType":"bool","name":"isFrozen","type":"bool"}
     ],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"asset","type":"address"}],
     "name":"getReserveData",
     "outputs":[
        {"internalType":"uint256","name":"unbacked","type":"uint256"},
        {"internalType":"uint256","name":"accruedToTreasuryScaled","type":"uint256"},
        {"internalType":"uint256","name":"totalAToken","type":"uint256"},
        {"internalType":"uint256","name":"totalStableDebt","type":"uint256"},
        {"internalType":"uint256","name":"totalVariableDebt","type":"uint256"},
        {"internalType":"uint256","name":"liquidityRate","type":"uint256"},
        {"internalType":"uint256","name":"variableBorrowRate","type":"uint256"},
        {"internalType":"uint256","name":"stableBorrowRate","type":"uint256"},
        {"internalType":"uint256","name":"averageStableBorrowRate","type":"uint256"},
        {"internalType":"uint256","name":"liquidityIndex","type":"uint256"},
        {"internalType":"uint256","name":"variableBorrowIndex","type":"uint256"},
        {"internalType":"uint40","name":"lastUpdateTimestamp","type":"uint40"}
     ],"stateMutability":"view","type":"function"}
]''')

ORACLE_ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"asset","type":"address"}],
     "name":"getAssetPrice",
     "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],
     "stateMutability":"view","type":"function"}
]''')


def _apr_to_apy(apr_ray):
    """Aave rates are linear APR in ray (1e27). Convert to compounded APY (%)."""
    apr = apr_ray / RAY
    if apr <= 0:
        return 0.0
    apy = (1 + apr / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1
    return apy * 100


class MonadMarketClient:
    POOL_ADDRESS = "0x69a5F9AD4f96ebf0a0C792dD42a01cC5C0102fef"
    DATA_PROVIDER_ADDRESS = "0xB65A68B98274ef7D9a60E0C0747dD1BEc3D32fad"
    ORACLE_ADDRESS = "0x0c02b2c2038066C10Eab8fe1D5Cdb73d5a78A1Bf"

    def __init__(self, rpc_url):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC at {rpc_url}")
        self.pool = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.POOL_ADDRESS), abi=POOL_ABI)
        self.data_provider = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.DATA_PROVIDER_ADDRESS), abi=DATA_PROVIDER_ABI)
        self.oracle = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.ORACLE_ADDRESS), abi=ORACLE_ABI)

    def get_dashboard(self, wallet_address):
        user = Web3.to_checksum_address(wallet_address)

        total_collateral_base, total_debt_base, _avail, _liq_th, _ltv, health_factor_raw = \
            self.pool.functions.getUserAccountData(user).call()

        net_worth_usd = (total_collateral_base - total_debt_base) / BASE_UNIT
        health_factor = health_factor_raw / 1e18 if health_factor_raw < 1e35 else float('inf')

        supplies = []
        borrows = []
        supply_weighted_apy = 0.0
        borrow_weighted_apy = 0.0

        reserves = self.data_provider.functions.getAllReservesTokens().call()
        for symbol, asset in reserves:
            (a_token_balance, stable_debt, variable_debt, _principal_stable,
             _scaled_variable, _stable_rate, liquidity_rate, _stable_last_updated,
             collateral_enabled) = self.data_provider.functions.getUserReserveData(asset, user).call()

            total_debt_raw = stable_debt + variable_debt
            if a_token_balance == 0 and total_debt_raw == 0:
                continue

            decimals = self.data_provider.functions.getReserveConfigurationData(asset).call()[0]
            price_usd = self.oracle.functions.getAssetPrice(asset).call() / BASE_UNIT

            if a_token_balance > 0:
                balance = a_token_balance / (10 ** decimals)
                balance_usd = balance * price_usd
                supply_apy = _apr_to_apy(liquidity_rate)
                supplies.append({
                    "symbol": symbol,
                    "balance": balance,
                    "balance_usd": balance_usd,
                    "apy": supply_apy,
                    "collateral": collateral_enabled,
                })
                supply_weighted_apy += balance_usd * supply_apy

            if total_debt_raw > 0:
                debt = total_debt_raw / (10 ** decimals)
                debt_usd = debt * price_usd
                reserve_data = self.data_provider.functions.getReserveData(asset).call()
                variable_borrow_rate = reserve_data[6]
                borrow_apy = _apr_to_apy(variable_borrow_rate)
                borrows.append({
                    "symbol": symbol,
                    "debt": debt,
                    "debt_usd": debt_usd,
                    "apy": borrow_apy,
                })
                borrow_weighted_apy += debt_usd * borrow_apy

        net_apy = 0.0
        if net_worth_usd > 0:
            net_apy = (supply_weighted_apy - borrow_weighted_apy) / net_worth_usd

        return {
            "net_worth_usd": net_worth_usd,
            "net_apy": net_apy,
            "health_factor": health_factor,
            "total_collateral_usd": total_collateral_base / BASE_UNIT,
            "total_debt_usd": total_debt_base / BASE_UNIT,
            "supplies": supplies,
            "borrows": borrows,
        }
