from pydantic import ValidationError

from politica.errors import ErroValidacao

MENSAGENS = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Deve ter no mínimo {min_length} caracteres.",
    "string_too_long": "Deve ter no máximo {max_length} caracteres.",
    "value_error": "E-mail inválido.",
    "date_parsing": "Data inválida, use AAAA-MM-DD.",
    "date_from_datetime_parsing": "Data inválida, use AAAA-MM-DD.",
    "int_parsing": "Deve ser um número inteiro.",
    "bool_parsing": "Deve ser verdadeiro ou falso.",
    "greater_than_equal": "Deve ser maior ou igual a {ge}.",
    "less_than_equal": "Deve ser menor ou igual a {le}.",
}


def _traduzir(erro):
    modelo = MENSAGENS.get(erro["type"], "Valor inválido.")
    try:
        return modelo.format(**erro.get("ctx", {}))
    except KeyError:
        return modelo


def validar(schema, dados):
    try:
        return schema.model_validate(dados or {})
    except ValidationError as excecao:
        detalhes = {".".join(str(parte) for parte in e["loc"]): _traduzir(e) for e in excecao.errors()}
        raise ErroValidacao(detalhes) from excecao
