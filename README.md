# Política Simplificada

Plataforma que traduz a agenda do Congresso Brasileiro para linguagem simples: votações e projetos de lei do dia, feriados e datas cívicas, perfil de parlamentares e resumos gerados por IA.

Backend em Flask (API JSON) e frontend em Vue.js (Vite + Tailwind).

## Backend

Requer Python 3.10+.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
flask db upgrade
flask importar-parlamentares
flask run
```

A API sobe em `http://localhost:5001/api`. A porta 5000 não é usada porque o AirPlay Receiver do macOS a ocupa; ela está definida em `.flaskenv`. Em produção (`APP_ENV=production`) o app se recusa a subir sem uma `SECRET_KEY` própria. Sem `GEMINI_API_KEY` no `.env` as rotas de análise com IA respondem 503; o resto funciona normalmente.

### Comandos do backend

| Comando | O que faz |
|---|---|
| `flask importar-parlamentares` | Importa os deputados da API da Câmara |
| `flask sincronizar-agenda AAAA-MM-DD` | Pré-carrega a agenda de um dia (padrão: hoje) |
| `flask precarregar` | Pré-carrega deputados, agendas dos próximos e últimos dias e votações do mês |
| `pytest` | Roda os testes automatizados |
| `ruff check . && ruff format --check .` | Verifica lint e formatação |

## Frontend

Requer Node 20+. Com o backend rodando:

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`. O Vite encaminha `/api` para o Flask. Testes: `npm test`.

### Pré-carga para apresentação

A primeira consulta de cada dia leva alguns segundos e depende da API da Câmara estar no ar. Para a demonstração, rode antes:

```bash
flask precarregar                  # 7 dias antes e 10 depois de hoje, mais as votações do mês
flask precarregar --ia             # também gera resumos e contextos com o Gemini (exige GEMINI_API_KEY)
flask precarregar --passados 3 --futuros 14 --limite-ia 10
```

O comando é idempotente: se a Câmara falhar em algum dia ele avisa, termina com erro e basta rodar de novo para completar só o que faltou. Com `--ia`, os resumos são gerados para os projetos do Plenário mais próximos de hoje e ficam salvos no banco.

### Estrutura do backend

```
politica/
  __init__.py         create_app (application factory)
  config.py           configurações por ambiente (APP_ENV)
  extensions.py       db, migrate, cors
  errors.py           exceções da API e handlers JSON
  validacao.py        validação de entrada com Pydantic
  cli.py              comandos flask
  precarga.py         pré-carga de dados para demonstração
  auth/               cadastro, login e sessão
  legislation/        agenda, projetos, parlamentares, integrações externas
  calendar_sync/      exportação de eventos em .ics
migrations/           Alembic
tests/                pytest
```

### Endpoints

| Método | Rota | Auth |
|---|---|---|
| POST | `/api/auth/registro`, `/api/auth/login`, `/api/auth/logout` | |
| GET | `/api/auth/me` | sim |
| GET | `/api/legislation/agenda?data=AAAA-MM-DD&apenas_seguidos=` | opcional |
| GET | `/api/legislation/projetos/<id>` | opcional |
| POST | `/api/legislation/projetos/<id>/analisar` | sim |
| POST | `/api/legislation/dias-especiais/<id>/contextualizar` | sim |
| GET | `/api/legislation/busca?q=` | opcional |
| GET | `/api/legislation/calendario?mes=AAAA-MM` | |
| GET | `/api/legislation/votacoes?periodo=hoje\|semana\|mes&status=aprovado\|rejeitado\|andamento&pagina=` | |
| GET | `/api/legislation/parlamentares?busca=&estado=&partido=&pagina=&por_pagina=` | opcional |
| GET | `/api/legislation/parlamentares/seguidos` | sim |
| POST, DELETE | `/api/legislation/parlamentares/<id>/seguir` | sim |
| GET | `/api/calendar/projetos/<id>.ics` | sim |

## Limitações conhecidas

- A busca global procura apenas em dados já consultados e salvos no banco (agendas visitadas, votações sincronizadas e parlamentares importados).
- Apenas a Câmara dos Deputados é consultada. Sessões do Congresso Nacional e o Senado não estão incluídos.
- Votações só entram se forem de mérito (projetos, PECs, MPs). Requerimentos e mudanças de regime de tramitação são ignorados.
- A autoria de projetos só é vinculada aos parlamentares para pautas do Plenário.
- Votações ficam em cache por 10 minutos. Se a API da Câmara estiver fora, são exibidos os dados já salvos.

## Documentação

O PDF de entrega fica em `docs/Documentacao_PoliticaSimplificada.pdf`. Ele é gerado a partir do código real (diagrama ER pelos metadados dos modelos, trechos de código e contagem de testes), com as capturas de `docs/img`.

Para regerar após mudar o código, com o Google Chrome instalado:

```bash
pip install -e ".[docs]"
python docs/gerar_documentacao.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/Documentacao_PoliticaSimplificada.pdf "file://$PWD/docs/documentacao.html"
```
