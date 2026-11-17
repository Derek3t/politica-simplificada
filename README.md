# Política Simplificada

Plataforma que traduz a agenda do Congresso Brasileiro para linguagem simples: votações e projetos de lei do dia, feriados e datas cívicas (nacionais e estaduais), perfil de deputados e senadores com o histórico de como votaram e resumos gerados por IA.

O repositório tem duas pastas: `backend/` (API JSON em Flask) e `frontend/` (Vue.js com Vite e Tailwind). A documentação técnica fica em `docs/`.

## Backend

Requer Python 3.10+. Os comandos abaixo rodam dentro de `backend/`.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"   # ou: pip install -r requirements-dev.txt
cp .env.example .env
flask db upgrade
flask importar-parlamentares
flask run
```

A API sobe em `http://localhost:5001/api`. A porta 5000 não é usada porque o AirPlay Receiver do macOS a ocupa; ela está definida em `backend/.flaskenv`. Para o login com Google, veja a seção [Login com Google](#login-com-google). Em produção (`APP_ENV=production`) o app se recusa a subir sem uma `SECRET_KEY` própria. Sem `GEMINI_API_KEY` em `backend/.env` as rotas de análise com IA respondem 503; o resto funciona normalmente.

### Login com Google

O login usa OAuth 2.0 / OpenID Connect (Authlib) e também pede permissão para criar eventos no Google Calendar do usuário. Cadastro e login por e-mail e senha continuam funcionando; se o e-mail da conta Google já existir, as contas são vinculadas.

1. No [Google Cloud Console](https://console.cloud.google.com/), crie um projeto e ative a **Google Calendar API**.
2. Em **Google Auth Platform**, configure a tela de consentimento (público Externo) e adicione seu e-mail como usuário de teste.
3. Crie um **ID do cliente OAuth** do tipo *Aplicativo da Web* com origem `http://localhost:5173` e URI de redirecionamento `http://localhost:5173/api/auth/google/callback`.
4. Preencha em `backend/.env`: `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` (os demais valores do `.env.example` já servem para o desenvolvimento).

Sem essas variáveis, `/api/auth/google/login` responde 503 e o resto do sistema funciona. O fluxo passa pelo proxy do Vite (porta 5173), então o cookie de sessão fica no mesmo endereço do frontend.

### Comandos do backend

| Comando | O que faz |
|---|---|
| `flask importar-parlamentares` | Importa os deputados (API da Câmara) e os senadores (API do Senado) |
| `flask sincronizar-agenda AAAA-MM-DD` | Pré-carrega a agenda de um dia (padrão: hoje) |
| `flask precarregar` | Pré-carrega parlamentares, agendas dos próximos e últimos dias, votações dos últimos 90 dias e os votos individuais |
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

### Estrutura

```
backend/
  app.py                ponto de entrada (flask run)
  politica/
    __init__.py         create_app (application factory)
    config.py           configurações por ambiente (APP_ENV)
    extensions.py       db, migrate, cors
    errors.py           exceções da API e handlers JSON
    validacao.py        validação de entrada com Pydantic
    cli.py              comandos flask
    precarga.py         pré-carga de dados para demonstração
    auth/               cadastro, login e sessão
    legislation/        agenda, projetos, votações, parlamentares, integrações externas
      datas_civicas.py  contexto de feriados, datas cívicas e feriados estaduais (sem IA)
      senado.py         senadores e votações do Plenário do Senado
      votos.py          votos individuais, placar e perfil do parlamentar
    calendar_sync/      exportação em .ics e criação de eventos no Google Calendar
  migrations/           Alembic
  tests/                pytest
frontend/               SPA Vue 3 (src/api, components, views, composables, utils)
docs/                   documentação técnica em PDF e gerador
```

### Endpoints

| Método | Rota | Auth |
|---|---|---|
| POST | `/api/auth/registro`, `/api/auth/login`, `/api/auth/logout` | |
| GET | `/api/auth/me` | sim |
| GET | `/api/auth/google/login`, `/api/auth/google/callback` | |
| GET | `/api/legislation/agenda?data=AAAA-MM-DD&apenas_seguidos=&uf=` | opcional |
| GET | `/api/legislation/projetos/<id>` | opcional |
| POST | `/api/legislation/projetos/<id>/analisar` | sim |
| POST | `/api/legislation/dias-especiais/<id>/contextualizar` | sim |
| GET | `/api/legislation/busca?q=` | opcional |
| GET | `/api/legislation/calendario?mes=AAAA-MM&uf=` | |
| GET | `/api/legislation/votacoes?periodo=hoje\|semana\|mes&status=aprovado\|rejeitado\|andamento&casa=Câmara\|Senado&pagina=` | |
| GET | `/api/legislation/votacoes/<id>` (placar e votos de quem o usuário segue) | opcional |
| GET | `/api/legislation/parlamentares?busca=&estado=&partido=&casa=&pagina=&por_pagina=` | opcional |
| GET | `/api/legislation/parlamentares/<id>` (perfil, histórico de votos e autorias) | opcional |
| GET | `/api/legislation/parlamentares/seguidos` | sim |
| POST, DELETE | `/api/legislation/parlamentares/<id>/seguir` | sim |
| GET | `/api/calendar/projetos/<id>.ics` | sim |
| POST | `/api/calendar/projetos/<id>/google` | sim, conta Google |

## Limitações conhecidas

- A busca global procura apenas em dados já consultados e salvos no banco (agendas visitadas, votações sincronizadas e parlamentares importados).
- Pautas e agenda diária vêm só da Câmara. Do Senado entram os senadores e as votações nominais de projetos (PEC, PLP, PL, PDL...), sem pauta.
- O histórico de posições mostra só votações nominais: votação simbólica não registra o voto individual. A janela é de 90 dias; os votos são baixados uma vez e guardados no banco.
- Feriados estaduais são de data fixa e cobrem 23 UFs (as demais não têm feriado estadual de data fixa próprio), de uma lista curada à mão em `datas_civicas.py` (não inclui feriados móveis nem municipais). O estado é escolhido pelo usuário e fica no navegador.
- Feriados nacionais e datas cívicas têm texto de contexto escrito à mão e funcionam sem IA; a chave do Gemini só é necessária para resumir projetos de lei e explicar datas fora dessa lista.
- Votações só entram se forem de mérito (projetos, PECs, MPs). Requerimentos e mudanças de regime de tramitação são ignorados.
- A autoria de projetos só é vinculada aos parlamentares para pautas do Plenário.
- Votações ficam em cache por 10 minutos. Se a API da Câmara estiver fora, são exibidos os dados já salvos.

## Documentação

O PDF de entrega fica em `docs/Documentacao_PoliticaSimplificada.pdf`. Ele é gerado a partir do código real (diagrama ER pelos metadados dos modelos, trechos de código e contagem de testes), com as capturas de `docs/img`.

Para regerar após mudar o código, com o Google Chrome instalado:

```bash
cd backend && pip install -e ".[docs]" && cd ..
backend/venv/bin/python docs/gerar_documentacao.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/Documentacao_PoliticaSimplificada.pdf "file://$PWD/docs/documentacao.html"
```

Para montar o zip de entrega (backend, frontend, README e o PDF, sem `venv`, `node_modules`, caches, `.env` e banco local; use `--com-git` para incluir a pasta `.git`):

```bash
python docs/gerar_zip.py NomeDoZip
```

O roteiro da apresentação, com o que mostrar e o que explicar em cada critério, está em `docs/roteiro_apresentacao.md`.
