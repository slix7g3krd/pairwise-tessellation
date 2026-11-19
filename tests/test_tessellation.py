import pytest
from render import tessellation as mod

CASES = [
    ("screen", 'm.screen_factor(2.0, 4.0) == approx(2.0)'),
    ("seam", 'm.uv_seam(0.5, 0.5) == approx(0.0)'),
    ("seam_off", 'm.uv_seam(0.2, 0.5) == approx(0.3)'),
    ("uv_match", 'm.uv_set_match(0, 0) is True'),
    ("uv_diff", 'm.uv_set_match(0, 1) is False'),
    ("winding", 'm.winding_flip((0, 1, 2), True) == (2, 1, 0)'),
    ("winding_no", 'm.winding_flip((0, 1, 2), False) == (0, 1, 2)'),
    ("shadow", 'm.shadow_factor(8.0, 4.0) == approx(4.0)'),
    ("lod", 'm.lod_factor(1.0, 2) == approx(4.0)'),
    ("disp", 'm.scaled_displacement(1.0, 2.0) == approx(2.0)'),
    ("water", 'm.watertight_edge(1.0, 1.0) is True'),
    ("skin", 'm.skin_before_tess(0.5) == approx(0.5)'),
    ("platform", 'm.platform_limit(16, 8) == 8'),
    ("frame", 'm.frame_factor(1.0, 3.0) == approx(2.0)'),
    ("bounds", 'm.bounds_expand((0.0, 1.0), 2.0) == approx((-2.0, 3.0))')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
