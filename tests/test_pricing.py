import pytest

from apartment_core import load
from apartment_core.furniture import Item, RoomFinish, Variant, load_variants
from apartment_core.pricing import estimate, load_prices, render_html
from apartment_core.validate import room_areas


@pytest.fixture(scope="module")
def apt():
    return load()


@pytest.fixture(scope="module")
def cat():
    return load_prices()


def _item(n, type_, room, size=(0.5, 0.5, 0.9)):
    return Item(id=f"T.{type_}-{room}-{n}", type=type_, room=room, size=size, position=(2, 8))


def _lines(sections):
    return [ln for s in sections for ln in s.lines]


def test_every_type_in_every_variant_is_priced(apt, cat):
    for v in load_variants():
        assert estimate(apt, v, cat).unpriced == [], v.key


def test_type_lookup_drops_leading_words(cat):
    assert cat.item_price("plush-corner-sofa") is cat.items["corner-sofa"]
    assert cat.item_price("black-sink") is cat.items["sink"]
    assert cat.item_price("no-such-thing") is None


def test_tiers_are_ordered(cat):
    for group in (cat.finishes, cat.fitout, cat.items):
        for key, p in group.items():
            assert p.price[0] <= p.price[1] <= p.price[2], key


def test_turnkey_variant_costs_only_door_upgrades_and_site(apt, cat):
    """Nothing changed and no furniture: floors, walls, paint, sanitary ware are the developer's."""
    est = estimate(apt, Variant(key="T", name="test"), cat)
    assert est.furniture_total == (0.0, 0.0, 0.0)
    titles = [s.title for s in est.fitout]
    assert "Floors" not in titles and "Wall coverings" not in titles
    door = next(ln for ln in _lines(est.fitout) if ln.label.startswith("Interior door"))
    assert door.total[0] == 0  # low = keep the developer's door


def test_changed_floor_pays_material_over_allowance(apt, cat):
    v = Variant(key="T", name="test", rooms={"living": RoomFinish(floor="walnut"), "kitchen": RoomFinish(
        floor="calacatta_gold"), "balcony": RoomFinish(floor="deck")})
    lines = {ln.label: ln for ln in _lines(estimate(apt, v, cat).fitout)}
    living = lines["Living: Walnut (upgrade)"]
    parquet = cat.finishes["parquet"]
    assert living.unit_price == tuple(max(0, m - 65) for m in parquet.material)
    assert "Balcony: Deck" in lines  # not in the turnkey list: full supply + laying
    assert lines["Balcony: Deck"].unit_price == cat.finishes["deck"].price
    large = next(ln for label, ln in lines.items() if label.startswith("Laying surcharge"))
    assert large.qty == pytest.approx(room_areas(apt)["kitchen"], rel=0.03)  # 60x120 > 60x60 (real floor area)


def test_developer_pieces_are_credited(apt, cat):
    v = Variant(key="T", name="test", items=[
        _item(1, "bathtub", "bath_2"), _item(1, "toilet", "bath_2"),
        _item(1, "air-conditioner", "living"), _item(2, "air-conditioner", "bedroom_1"),
        _item(1, "heat-recovery-vent", "living"),
    ])
    est = estimate(apt, v, cat)
    credits = {ln.label: ln for ln in _lines(est.furniture) if ln.total[1] < 0}
    tub = credits["Included by the developer: bathtub + mixer (Bath 2)"]
    assert tub.total == (-900, -900, -900)
    ac = credits["Included by the developer: 1 AC unit, installed"]
    assert ac.total[1] == -2800  # one unit, not both
    vent = credits["Included by the developer: 2 heat-recovery ventilation units"]
    assert -vent.total[1] == min(cat.items["heat-recovery-vent"].price[1], 3200)  # only one in the variant
    assert any("shower tray" in u for u in est.unused)
    gross = sum(cat.items[t].price[1] for t in ("bathtub", "toilet", "heat-recovery-vent")) + 2 * cat.items[
        "air-conditioner"].price[1]
    assert est.furniture_total[1] == pytest.approx(gross + sum(c.total[1] for c in credits.values()))
    assert est.furniture_total[1] < gross


def test_furniture_is_never_included(apt, cat):
    v = Variant(key="T", name="test", items=[
        _item(1, "wardrobe", "living", (2.0, 0.6, 2.5)), _item(1, "chair", "living"), _item(2, "chair", "living"),
        _item(1, "mug", "living", (0.1, 0.1, 0.1)),
    ])
    est = estimate(apt, v, cat)
    assert est.personal == ["T.mug-living-1"]
    assert est.furniture_total[1] == pytest.approx(cat.items["wardrobe"].price[1] * 5 + cat.items["chair"].price[1] * 2)


def test_html_page(apt, cat):
    v = next(v for v in load_variants() if v.key == "V1")
    page = render_html(estimate(apt, v, cat), apt)
    assert page.startswith("<!doctype html>") and "Price list - variant V1" in page
    assert "turnkey" in page and "Included by the developer" in page
