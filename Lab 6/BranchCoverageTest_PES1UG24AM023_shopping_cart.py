"""Lab 6 - Step 7: tests written to reach >= 90% BRANCH coverage of shopping_cart.py.

Line coverage asks "did every line run?". Branch coverage asks "did every
decision (if / elif) go BOTH ways - True AND False?".
This file keeps all the code-coverage tests and adds:
  * the decision outcome they never exercised: is_express True with is_prime False
    (line 38 `if is_prime:` evaluated to False)
  * boundary values (exactly 10 qty, 500, 1000, 2000, 5000), where off-by-one bugs live
  * each half of the compound conditions (`price < 0 or qty <= 0`,
    `coupon == "FLAT10" and cart_value >= 1000`)
"""
import pytest
from shopping_cart import item_total, cart_discount, shipping_fee


# =========================================================== item_total
# Decision 1: category not in GST_RATE      True -> raise | False -> continue
# Decision 2: price < 0 or qty <= 0         True -> raise | False -> continue
# Decision 3: qty >= 10                     True -> bulk discount | False -> skip
def test_food_item():
    assert item_total("food", 100, 2) == 210               # D1 F, D2 F, D3 F


def test_unknown_category_raises():
    with pytest.raises(ValueError, match="unknown category"):
        item_total("toys", 100, 1)                         # D1 T


def test_negative_price_raises():
    with pytest.raises(ValueError, match="invalid price or quantity"):
        item_total("food", -5, 1)                          # D2 T via price < 0


def test_zero_quantity_raises():
    with pytest.raises(ValueError, match="invalid price or quantity"):
        item_total("food", 100, 0)                         # D2 T via qty <= 0 (other half of `or`)


def test_zero_price_is_allowed():
    assert item_total("food", 0, 1) == 0                   # boundary: price == 0 is valid


@pytest.mark.parametrize("category, price, qty, expected", [
    ("electronics", 100, 10, 1062),   # D3 T at boundary qty == 10: 1000-100=900, +162
    ("food",        100,  9,  945),   # D3 F just below boundary: 900, +45
    ("food",         15, 10,  141),   # bulk: 150-15=135, 135*5//100=6 -> 141
    ("clothing",     99,  1,  110),   # 12% GST floors: 1188//100 = 11 -> 99+11
])
def test_item_total_values(category, price, qty, expected):
    assert item_total(category, price, qty) == expected


# ======================================================== cart_discount
# Decision 1: if/elif/else on cart_value    >=5000 | >=2000 | else
# Decision 2: is_prime                      True | False
# Decision 3: coupon == "FLAT10" and cart_value >= 1000   True | False
@pytest.mark.parametrize("cart_value, is_prime, coupon, expected", [
    (6000, True,  "FLAT10", 1200),   # >=5000, prime, coupon applies: 500+100+600
    (5000, False, None,      500),   # boundary exactly 5000
    (4999, False, None,      200),   # just below 5000 -> middle tier
    (3000, False, None,      200),   # middle tier
    (2000, True,  "FLAT10",  500),   # boundary 2000: 200+100+200
    (1999, False, None,        0),   # just below 2000 -> no tier discount
    (500,  False, None,        0),   # small cart
    (1000, False, "FLAT10",  100),   # coupon boundary: exactly 1000 -> 1000//10
    (999,  False, "FLAT10",    0),   # right coupon, cart too small (`and` 2nd half False)
    (5000, False, "flat10",  500),   # wrong coupon text (`and` 1st half False): case-sensitive
])
def test_cart_discount(cart_value, is_prime, coupon, expected):
    assert cart_discount(cart_value, is_prime, coupon) == expected


# ========================================================= shipping_fee
# Decision 1: if/elif/else                 prime | cart >= 500 | else
# Decision 2: is_express                   True | False
# Decision 3 (nested): is_prime            True | False   <- only reachable when express
@pytest.mark.parametrize("cart_value, is_prime, is_express, expected", [
    (1000, False, False,   0),   # given starter test: free over 500
    (100,  True,  False,   0),   # prime, standard
    (100,  True,  True,   50),   # prime express: 0 + 100 - 50   (D3 True)
    (100,  False, True,  140),   # NEW BRANCH: express, not prime: 40 + 100  (D3 False)
    (600,  False, True,  100),   # free standard + express fee   (D3 False)
    (100,  False, False,  40),   # small cart standard
    (499,  False, False,  40),   # boundary just below 500
    (500,  False, False,   0),   # boundary exactly 500
])
def test_shipping_fee(cart_value, is_prime, is_express, expected):
    assert shipping_fee(cart_value, is_prime, is_express) == expected
