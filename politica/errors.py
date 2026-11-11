import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

MENSAGENS_HTTP = {
    404: "Recurso não encontrado.",
    405: "Método não permitido para este endereço.",
    415: "Envie o corpo da requisição em JSON.",
}


class ErroApi(Exception):
    def __init__(self, mensagem, status=400, detalhes=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.detalhes = detalhes


class ErroValidacao(ErroApi):
    def __init__(self, detalhes):
        super().__init__("Dados inválidos.", 422, detalhes)


class ErroServicoExterno(ErroApi):
    def __init__(self, mensagem):
        super().__init__(mensagem, 502)


def resposta_erro(mensagem, status, detalhes=None):
    corpo = {"erro": mensagem}
    if detalhes:
        corpo["detalhes"] = detalhes
    return jsonify(corpo), status


def registrar_handlers(app):
    @app.errorhandler(ErroApi)
    def tratar_erro_api(erro):
        if erro.status >= 500:
            logger.warning("%s: %s", erro.status, erro.mensagem)
        return resposta_erro(erro.mensagem, erro.status, erro.detalhes)

    @app.errorhandler(HTTPException)
    def tratar_http(erro):
        return resposta_erro(MENSAGENS_HTTP.get(erro.code, erro.description), erro.code)

    @app.errorhandler(Exception)
    def tratar_inesperado(erro):
        logger.exception("Erro não tratado")
        return resposta_erro("Erro interno do servidor.", 500)
