from brownie import (
    accounts,
    network,
    config,
    interface,
    LinkToken,
    MockV3Aggregator,
    VRFCoordinatorMock,
    Contract,
    MockDAI,
    MockWETH,
)

INITIAL_PRICE_FEED_VALUE = 2000 * 10 ** 18

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]


def get_account(index=None, id=None):
    # The index is specified used that
    if index:
        return accounts[index]
    # If we're working from a development network, use that
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    # If id is specified, use that
    if id:
        return accounts.load(id)
    # If we specify a test net, use our metamask wallet
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    # If all else fails, return nothing
    return None


def get_contract(contract_name):
    print(f"Getting contract: {contract_name}")
    print(f"Network: {network.show_active()}")
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it
        Args:
            contract_name (string): This is the name that is refered to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictonary. This could be either
            a mock or the 'real' contract on a live network.
    """
    # Get the contract type from the supplied contract name in the argument.
    contract_type = contract_to_mock[contract_name]
    # print(f"The contract type is: {contract_type}")

    # Check to see if we're working on a local environment, if so get ready to deploy mock contracts
    if network.show_active() in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print(
            f"{network.show_active()} not in Non Forked Local Blockchain Environments"
        )
        # If a mock has not yet been deployed, deploy a mock
        if len(contract_type) <= 0:
            deploy_mocks()
        # get the latest contract
        contract = contract_type[-1]
    # If we're not in a local environment,
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run script/deploy_mocks.py --network {network.show_active()}"
            )

    return contract


def deploy_mocks(decimals=18, initial_value=INITIAL_PRICE_FEED_VALUE):
    # Show the active network
    print(f"The active network is: {network.show_active()}")
    print("Deploying mocks")
    account = get_account()
    print("Deploying Mock Link Token...")
    link_token = LinkToken.deploy({"from": account})

    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")

    print("Deploying Mock Dai")
    dai_token = MockDAI.deploy({"from": account})
    print(f"Deployed to {dai_token.address}")

    print("Deploy Mock WETH")
    weth_token = MockWETH.deploy({"from": account})
    print(f"Deployed to {weth_token.address}")

    print("Mocks Deployed!")
