def add_liquidity(reserve_balance, supply_balance, voucher_balance, tokens, value):
    """
    Example:
    new_reserve = (1 + alpha)*reserve_balance
    new_supply = (1 + alpha)*supply_balance
    new_vouchers = (1 + alpha)*voucher_balance
    """
    if voucher_balance <= 0:
        dr = value
        ds = tokens
        dv = tokens
        return (dr, ds, dv)

    alpha = value / reserve_balance

    dr = alpha * reserve_balance
    ds = alpha * supply_balance
    dv = alpha * voucher_balance

    return (dr, ds, dv)


def remove_liquidity(reserve_balance, supply_balance, voucher_balance, tokens):
    """
    Example:
    new_reserve = (1 - alpha)*reserve_balance
    new_supply = (1 - alpha)*supply_balance
    new_liquidity_tokens = (1 - alpha)*liquidity_token_balance
    """
    alpha = tokens / voucher_balance

    dr = -alpha * reserve_balance
    ds = -alpha * supply_balance
    dv = -alpha * voucher_balance

    return (dr, ds, dv)


def get_input_price(dx, x_balance, y_balance, trade_fee=0):
    """
    How much y received for selling dx?
    Example:
    new_x = (1 + alpha)*x_balance
    new_y = y_balance - dy
    """
    rho = trade_fee

    alpha = dx / x_balance
    gamma = 1 - rho

    dy = (alpha * gamma / (1 + alpha * gamma)) * y_balance

    _dx = alpha * x_balance
    _dy = -dy

    return (_dx, _dy)


def get_output_price(dy, x_balance, y_balance, trade_fee=0):
    """
    How much x needs to be sold to buy dy?
    Example:
    new_x = x_balance + dx
    new_y = (1 - beta)*y_balance
    """
    rho = trade_fee

    beta = dy / y_balance
    gamma = 1 - rho

    dx = (beta / (1 - beta)) * (1 / gamma) * x_balance

    _dx = dx
    _dy = -beta * y_balance

    return (_dx, _dy)


# Token trading
def collateral_to_token(value, reserve_balance, supply_balance, trade_fee):
    """
    Trade collateral for token
    Example:
    new_reserve = reserve_balance + dx
    new_supply = supply_balance - dy
    """
    if reserve_balance == 0:
        return 0
    _dx, dy = get_input_price(value, reserve_balance, supply_balance, trade_fee)

    return abs(dy)


def token_to_collateral(tokens, reserve_balance, supply_balance, trade_fee):
    """
    Trade token for collateral
    Example:
    new_reserve = reserve_balance - dx
    new_supply = supply_balance + dy
    """
    if supply_balance == 0:
        return 0
    _dx, dy = get_input_price(tokens, supply_balance, reserve_balance, trade_fee)

    return abs(dy)
