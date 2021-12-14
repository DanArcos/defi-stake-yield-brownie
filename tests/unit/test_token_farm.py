from brownie import config, exceptions, network
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    INITIAL_PRICE_FEED_VALUE,
    get_account,
    get_contract,
)
from scripts.deploy import deploy_token_farm_and_dapp_token
import pytest


def test_set_price_feed_contract():
    # Arrange
    # Ensure test is being done in a local environment
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    account = get_account()
    non_owner = get_account(index=1)  # Check only owner function
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    # Act
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(
        dapp_token.address, price_feed_address, {"from": account}
    )

    # Assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address

    # Check to see that a non owner can do this
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address, price_feed_address, {"from": non_owner}
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})

    # Assert

    # check staking balance
    assert (
        token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked
    )

    # check unique tokens stakes
    assert token_farm.uniqueTokensStaked(account.address) == 1

    # check stakers
    assert token_farm.stakers(0) == account

    # return values for the next token.
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    account = get_account()

    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens({"from": account})

    assert (
        dapp_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )


def test_unstake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing.")

    account = get_account()

    token_farm, dapp_token = test_stake_tokens(amount_staked)

    assert token_farm.stakingBalance(dapp_token.address, account) > 0

    # Unstake Token
    token_farm.unstakeTokens(dapp_token.address)

    # Assert that staking balance is now 0
    assert token_farm.stakingBalance(dapp_token.address, account) == 0

    assert token_farm.uniqueTokensStaked(account.address) == 0
