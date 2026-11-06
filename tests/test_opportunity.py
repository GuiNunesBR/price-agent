from opportunity import evaluate_offer, normalize_text

GELADEIRA = {
    "required_keywords": ["Electrolux", "Inverter"],
    "blocked_keywords": ["usado", "recondicionado"],
    "target_price_range": {"min": 3500, "max": 4200},
}


def test_normalize_text_remove_acentos_caixa_e_espacos():
    assert normalize_text("  Ação   RÁPIDA ") == "acao rapida"


def test_oferta_na_faixa_com_palavras_obrigatorias_gera_alerta():
    result = evaluate_offer(GELADEIRA, title="Geladeira Electrolux Inverter 400L", price=3800)
    assert result.matches_product
    assert result.should_alert
    assert result.score == 80
    assert "required_keywords_matched" in result.reasons
    assert "price_in_target_range" in result.reasons


def test_palavra_proibida_descarta_oferta_mesmo_com_preco_bom():
    result = evaluate_offer(GELADEIRA, title="Geladeira Electrolux Inverter USADO", price=3600)
    assert not result.matches_product
    assert not result.should_alert
    assert result.score == 0
    assert result.reasons == ["blocked_keyword"]


def test_palavras_obrigatorias_ignoram_acento_e_caixa():
    produto = {"required_keywords": ["refrigeração"], "target_price": 5000}
    result = evaluate_offer(produto, title="Linha REFRIGERACAO Frost Free", price=4000)
    assert result.matches_product
    assert result.should_alert


def test_falta_palavra_obrigatoria_nao_alerta():
    result = evaluate_offer(GELADEIRA, title="Geladeira Electrolux 400L", price=3800)
    assert not result.matches_product
    assert not result.should_alert
    assert result.score == 60  # metade das palavras (20) + faixa de preco (40)
    assert "missing_required_keywords" in result.reasons


def test_preco_abaixo_do_minimo_da_faixa_nao_alerta_sem_queda():
    result = evaluate_offer(GELADEIRA, title="Geladeira Electrolux Inverter", price=3000)
    assert not result.should_alert
    assert "price_in_target_range" not in result.reasons


def test_target_price_substitui_maximo_da_faixa():
    produto = {"target_price": 1000, "target_price_range": {"max": 500}}
    assert evaluate_offer(produto, title="qualquer", price=1000).should_alert
    assert not evaluate_offer(produto, title="qualquer", price=1000.01).should_alert


def test_sem_palavras_obrigatorias_qualquer_titulo_serve():
    result = evaluate_offer({"target_price": 100}, title="Produto X", price=90)
    assert result.matches_product
    assert result.should_alert


def test_queda_de_15_por_cento_alerta_mesmo_fora_da_faixa():
    result = evaluate_offer(
        GELADEIRA, title="Geladeira Electrolux Inverter", price=4250, previous_min=5000
    )
    assert result.should_alert
    assert "price_in_target_range" not in result.reasons
    assert any(r.startswith("price_drop_15.0") for r in result.reasons)
    assert result.score == 60  # palavras (40) + queda (20)


def test_queda_menor_que_15_por_cento_nao_alerta_fora_da_faixa():
    result = evaluate_offer(
        GELADEIRA, title="Geladeira Electrolux Inverter", price=4300, previous_min=5000
    )
    assert not result.should_alert


def test_score_limitado_a_100():
    result = evaluate_offer(
        GELADEIRA, title="Geladeira Electrolux Inverter", price=3500, previous_min=10000
    )
    assert result.score == 100
