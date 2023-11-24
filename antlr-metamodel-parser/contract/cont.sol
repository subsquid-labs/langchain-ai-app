// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v5.0.0) (token/ERC20/ERC20.sol)

pragma solidity ^0.8.20;

contract ERC20 {
    mapping(address => uint256) private _balances;

    uint256 private _totalSupply;

    string private _name;

    /**
     * @dev Sets the values for {name} and {symbol}.
     *
     * All two of these values are immutable: they can only be set once during
     * construction.
     */
    constructor(string memory name_) {
        if (bytes(name_).length == 0) _name = "aa";

        _name = name_;
    }

    /**
     * @dev Returns the name of the token.
     */
    /*  function name() public view virtual returns (string memory) {
        return _name;
    } */
}
