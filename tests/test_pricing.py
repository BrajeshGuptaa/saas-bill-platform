from app.services.pricing import calculate_flat, calculate_tiered, calculate_volume


def test_calculate_flat():
    assert float(calculate_flat(10, 3)) == 30.0


def test_calculate_tiered():
    tiers = [
        {"up_to": 100, "unit_amount": 0.1},
        {"up_to": 200, "unit_amount": 0.05},
        {"up_to": None, "unit_amount": 0.03},
    ]
    assert float(calculate_tiered(tiers, 150)) == 12.5


def test_calculate_volume():
    tiers = [
        {"up_to": 100, "unit_amount": 0.1},
        {"up_to": 200, "unit_amount": 0.05},
        {"up_to": None, "unit_amount": 0.03},
    ]
    assert float(calculate_volume(tiers, 150)) == 7.5
