import pytest

from monitor import decide_alerts


def test_preco_igual_ou_abaixo_da_meta_dispara_alerta_de_meta():
    assert decide_alerts(100, 100, None) == (True, None)
    assert decide_alerts(90, 100, None) == (True, None)


def test_preco_acima_da_meta_sem_historico_nao_dispara_nada():
    assert decide_alerts(110, 100, None) == (False, None)


def test_queda_de_15_por_cento_dispara_alerta_de_queda():
    hit_target, pct = decide_alerts(85, 50, 100)
    assert hit_target is False
    assert pct == pytest.approx(15.0)


def test_queda_menor_que_15_por_cento_nao_dispara():
    assert decide_alerts(86, 50, 100) == (False, None)


def test_preco_subiu_ou_sem_preco_anterior_nao_e_queda():
    assert decide_alerts(120, 50, 100) == (False, None)
    assert decide_alerts(80, 50, 0) == (False, None)


def test_meta_e_queda_ao_mesmo_tempo():
    hit_target, pct = decide_alerts(50, 60, 100)
    assert hit_target is True
    assert pct == pytest.approx(50.0)
