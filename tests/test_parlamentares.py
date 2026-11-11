from politica.extensions import db
from politica.legislation.models import Parlamentar


def criar_parlamentares():
    db.session.add_all(
        [
            Parlamentar(id_original=1, nome="Carlos Dias", partido="PL", estado="SP"),
            Parlamentar(id_original=2, nome="Carla Nunes", partido="PT", estado="ES"),
            Parlamentar(id_original=3, nome="Bruno Alves", partido="PT", estado="SP"),
        ]
    )
    db.session.commit()


def test_listagem_filtra_por_nome_estado_e_partido(client, app):
    criar_parlamentares()

    assert client.get("/api/legislation/parlamentares?busca=car").json["total"] == 2
    assert client.get("/api/legislation/parlamentares?estado=sp").json["total"] == 2
    assert client.get("/api/legislation/parlamentares?partido=pt&estado=ES").json["total"] == 1


def test_listagem_pagina_resultados(client, app):
    criar_parlamentares()

    corpo = client.get("/api/legislation/parlamentares?por_pagina=2&pagina=2").json

    assert len(corpo["itens"]) == 1
    assert corpo["total_paginas"] == 2


def test_listagem_valida_parametros(client):
    resposta = client.get("/api/legislation/parlamentares?pagina=0&por_pagina=500&estado=XYZ")

    assert resposta.status_code == 422
    assert set(resposta.json["detalhes"]) == {"pagina", "por_pagina", "estado"}


def test_seguir_exige_login(client, parlamentar):
    assert client.post(f"/api/legislation/parlamentares/{parlamentar.id}/seguir").status_code == 401


def test_seguir_e_deixar_de_seguir(usuario_logado, parlamentar):
    url = f"/api/legislation/parlamentares/{parlamentar.id}/seguir"

    assert usuario_logado.post(url).status_code == 201
    assert usuario_logado.get("/api/legislation/parlamentares/seguidos").json["itens"][0]["nome"] == "Maria Souza"
    assert usuario_logado.get("/api/legislation/parlamentares").json["itens"][0]["seguido"] is True
    assert usuario_logado.delete(url).status_code == 204
    assert usuario_logado.get("/api/legislation/parlamentares/seguidos").json["itens"] == []


def test_seguir_duas_vezes_retorna_409(usuario_logado, parlamentar):
    url = f"/api/legislation/parlamentares/{parlamentar.id}/seguir"
    usuario_logado.post(url)

    assert usuario_logado.post(url).status_code == 409


def test_seguir_parlamentar_inexistente_retorna_404(usuario_logado):
    assert usuario_logado.post("/api/legislation/parlamentares/999/seguir").status_code == 404


def test_deixar_de_seguir_quem_nao_segue_retorna_404(usuario_logado, parlamentar):
    assert usuario_logado.delete(f"/api/legislation/parlamentares/{parlamentar.id}/seguir").status_code == 404
