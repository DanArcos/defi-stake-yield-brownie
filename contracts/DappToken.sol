// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

//This is our reward token that we'll be giving out to users that stake on our platform
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("Dapp Token", "DAPP") {
        _mint(msg.sender, initialSupply);
    }
}
