from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3
from brownie import (
    DappToken,
    TokenFarm,
    config,
    network,
)

KEPT_BALANCE = Web3.toWei(100, "ether")


def main():

    deploy_token_farm_and_dapp_token()


def deploy_token_farm_and_dapp_token():
    print("Getting Account")
    account = get_account()

    # Generate Dapp Token
    print(f"Deploying Dapp Token")
    initial_supply = Web3.toWei(1000000, "ether")
    dapp_token = deploy_DappToken(initial_supply, account)
    print(f"Dapp Token Deployed to: {dapp_token}")

    print("Deploy Token Farm")
    # Generate Token Farm
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    # Send generated dapp tokens to our token farm
    # This way our token farm can give it out as a reward
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE
    )
    tx.wait(1)

    # Allow dapp_token, weth_token, fau_token/DAI (fau=faucet)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")

    # map token addresses with associated price feed so we can convert to DAI
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }

    add_allowed_tokens(token_farm, dict_of_allowed_tokens, account)

    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dictionary_of_allowed_tokens, account):
    for token in dictionary_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dictionary_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)


def deploy_DappToken(initial_supply, account):
    dapp_token = DappToken.deploy(initial_supply, {"from": account})
    return dapp_token
