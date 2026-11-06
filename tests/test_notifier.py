import notifier


class _FakeResponse:
    ok = True
    status_code = 200
    text = "ok"


def _post_proibido(*args, **kwargs):
    raise AssertionError("nao deveria chamar o Telegram")


def test_sem_credenciais_cai_no_console(monkeypatch, capsys):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setattr(notifier.requests, "post", _post_proibido)
    assert notifier.send_message("alerta de teste") is True
    assert "alerta de teste" in capsys.readouterr().out


def test_secrets_vazios_do_github_actions_caem_no_console(monkeypatch, capsys):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "")
    monkeypatch.setattr(notifier.requests, "post", _post_proibido)
    assert notifier.send_message("alerta vazio") is True
    assert "alerta vazio" in capsys.readouterr().out


def test_com_credenciais_envia_ao_telegram(monkeypatch):
    chamadas = []

    def fake_post(url, json, timeout):
        chamadas.append((url, json))
        return _FakeResponse()

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    monkeypatch.setattr(notifier.requests, "post", fake_post)
    assert notifier.send_message("oi") is True
    assert chamadas == [
        (
            "https://api.telegram.org/bot123:abc/sendMessage",
            {"chat_id": "42", "text": "oi", "parse_mode": "HTML"},
        )
    ]


def test_format_brl():
    assert notifier._format_brl(3499.9) == "R$ 3.499,90"
    assert notifier._format_brl(1234567.5) == "R$ 1.234.567,50"
