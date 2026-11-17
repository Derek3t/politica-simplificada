# Roteiro de apresentação (18/11/2026)

Cada integrante precisa saber explicar ao menos um critério, porque a participação vale 3 pontos.

## Antes de entrar na sala

```bash
cd backend && source venv/bin/activate
flask db upgrade && flask importar-parlamentares && flask precarregar
flask run                      # terminal 1 (porta 5001)
cd ../frontend && npm run dev  # terminal 2 (porta 5173)
```

- Rode o `flask precarregar` pelo menos uma vez com internet: sem ele a primeira consulta de cada dia leva alguns segundos.
- Deixe uma conta criada e logada, seguindo 2 ou 3 parlamentares.
- Se for mostrar o login com Google, só contas cadastradas como usuários de teste entram (modo "Testing" no Google Cloud).
- Deixe o PDF aberto e rode `pytest` e `ruff check .` uma vez para ver tudo verde.

## Demonstração (cerca de 5 minutos)

1. **Agenda:** abra uma data com votação (por exemplo 23/04/2026), troque “Meu estado” para RJ e mostre o feriado estadual e a votação. Abra “Ver detalhes”.
2. **Votações:** filtre por Senado, abra uma votação nominal e mostre o placar. Mostre os parlamentares seguidos (precisa estar logado).
3. **Perfil do parlamentar:** clique em um senador e mostre o histórico de posições.
4. **Calendário e busca:** mostre os marcadores do mês e uma busca global.
5. **Login com Google e Calendar:** entre com o Google e adicione uma votação ao Google Calendar. Alternativa sem login: baixar o `.ics`.
6. **Responsivo:** reduza a janela para 390 px e mostre o menu inferior.
7. **Falha externa (opcional):** desligue a internet e mostre que os dados já salvos continuam aparecendo e o erro é claro.

## O que explicar em cada critério

| Critério | Onde mostrar | O que dizer |
|---|---|---|
| 1. Application Factory | `backend/politica/__init__.py` (`create_app`), `config.py`, `extensions.py` | A fábrica recebe a configuração; os testes usam banco em memória; em produção o app se recusa a subir com a chave padrão. |
| 2. Blueprints e rotas | `backend/politica/auth/`, `legislation/`, `calendar_sync/` | Três blueprints com routes, services, models e schemas; as rotas só orquestram. |
| 3. Formulários e validação | `backend/politica/validacao.py`, `auth/schemas.py`, `frontend/src/components/FormCampo.vue` | Pydantic valida no servidor e devolve 422 por campo; o Vue mostra cada erro no campo certo. |
| 4. Interface | `frontend/src/views/`, `SidebarMenu.vue` | Vue 3 + Tailwind, layout responsivo, estados de carregando, vazio e erro. |
| 5. Testes | `backend/tests/`, `frontend/tests/` | 147 testes de backend e 48 de frontend; integrações externas simuladas, e o fixture `sem_rede` bloqueia chamadas reais. |
| 6. Persistência e ORM | `backend/politica/*/models.py`, `backend/migrations/` | 9 tabelas, relacionamentos 1:N e N:N, restrições de unicidade, 5 migrations; diagrama ER na seção 3 do PDF. |
| 7. Qualidade | `.env.example`, `errors.py`, `integracoes.py` (`_buscar_json`), `ruff` | Variáveis de ambiente, logging, erros em JSON, timeout e novas tentativas nas APIs externas, lint e commits por funcionalidade. |

## Perguntas prováveis

- **Por que Pydantic e não Flask-WTF?** O frontend é uma SPA que envia JSON, não formulários HTML.
- **Onde ficam os segredos?** No `backend/.env`, fora do git. O `.env.example` mostra as variáveis sem valores.
- **Como o cookie de sessão é protegido?** `HttpOnly`, `SameSite=Lax`, `Secure` em produção e CORS restrito às origens configuradas.
- **Como o login com Google funciona?** OAuth 2.0 / OpenID Connect com Authlib. O servidor valida o token, exige e-mail verificado, vincula a conta por `google_id` ou e-mail e guarda o refresh token para o Calendar.
- **E a IA?** O código do Gemini está pronto e testado com respostas simuladas, mas exige uma chave pessoal. O contexto de feriados e datas cívicas é curado e não depende dela.
- **O que ficou de fora?** Pauta diária do Senado (não existe endpoint), feriados municipais e móveis, resumo por IA sem a chave.
- **Como evitam repetir chamadas externas?** A agenda do dia fica salva no banco e os votos têm a marca `votos_carregados`.
- **O que é uma condição de corrida?** Duas requisições criando o mesmo dia; a restrição única do banco gera `IntegrityError`, que é tratado devolvendo a agenda da outra requisição (há teste para isso).
