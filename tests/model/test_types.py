import pytest
from model.types import PCVDeposit


initial_balance = 100
initial_asset_price = 0.5
initial_asset_value = initial_balance * initial_asset_price


@pytest.fixture
def deposit_A():
    deposit = PCVDeposit(
        asset="fei",
        deposit_location="A",
    )

    # Test Deposit deposit() method
    deposit.deposit(initial_balance, initial_asset_price)
    assert deposit.asset_value == initial_asset_value

    return deposit


@pytest.fixture
def deposit_B():
    deposit = PCVDeposit(
        asset="fei",
        deposit_location="B",
    )

    # Test Deposit deposit() method
    deposit.deposit(initial_balance, initial_asset_price)
    assert deposit.asset_value == initial_asset_value

    return deposit


def test_deposit_transfer(deposit_A, deposit_B):
    # Test Deposit transfer() method
    deposit_A.transfer(deposit_B, deposit_A.balance)

    assert deposit_A.balance == 0
    assert deposit_A.asset_value == 0
    assert deposit_B.balance == 2 * initial_balance
    assert deposit_B.asset_value == 2 * initial_asset_value

    # Test Deposit transfer() with zero balance
    with pytest.raises(Exception) as e_info:
        deposit_A.transfer(deposit_B, 100)
    assert str(e_info.value) == "Amount must be less than balance"


def test_deposit_addition(deposit_A, deposit_B):
    deposit_C = deposit_A + deposit_B

    assert deposit_C.balance == deposit_A.balance + deposit_B.balance
    assert deposit_C.asset_value == deposit_A.asset_value + deposit_B.asset_value
