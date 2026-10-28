# Lab 6 — Code and Branch Coverage Analysis Report

| | |
|---|---|
| **Name** | Akhil Mangipudi |
| **SRN** | PES1UG24AM023 |
| **Repository** | L6_L7_23_shopping_cart |
| **Module under test** | `shopping_cart.py` (`item_total`, `cart_discount`, `shipping_fee`) |
| **Tools** | Python 3, pytest, coverage.py 7.17 |

---

## 1. Objective

Measure how much of `shopping_cart.py` is exercised by tests. The work has three parts:

- Raise **line (code) coverage** to at least 90%.
- Raise **branch coverage** to at least 90%.
- Explain why the two metrics can disagree.

## 2. Definitions

- **Line coverage:** the percentage of executable statements that ran at least once during the tests.
- **Branch coverage:** the percentage of decision outcomes that were taken. Every `if`/`elif` has two outcomes, True and False, and both must happen.
  - `coverage.py` combines lines and branches into one figure: **(statements hit + branches hit) / (statements + branches)**.

`shopping_cart.py` has **32 statements** and **22 branch outcomes**: 11 decisions × 2 outcomes each.

## 3. Commands used

```
# line (code) coverage
python -m coverage run -m pytest <test_file>
python -m coverage report -m

# branch coverage
python -m coverage run --branch -m pytest <test_file>
python -m coverage report -m
```

## 4. Results summary

| Test file | Tests | Line coverage | Branch coverage | Missing |
|---|---|---|---|---|
| `test_shopping_cart.py` (starter) | 2 | **44%** (14/32) | **37%** (6/22 branches) | lines 6, 8, 11, 16-26, 31, 35, 37-39 |
| `CodeCoverageTest_PES1UG24AM023_shopping_cart.py` | 10 | **100%** (32/32) | 98% (21/22 branches) | branch 38->40 only |
| `BranchCoverageTest_PES1UG24AM023_shopping_cart.py` | 27 | **100%** (32/32) | **100%** (22/22 branches) | none |

Screenshots: `code_coverage.png` (line coverage) and `branch_coverage.png` (branch coverage).

## 5. Baseline analysis (starter tests)

The starter file had two tests: `item_total("food", 100, 2)` and `shipping_fee(1000, False, False)`. Together they left large parts of the module unexecuted:

- **`cart_discount` was never called.** Lines 16-26 were entirely missed.
- **`item_total`** never hit either error path (lines 6, 8) or the bulk discount (line 11).
- **`shipping_fee`** never hit the prime path (31), the small-cart fee (35), or the express logic (37-39).

This gave 44% line coverage. With `--branch` the figure falls to **37%**: (14 + 6) / (32 + 22) = 20/54. The starter tests only ever took one direction at most decisions (**BrPart = 6**).

## 6. Code coverage tests (Commit 1)

**Goal:** make every *line* run at least once. One test was written for each unreached line or group of lines:

| Test | Input | Expected | Lines reached |
|---|---|---|---|
| unknown category | `item_total("toys", 100, 1)` | `ValueError` | 6 |
| negative price | `item_total("food", -5, 1)` | `ValueError` | 8 |
| bulk discount | `item_total("electronics", 100, 10)` | 1062 | 11 |
| big cart, prime, coupon | `cart_discount(6000, True, "FLAT10")` | 1200 | 17, 23, 25 |
| medium cart | `cart_discount(3000, False, None)` | 200 | 19 |
| small cart | `cart_discount(500, False, None)` | 0 | 21 |
| prime express | `shipping_fee(100, True, True)` | 50 | 31, 37, 39 |
| small cart standard | `shipping_fee(100, False, False)` | 40 | 35 |

Expected values were worked out by hand. For example, the bulk electronics case:

- 100 × 10 = 1000
- bulk discount: 1000 − 1000//10 = 900
- GST at 18%: 900 × 18 // 100 = 162
- total: 900 + 162 = **1062**

**Result:** 100% line coverage, 0 missing lines.

## 7. Why 100% line coverage was not 100% branch coverage

Running the same code-coverage file with `--branch` reports **98%, with branch `38->40` missing**:

```python
36    if is_express:
37        fee += 100
38        if is_prime:        # decision
39            fee -= 50
40    return fee
```

The test `shipping_fee(100, True, True)` executes lines 37, 38 and 39, so every *line* is covered. But the decision on line 38 only ever evaluated to **True**. The path where an express order is placed by a **non-prime** customer (line 38 jumps straight to line 40) was never executed. A bug in that path, such as charging the wrong express fee to non-prime customers, would go undetected even at 100% line coverage.

This is exactly the weakness of line coverage: **it shows which lines ran, not which decisions were tested both ways.**

## 8. Branch coverage tests (Commit 2)

The branch-coverage file keeps all the code-coverage tests and adds three kinds of tests.

**1. The missing decision outcome**
- `shipping_fee(100, False, True)` = 140 (40 + 100).
- `shipping_fee(600, False, True)` = 100 (0 + 100).
- These take the False side of line 38.

**2. Boundary values.** Off-by-one errors (`>` written instead of `>=`) only show up exactly at a threshold:

| Function | Value at threshold | Value just below |
|---|---|---|
| `item_total` qty | 10 → bulk discount applied | 9 → not applied |
| `cart_discount` | 5000 → 500 | 4999 → 200 |
| `cart_discount` | 2000 → 200 | 1999 → 0 |
| `cart_discount` coupon | 1000 → 100 | 999 → 0 |
| `shipping_fee` | 500 → free | 499 → 40 |

**3. Each half of the compound conditions**
- `price < 0 or qty <= 0`:
  - `price = -5` makes the first half True.
  - `qty = 0` makes the second half True.
  - `price = 0` is a valid value at the boundary.
- `coupon == "FLAT10" and cart_value >= 1000`:
  - The correct coupon on a cart of 999 makes the second half False.
  - `"flat10"` on a cart of 5000 makes the first half False, which shows the coupon check is case-sensitive.

Related cases were grouped with `@pytest.mark.parametrize` to keep the file readable. That is why pytest reports 27 tests.

**Result:** 100% branch coverage. All 22 branch outcomes were taken, BrPart = 0, and nothing is missing.

## 9. Observations

1. **Line coverage overstates test quality.** The code-coverage file reached 100% lines but still missed a real business case: non-prime express shipping.
2. **Branch coverage is stronger, but still not complete.**
   - It treats `price < 0 or qty <= 0` as a *single* decision.
   - A negative price alone already makes that `if` True, so branch coverage would be 100% even if `qty <= 0` were broken.
   - Testing each sub-condition separately (**condition coverage**) needed the extra `qty = 0` test, and that test is not required to reach 100% branch coverage.
3. **Integer arithmetic.** GST and discounts use floor division (`//`), so amounts are rounded down. For example, clothing at 99: 99 × 12 = 1188, and 1188 // 100 = 11, giving a total of 110. A test pins this behaviour, so a later change to normal division would be caught.
4. **Untested input domain.**
   - `cart_discount` and `shipping_fee` do not validate negative `cart_value`.
   - `item_total` does not reject non-numeric input.
   - Coverage cannot reveal missing validation, because code that does not exist cannot be "uncovered".

## 10. Conclusion

| Metric | Before | After |
|---|---|---|
| Line coverage | 44% | **100%** |
| Branch coverage | 37% | **100%** |

Both targets (at least 90%) were exceeded.

The lab shows that line coverage alone can give false confidence. Branch coverage, combined with boundary-value and condition-level tests, gives much stronger evidence that the logic is correct.
