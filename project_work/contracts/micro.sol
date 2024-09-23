// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

contract MicroPayments {
    address public owner;
    mapping(address => uint256) public balances;

    event PaymentSent(address indexed _from, address indexed _to, uint256 _amount);

    constructor() {
        owner = msg.sender;
    }

    function deposit() public payable {
        require(msg.value > 0, "Must send some Ether");
        balances[msg.sender] += msg.value;
    }

    function sendPayment(address payable _recipient, uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        require(_amount > 0, "Amount should be greater than zero");

        balances[msg.sender] -= _amount;
        _recipient.transfer(_amount);

        emit PaymentSent(msg.sender, _recipient, _amount);
    }

    function withdraw() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No funds to withdraw");

        balances[msg.sender] = 0;
        payable(msg.sender).transfer(balance);
    }

    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }
}