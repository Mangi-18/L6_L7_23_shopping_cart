"""Lab 6 - Step 5: tests written to reach >= 90% CODE (line) coverage of shopping_cart.py.

Strategy: make every LINE of shopping_cart.py run at least once.
Each test names the line(s) it exists to reach.
"""
import pytest
from shopping_cart import item_total, cart_discount, shipping_fee


# ---------------------------------------------------------------- item_total
def test_food_item():
    # given starter test: 100*2 = 200, qty < 10 so no bulk discount, +5% GST = 210
    assert item_total("food", 100, 2) == 210


def test_unknown_category_raises():
    # reaches line 6: raise ValueError("unknown category")
    with pytest.raises(ValueError):
        item_total("toys", 100, 1)


def test_negative_price_raises():
    # reaches line 8: raise ValueError("invalid price or quantity")
    with pytest.raises(ValueError):
        item_total("food", -5, 1)


def test_bulk_discount_electronics():
    # reaches line 11 (qty >= 10): 100*10 = 1000, minus 1000//10 = 100 -> 900
    # GST 18%: 900*18//100 = 162 -> 900 + 162 = 1062
    assert item_total("electronics", 100, 10) == 1062


# ------------------------------------------------------------- cart_discount
def test_big_cart_prime_with_coupon():
    # reaches lines 17, 23, 25: 500 (>=5000) + 100 (prime) + 6000//10 = 600 -> 1200
    assert cart_discount(6000, True, "FLAT10") == 1200


def test_medium_cart():
    # reaches line 19: 2000 <= 3000 < 5000 -> 200
    assert cart_discount(3000, False, None) == 200


def test_small_cart():
    # reaches line 21: below 2000 -> 0
    assert cart_discount(500, False, None) == 0


# -------------------------------------------------------------- shipping_fee
def test_free_shipping():
    # given starter test, reaches line 33: non-prime, cart >= 500 -> free
    assert shipping_fee(1000, False, False) == 0


def test_prime_express():
    # reaches lines 31, 37, 39: prime -> 0, express +100, prime express -50 -> 50
    assert shipping_fee(100, True, True) == 50


def test_small_cart_standard_shipping():
    # reaches line 35: non-prime, cart < 500 -> 40
    assert shipping_fee(100, False, False) == 40
