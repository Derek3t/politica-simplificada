DADOS = {"nome": "Ana Lima", "email": "ana@exemplo.com", "senha": "senha1234"}


def test_registro_cria_usuario_e_abre_sessao(client):
    resposta = client.post("/api/auth/registro", json=DADOS)

    assert resposta.status_code == 201
    assert resposta.json["usuario"]["email"] == "ana@exemplo.com"
    assert "senha" not in resposta.json["usuario"]
    assert client.get("/api/auth/me").status_code == 200


def test_registro_email_duplicado_retorna_409(client):
    client.post("/api/auth/registro", json=DADOS)

    resposta = client.post("/api/auth/registro", json={**DADOS, "email": "ANA@exemplo.com"})

    assert resposta.status_code == 409


def test_registro_valida_campos(client):
    resposta = client.post("/api/auth/registro", json={"nome": "A", "email": "invalido", "senha": "123"})

    assert resposta.status_code == 422
    assert set(resposta.json["detalhes"]) == {"nome", "email", "senha"}


def test_registro_sem_corpo_retorna_422(client):
    assert client.post("/api/auth/registro").status_code == 422


def test_login_com_credenciais_corretas(client):
    client.post("/api/auth/registro", json=DADOS)
    client.post("/api/auth/logout")

    resposta = client.post("/api/auth/login", json={"email": DADOS["email"], "senha": DADOS["senha"]})

    assert resposta.status_code == 200
    assert client.get("/api/auth/me").json["usuario"]["nome"] == "Ana Lima"


def test_login_com_senha_errada_retorna_401(client):
    client.post("/api/auth/registro", json=DADOS)
    client.post("/api/auth/logout")

    resposta = client.post("/api/auth/login", json={"email": DADOS["email"], "senha": "errada123"})

    assert resposta.status_code == 401


def test_me_sem_login_retorna_401(client):
    assert client.get("/api/auth/me").status_code == 401


def test_logout_encerra_sessao(usuario_logado):
    usuario_logado.post("/api/auth/logout")

    assert usuario_logado.get("/api/auth/me").status_code == 401


def test_rota_inexistente_retorna_json_em_portugues(client):
    resposta = client.get("/api/nao-existe")

    assert resposta.status_code == 404
    assert resposta.json["erro"] == "Recurso não encontrado."
