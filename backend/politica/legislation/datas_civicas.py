"""Contexto de feriados e datas cívicas escrito à mão.

Serve para explicar as datas sem depender da IA: os feriados nacionais da BrasilAPI ganham texto pelo nome,
e datas cívicas e feriados estaduais de data fixa aparecem pelo dia e mês. Quando a IA está configurada,
ela só entra para datas que não estão aqui.
"""

import unicodedata
from datetime import date


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower().strip()


def contexto(historico, importancia, impacto):
    return {"contexto_historico": historico, "importancia": importancia, "impacto_legislativo": impacto}


LEI_FERIADOS = "Lei 662/1949, atualizada pela Lei 10.607/2002"

FERIADOS_NACIONAIS = {
    "confraternizacao mundial": contexto(
        "O 1º de janeiro marca o início do ano no calendário gregoriano e é celebrado como o Dia da "
        "Confraternização Universal, data de renovação e de paz entre os povos.",
        "Abre o ano civil e o ano fiscal. O calendário legislativo só retoma em 2 de fevereiro, quando começa a "
        "sessão legislativa.",
        f"É feriado nacional ({LEI_FERIADOS}). De 23 de dezembro a 1º de fevereiro o Congresso está em recesso e "
        "não faz votações ordinárias.",
    ),
    "carnaval": contexto(
        "Festa popular que antecede a Quaresma, de origem europeia e incorporada à cultura brasileira desde o "
        "período colonial. Hoje reúne desfiles de escolas de samba, blocos de rua e bailes.",
        "É uma das maiores manifestações culturais do país e movimenta o turismo e a economia criativa.",
        "Não é feriado nacional por lei federal: segunda e terça de Carnaval são ponto facultativo e viram feriado "
        "por leis estaduais e municipais. A semana costuma esvaziar as votações no Congresso.",
    ),
    "sexta-feira santa": contexto(
        "Dia em que os cristãos lembram a crucificação e a morte de Jesus Cristo, na Semana Santa que antecede a "
        "Páscoa.",
        "Tem grande importância religiosa para católicos e protestantes e é tradicionalmente dia de jejum e reflexão.",
        "A Sexta-feira da Paixão é reconhecida em lei (Lei 9.093/1995, sobre feriados religiosos) e é feriado na "
        "prática em todo o país. O Brasil é um Estado laico (Constituição, art. 19).",
    ),
    "pascoa": contexto(
        "Celebra a ressurreição de Jesus Cristo, a principal festa do calendário cristão. Cai em um domingo que "
        "muda a cada ano e, no Brasil, é marcada pelo costume de trocar ovos de chocolate.",
        "Encerra a Semana Santa e serve de referência para outras datas móveis, como o Carnaval e Corpus Christi.",
        "Por cair sempre no domingo, não cria um dia extra de descanso. A liberdade de crença é garantida pela "
        "Constituição (art. 5º, VI).",
    ),
    "tiradentes": contexto(
        "Homenageia Joaquim José da Silva Xavier, o Tiradentes, líder da Inconfidência Mineira (1789), movimento "
        "contra a dominação portuguesa e a cobrança de impostos. Foi enforcado em 21 de abril de 1792.",
        "É símbolo da luta por liberdade e autonomia e foi transformado em herói nacional com a Proclamação da "
        "República.",
        f"É feriado nacional ({LEI_FERIADOS}). Tiradentes também é o Patrono Cívico da Nação brasileira "
        "(Lei 4.897/1965).",
    ),
    "dia do trabalho": contexto(
        "Lembra as lutas dos trabalhadores por jornadas menores e melhores condições, em especial a greve de "
        "Chicago, em 1886. No Brasil, a data se consolidou como feriado no século XX.",
        "É uma ocasião para debater direitos trabalhistas, salário e emprego.",
        "Os direitos dos trabalhadores estão na Constituição (art. 7º) e na CLT, assinada em 1º de maio de 1943. "
        "A reforma trabalhista (Lei 13.467/2017) e o salário mínimo são temas recorrentes no Congresso.",
    ),
    "corpus christi": contexto(
        "Festa católica que celebra a presença de Cristo na Eucaristia, realizada 60 dias depois da Páscoa. "
        "Tradicionalmente tem procissões e tapetes de serragem colorida.",
        "É uma das principais festas religiosas populares do país.",
        "Não é feriado nacional por lei federal: é ponto facultativo no serviço público federal e feriado onde leis "
        "estaduais ou municipais assim definem.",
    ),
    "independencia do brasil": contexto(
        "Lembra o Grito do Ipiranga, quando Dom Pedro I proclamou a independência do Brasil de Portugal, em 7 de "
        "setembro de 1822, às margens do riacho Ipiranga, em São Paulo.",
        "É a principal data cívica do país e costuma ser celebrada com desfiles militares e civis.",
        f"É feriado nacional ({LEI_FERIADOS}). A soberania é um dos fundamentos da República na Constituição "
        "(art. 1º, I).",
    ),
    "nossa senhora aparecida": contexto(
        "Celebra a padroeira do Brasil, cuja imagem foi encontrada por pescadores no rio Paraíba do Sul, em 1717. "
        "O santuário de Aparecida (SP) recebe milhões de fiéis.",
        "É uma das maiores romarias do mundo católico. A data também é o Dia das Crianças.",
        "É feriado nacional pela Lei 6.802/1980, que declarou o dia de Nossa Senhora Aparecida, padroeira do Brasil.",
    ),
    "finados": contexto(
        "Dia em que os cristãos, em especial os católicos, rezam e homenageiam os mortos. No Brasil é comum visitar "
        "cemitérios e levar flores.",
        "Reforça a tradição de memória das famílias e da comunidade.",
        f"É feriado nacional ({LEI_FERIADOS}). Os serviços de cemitério e funerários são organizados por leis "
        "municipais.",
    ),
    "proclamacao da republica": contexto(
        "Em 15 de novembro de 1889, militares liderados pelo marechal Deodoro da Fonseca derrubaram a monarquia e "
        "proclamaram a República, encerrando o Império de Dom Pedro II.",
        "Marca o início do regime republicano e federativo que o Brasil vive até hoje.",
        f"É feriado nacional ({LEI_FERIADOS}). Em 1993, um plebiscito confirmou a República como forma de governo.",
    ),
    "dia da consciencia negra": contexto(
        "Homenageia Zumbi dos Palmares, líder do Quilombo dos Palmares, morto em 20 de novembro de 1695. A data "
        "lembra a resistência negra à escravidão e a contribuição afro-brasileira à formação do país.",
        "Convida a refletir sobre racismo, desigualdade e reparação histórica.",
        "Virou feriado nacional pela Lei 14.759/2023; antes já era feriado em vários estados e municípios. Temas "
        "relacionados são o Estatuto da Igualdade Racial (Lei 12.288/2010) e as cotas raciais (Lei 12.711/2012).",
    ),
    "natal": contexto(
        "Celebra o nascimento de Jesus Cristo. No Brasil, mistura tradições religiosas, a ceia em família e a troca "
        "de presentes.",
        "É uma das datas mais importantes do calendário cristão e do comércio.",
        f"É feriado nacional ({LEI_FERIADOS}). No fim de dezembro o Congresso costuma votar o orçamento da União "
        "do ano seguinte antes de entrar em recesso.",
    ),
}

# (mês, dia) -> data cívica que não é feriado nacional
DATAS_CIVICAS = {
    (2, 24): {
        "nome": "Conquista do Voto Feminino",
        **contexto(
            "Em 24 de fevereiro de 1932, o Código Eleitoral, decretado por Getúlio Vargas, garantiu às mulheres o "
            "direito de votar e de ser votadas no Brasil.",
            "Foi um passo decisivo na ampliação da cidadania política no país.",
            "A Lei das Eleições (Lei 9.504/1997) exige que cada partido reserve ao menos 30% das candidaturas "
            "para cada sexo.",
        ),
    },
    (3, 8): {
        "nome": "Dia Internacional da Mulher",
        **contexto(
            "Data lembrada no mundo todo em memória das lutas das mulheres por direitos, adotada pela ONU nos anos "
            "1970.",
            "Chama a atenção para igualdade de gênero, violência e participação das mulheres na política e no "
            "trabalho.",
            "A Lei Maria da Penha (Lei 11.340/2006) e a Lei do Feminicídio (Lei 13.104/2015) estão entre as "
            "principais leis brasileiras de proteção às mulheres.",
        ),
    },
    (4, 19): {
        "nome": "Dia dos Povos Indígenas",
        **contexto(
            "Antes chamado Dia do Índio, a data remete ao Primeiro Congresso Indigenista Interamericano, de 1940, "
            "no México. O nome atual foi definido pela Lei 14.402/2022.",
            "Lembra a diversidade e os direitos dos povos originários.",
            "A Constituição de 1988 reconhece a organização, os costumes e os direitos originários dos indígenas "
            "sobre as terras que ocupam (art. 231). A demarcação de terras é tema frequente no Congresso.",
        ),
    },
    (4, 22): {
        "nome": "Descobrimento do Brasil",
        **contexto(
            "Em 22 de abril de 1500, a esquadra de Pedro Álvares Cabral chegou ao litoral da atual Bahia, dando "
            "início à presença portuguesa no território.",
            "É o marco inicial da colonização portuguesa; hoje a data também provoca debates sobre os povos que já "
            "viviam aqui.",
            "Não há lei que institua feriado nesta data; ela é lembrada em escolas e eventos cívicos.",
        ),
    },
    (5, 13): {
        "nome": "Abolição da Escravatura",
        **contexto(
            "Em 13 de maio de 1888, a Princesa Isabel assinou a Lei Áurea (Lei 3.353), que extinguiu a escravidão "
            "no Brasil, o último país independente das Américas a fazê-lo.",
            "Pôs fim a mais de três séculos de escravidão, mas sem políticas de inclusão para os libertos, o que "
            "deixou desigualdades que persistem.",
            "A Constituição de 1988 define o racismo como crime inafiançável e imprescritível (art. 5º, XLII).",
        ),
    },
    (8, 11): {
        "nome": "Dia do Advogado e do Estudante",
        **contexto(
            "Em 11 de agosto de 1827, Dom Pedro I criou os primeiros cursos jurídicos do Brasil, em São Paulo e em "
            "Olinda.",
            "Por isso a data homenageia advogados e estudantes.",
            "A advocacia é função essencial à Justiça segundo a Constituição (art. 133) e é regulada pelo "
            "Estatuto da Advocacia (Lei 8.906/1994).",
        ),
    },
    (9, 21): {
        "nome": "Dia Nacional de Luta da Pessoa com Deficiência",
        **contexto(
            "Data criada por lei federal (Lei 11.133/2005) para chamar a atenção para a inclusão e os direitos das "
            "pessoas com deficiência.",
            "Lembra que acessibilidade e oportunidades iguais ainda são desafios.",
            "A Lei Brasileira de Inclusão (Lei 13.146/2015) reúne direitos como acessibilidade, educação "
            "inclusiva e trabalho.",
        ),
    },
    (10, 5): {
        "nome": "Promulgação da Constituição de 1988",
        **contexto(
            "Em 5 de outubro de 1988, a Assembleia Nacional Constituinte, presidida por Ulysses Guimarães, "
            "promulgou a Constituição, chamada de Constituição Cidadã, que encerrou o regime militar.",
            "É a lei máxima do país: define direitos, poderes e deveres.",
            "A Constituição já recebeu mais de uma centena de emendas, aprovadas pelo Congresso por meio de PECs.",
        ),
    },
    (10, 15): {
        "nome": "Dia do Professor",
        **contexto(
            "Lembra o decreto de 15 de outubro de 1827, em que Dom Pedro I criou as escolas de primeiras letras. A "
            "data foi oficializada como Dia do Professor em 1963.",
            "Homenageia quem ensina e chama a atenção para as condições da educação.",
            "O piso salarial do magistério (Lei 11.738/2008) e o Plano Nacional de Educação (Lei 13.005/2014) "
            "são temas centrais no Congresso.",
        ),
    },
    (11, 19): {
        "nome": "Dia da Bandeira",
        **contexto(
            "Celebra a Bandeira Nacional, adotada em 19 de novembro de 1889, quatro dias depois da Proclamação da "
            "República.",
            "A bandeira é um dos símbolos que representam o país e a sua unidade.",
            "Os símbolos nacionais são regulados pela Lei 5.700/1971 e citados na Constituição (art. 13).",
        ),
    },
    (12, 10): {
        "nome": "Dia dos Direitos Humanos",
        **contexto(
            "Em 10 de dezembro de 1948, a ONU adotou a Declaração Universal dos Direitos Humanos, que reconhece "
            "direitos básicos de todas as pessoas.",
            "Serve de referência para leis e políticas públicas em quase todo o mundo.",
            "A dignidade da pessoa humana é fundamento da República brasileira (Constituição, art. 1º, III).",
        ),
    },
}


def estadual(nome, historico, importancia, uf):
    return {
        "nome": nome,
        **contexto(
            historico,
            importancia,
            f"É feriado estadual de {uf}, definido por lei do próprio estado, e não vale para os demais.",
        ),
    }


# UF -> {(mês, dia): feriado estadual de data fixa}. Lista curada. Não aparecem ES (Nossa Senhora da Penha é
# móvel), MG, GO e MT (sem feriado estadual de data fixa próprio; os feriados de Goiás são municipais).
FERIADOS_ESTADUAIS = {
    "AC": {
        (6, 15): estadual(
            "Aniversário do Acre",
            "Em 15 de junho de 1962, o Acre deixou de ser território federal e passou a ser estado.",
            "É a data de aniversário do estado.",
            "AC",
        )
    },
    "AL": {
        (9, 16): estadual(
            "Emancipação Política de Alagoas",
            "Em 16 de setembro de 1817, Alagoas deixou de fazer parte da capitania de Pernambuco.",
            "Marca a autonomia política de Alagoas.",
            "AL",
        )
    },
    "AM": {
        (9, 5): estadual(
            "Elevação do Amazonas à Categoria de Província",
            "Em 5 de setembro de 1850, o Amazonas foi separado do Pará e se tornou província.",
            "Marca o nascimento político do Amazonas como unidade própria.",
            "AM",
        )
    },
    "AP": {
        (9, 13): estadual(
            "Criação do Território Federal do Amapá",
            "Em 13 de setembro de 1943, o governo federal criou o Território Federal do Amapá. O Amapá virou "
            "estado em 1988.",
            "É a principal data cívica do Amapá.",
            "AP",
        )
    },
    "BA": {
        (7, 2): estadual(
            "Independência da Bahia",
            "Em 2 de julho de 1823, tropas brasileiras expulsaram as forças portuguesas de Salvador, consolidando "
            "a independência do Brasil na Bahia.",
            "Para os baianos, é a verdadeira data da independência, celebrada com um grande desfile popular.",
            "BA",
        )
    },
    "CE": {
        (3, 25): estadual(
            "Data Magna do Ceará",
            "Em 25 de março de 1884, o Ceará aboliu a escravidão em seu território, quatro anos antes da Lei Áurea.",
            "Orgulho do estado por ter sido pioneiro na abolição.",
            "CE",
        )
    },
    "DF": {
        (11, 30): estadual(
            "Dia do Evangélico",
            "Data dedicada à comunidade evangélica do Distrito Federal, instituída por lei distrital.",
            "Reconhece a presença e a contribuição da população evangélica na capital.",
            "DF",
        )
    },
    "MA": {
        (7, 28): estadual(
            "Adesão do Maranhão à Independência",
            "Em 28 de julho de 1823, o Maranhão aderiu à independência do Brasil, quase um ano depois do Grito "
            "do Ipiranga.",
            "É a data cívica máxima do Maranhão.",
            "MA",
        )
    },
    "MS": {
        (10, 11): estadual(
            "Criação do Estado de Mato Grosso do Sul",
            "Em 11 de outubro de 1977, uma lei complementar dividiu Mato Grosso e criou Mato Grosso do Sul.",
            "É o aniversário do estado.",
            "MS",
        )
    },
    "PA": {
        (8, 15): estadual(
            "Adesão do Grão-Pará à Independência",
            "Em 15 de agosto de 1823, o Grão-Pará aderiu à independência do Brasil, depois da resistência de "
            "tropas portuguesas.",
            "É a principal data cívica do Pará.",
            "PA",
        )
    },
    "PB": {
        (8, 5): estadual(
            "Fundação do Estado da Paraíba",
            "Em 5 de agosto de 1585 foi fundada a cidade de Nossa Senhora das Neves, hoje João Pessoa, origem da "
            "Paraíba.",
            "É o aniversário da capital e do estado.",
            "PB",
        )
    },
    "PE": {
        (3, 6): estadual(
            "Data Magna de Pernambuco",
            "Lembra a Revolução Pernambucana de 1817, movimento republicano que formou um governo provisório "
            "contra a Coroa portuguesa.",
            "É considerada a data máxima de Pernambuco e símbolo de sua tradição de luta por liberdade.",
            "PE",
        )
    },
    "PI": {
        (10, 19): estadual(
            "Dia do Piauí",
            "Lembra a adesão de Parnaíba à independência do Brasil, em 19 de outubro de 1822.",
            "É a principal data cívica do Piauí.",
            "PI",
        )
    },
    "PR": {
        (12, 19): estadual(
            "Emancipação Política do Paraná",
            "Em 19 de dezembro de 1853, o Paraná se separou da província de São Paulo.",
            "Marca a autonomia política do Paraná.",
            "PR",
        )
    },
    "RJ": {
        (4, 23): estadual(
            "Dia de São Jorge",
            "Dia dedicado a São Jorge, santo guerreiro de grande devoção popular no Rio de Janeiro, associado "
            "também a Ogum nas religiões de matriz africana.",
            "Mistura tradições católicas e afro-brasileiras e reúne festas e procissões.",
            "RJ",
        )
    },
    "RN": {
        (10, 3): estadual(
            "Mártires de Cunhaú e Uruaçu",
            "Lembra os colonos católicos mortos em 1645, durante a ocupação holandesa, em Cunhaú e Uruaçu. Os "
            "mártires foram canonizados pelo Papa Francisco em 2017.",
            "É uma data religiosa e histórica do Rio Grande do Norte.",
            "RN",
        )
    },
    "RO": {
        (1, 4): estadual(
            "Criação do Estado de Rondônia",
            "O estado de Rondônia foi instalado em 4 de janeiro de 1982, deixando de ser território federal.",
            "É o aniversário do estado.",
            "RO",
        )
    },
    "RR": {
        (10, 5): estadual(
            "Criação do Estado de Roraima",
            "Em 5 de outubro de 1988, a nova Constituição transformou o Território Federal de Roraima em estado.",
            "É o aniversário do estado.",
            "RR",
        )
    },
    "RS": {
        (9, 20): estadual(
            "Revolução Farroupilha (Dia do Gaúcho)",
            "Revolta iniciada em 1835 contra o governo imperial, por impostos e disputas políticas. Durou até "
            "1845 e deu origem à República Rio-Grandense.",
            "É a maior data do Rio Grande do Sul, celebrada com desfiles e tradições gaúchas.",
            "RS",
        )
    },
    "SC": {
        (8, 11): estadual(
            "Dia do Estado de Santa Catarina",
            "Em 11 de agosto de 1738, foi criada a capitania de Santa Catarina, separada da de São Paulo. A data é "
            "a Data Magna do estado.",
            "Celebra a identidade catarinense. Pela Lei estadual 17.335/2017, o feriado é transferido para o "
            "domingo seguinte.",
            "SC",
        )
    },
    "SE": {
        (7, 8): estadual(
            "Emancipação Política de Sergipe",
            "Em 8 de julho de 1820, Dom João VI tornou Sergipe independente da Bahia.",
            "Marca a autonomia política de Sergipe.",
            "SE",
        )
    },
    "SP": {
        (7, 9): estadual(
            "Revolução Constitucionalista de 1932",
            "Em 1932, os paulistas se levantaram contra o governo provisório de Getúlio Vargas e exigiram uma "
            "nova Constituição. A revolta foi derrotada, mas uma Constituinte foi convocada em seguida.",
            "É a principal data cívica de São Paulo e lembra a luta por eleições e pela lei.",
            "SP",
        )
    },
    "TO": {
        (10, 5): estadual(
            "Criação do Estado do Tocantins",
            "O Tocantins foi criado pela Constituição de 1988, em 5 de outubro, a partir do norte de Goiás.",
            "É o aniversário do estado, o mais novo do Brasil.",
            "TO",
        )
    },
}

UFS_COM_FERIADO = sorted(FERIADOS_ESTADUAIS)


def contexto_do_feriado(nome):
    return FERIADOS_NACIONAIS.get(normalizar(nome))


def dias_especiais_extras(data: date, uf=None):
    """Datas cívicas do dia e, se houver UF, o feriado estadual. Não são gravadas no banco."""
    extras = []
    civica = DATAS_CIVICAS.get((data.month, data.day))
    if civica:
        extras.append({**civica, "tipo": "civica"})
    estadual_do_dia = FERIADOS_ESTADUAIS.get((uf or "").upper(), {}).get((data.month, data.day))
    if estadual_do_dia:
        extras.append({**estadual_do_dia, "tipo": "estadual", "uf": uf.upper()})
    return [{"id": None, "data": data.isoformat(), **extra} for extra in extras]
