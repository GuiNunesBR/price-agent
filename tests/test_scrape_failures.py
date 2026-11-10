import pytest

import monitor
import notifier

ITEM = {
    "name": "Geladeira",
    "url": "https://www.kabum.com.br/produto/123",
    "target_price": 1000,
}


class FakeScraper:
    def __init__(self, result):
        self.result = result

    def scrape(self, url):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@pytest.fixture
def state(monkeypatch):
    """Substitui banco e Telegram por um estado em memoria."""
    st = {"failures": 0, "events": [], "saved": []}

    def record_scrape_failure(name, url, store, reason):
        st["failures"] += 1
        st["events"].append(("record", store, reason))

    def save_price(name, price):
        st["saved"].append(price)
        st["failures"] = 0  # um preco salvo encerra a sequencia de falhas

    monkeypatch.setattr(monitor, "upsert_product", lambda item: 1)
    monkeypatch.setattr(monitor, "record_scrape_failure", record_scrape_failure)
    monkeypatch.setattr(monitor, "count_consecutive_failures", lambda name: st["failures"])
    monkeypatch.setattr(monitor, "get_last_price", lambda name: None)
    monkeypatch.setattr(monitor, "save_price", save_price)
    monkeypatch.setattr(
        monitor, "send_scrape_error", lambda *args: st["events"].append(("alerta_falha",) + args)
    )
    monkeypatch.setattr(
        monitor, "send_scrape_recovered", lambda *args: st["events"].append(("recuperou",) + args)
    )
    monkeypatch.setattr(monitor, "send_target_alert", lambda *args: st["events"].append(("meta",)))
    monkeypatch.setattr(monitor, "send_drop_alert", lambda *args: st["events"].append(("queda",)))
    monkeypatch.setattr(monitor, "FAILURE_ALERT_AFTER", 3)
    return st


def _check(monkeypatch, result):
    monkeypatch.setattr(monitor, "get_scraper", lambda url: FakeScraper(result))
    monitor.check_product(ITEM)


def _alerts(state, kind):
    return [e for e in state["events"] if e[0] == kind]


def test_should_alert_failure_dispara_so_ao_atingir_o_limite():
    assert not monitor.should_alert_failure(2, 3)
    assert monitor.should_alert_failure(3, 3)
    assert not monitor.should_alert_failure(4, 3)


def test_scrape_recovered_so_depois_de_sequencia_alertada():
    assert not monitor.scrape_recovered(0, 3)
    assert not monitor.scrape_recovered(2, 3)
    assert monitor.scrape_recovered(3, 3)


def test_store_from_url_remove_www():
    assert monitor.store_from_url("https://www.amazon.com.br/dp/X") == "amazon.com.br"
    assert monitor.store_from_url("https://loja.electrolux.com.br/p") == "loja.electrolux.com.br"


def test_falhas_sao_gravadas_e_alertam_uma_vez_no_limite(monkeypatch, state):
    for _ in range(4):
        _check(monkeypatch, None)

    records = _alerts(state, "record")
    assert len(records) == 4
    assert records[0] == ("record", "kabum.com.br", "preco_nao_encontrado")

    alerts = _alerts(state, "alerta_falha")
    assert alerts == [
        ("alerta_falha", "Geladeira", ITEM["url"], 3, "preco_nao_encontrado"),
    ]
    assert state["saved"] == []


def test_excecao_do_scraper_vira_falha_registrada(monkeypatch, state):
    _check(monkeypatch, TimeoutError("page took too long"))

    assert _alerts(state, "record") == [
        ("record", "kabum.com.br", "TimeoutError: page took too long")
    ]
    assert state["saved"] == []


def test_preco_depois_de_sequencia_alertada_avisa_recuperacao(monkeypatch, state):
    for _ in range(3):
        _check(monkeypatch, None)
    _check(monkeypatch, 1500.0)

    assert state["saved"] == [1500.0]
    assert _alerts(state, "recuperou") == [("recuperou", "Geladeira", ITEM["url"], 3)]
    assert state["failures"] == 0


def test_falha_isolada_seguida_de_preco_nao_gera_nenhum_aviso(monkeypatch, state):
    _check(monkeypatch, None)
    _check(monkeypatch, 1500.0)

    assert _alerts(state, "alerta_falha") == []
    assert _alerts(state, "recuperou") == []
    assert state["saved"] == [1500.0]


def test_loja_sem_scraper_e_erro_de_configuracao(monkeypatch, state):
    item = dict(ITEM, url="https://loja-desconhecida.com.br/produto")
    with pytest.raises(ValueError):
        monitor.check_product(item)
    assert _alerts(state, "record") == []


def test_alerta_de_falha_escapa_html_do_erro(monkeypatch):
    enviados = []
    monkeypatch.setattr(notifier, "send_message", enviados.append)
    notifier.send_scrape_error("Geladeira", "https://x", 3, "<html> inesperado & quebrado")
    assert "&lt;html&gt; inesperado &amp; quebrado" in enviados[0]
    assert "Falhas seguidas:</b> 3" in enviados[0]
