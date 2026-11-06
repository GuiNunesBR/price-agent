from busca import extrair_candidatos
from scrapers.base import parse_brl
from scrapers.electrolux import price_from_vtex


def _vtex_produto(nome, preco, disponivel=True, link="produto-x"):
    return {
        "productName": nome,
        "linkText": link,
        "items": [
            {"sellers": [{"commertialOffer": {"Price": preco, "IsAvailable": disponivel}}]}
        ],
    }


def test_parse_brl_formato_brasileiro():
    assert parse_brl("R$ 1.234,56") == 1234.56
    assert parse_brl("R$ 3.499,90") == 3499.90
    assert parse_brl("R$ 99") == 99.0


def test_parse_brl_ponto_decimal():
    assert parse_brl("1234.56") == 1234.56


def test_parse_brl_texto_sem_numero():
    assert parse_brl("") is None
    assert parse_brl("Indisponível") is None


def test_price_from_vtex_produto_disponivel():
    assert price_from_vtex([_vtex_produto("Geladeira", 3999.9)]) == 3999.9


def test_price_from_vtex_indisponivel_ou_sem_preco():
    assert price_from_vtex([_vtex_produto("Geladeira", 3999.9, disponivel=False)]) is None
    assert price_from_vtex([_vtex_produto("Geladeira", 0)]) is None
    assert price_from_vtex([]) is None


def test_extrair_candidatos_filtra_e_monta_url():
    produtos = [
        _vtex_produto("Geladeira Inverter 400L", 3899.0, link="geladeira-inverter"),
        _vtex_produto("Geladeira Frost Free", 2999.0, disponivel=False),
        _vtex_produto("Tampa de Geladeira", 38.0),
        _vtex_produto("Geladeira sem preco", 0),
        {"productName": "Sem itens", "items": []},
    ]
    candidatos = extrair_candidatos("electrolux", "https://loja.exemplo.com.br", produtos)
    assert candidatos == [
        {
            "loja": "electrolux",
            "nome": "Geladeira Inverter 400L",
            "preco": 3899.0,
            "url": "https://loja.exemplo.com.br/geladeira-inverter/p",
        }
    ]
