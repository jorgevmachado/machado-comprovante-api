# Comprovante — Requisitos tecnológicos

## 1. Objetivo

Definir as tecnologias utilizadas no projeto Comprovante, priorizando:

* simplicidade;
* baixo custo;
* preferência por serviços gratuitos;
* facilidade de desenvolvimento e manutenção;
* possibilidade de evolução futura;
* aprendizado técnico;
* baixo acoplamento a fornecedores.

O projeto deverá priorizar processamento determinístico e local sempre que possível, utilizando serviços externos somente quando agregarem valor.

---

# 2. Princípios tecnológicos

## 2.1. Gratuito como prioridade

Sempre que houver uma alternativa tecnicamente adequada e gratuita, ela deverá ser priorizada.

Serviços pagos poderão ser utilizados futuramente caso:

* o projeto ultrapasse os limites gratuitos;
* a qualidade do resultado seja insuficiente;
* exista uma necessidade técnica que não possa ser atendida pela solução gratuita.

A arquitetura não deverá depender inicialmente de serviços pagos.

---

## 2.2. Processamento determinístico como primeira opção

O sistema deverá tentar extrair e interpretar as informações do comprovante sem utilizar Inteligência Artificial.

O fluxo principal será baseado em:

* extração de texto de PDF;
* OCR quando necessário;
* identificação de padrões;
* regras de parsing;
* identificadores de instituições;
* parsers específicos por instituição quando necessário.

A IA será utilizada apenas como mecanismo de fallback.

---

## 2.3. IA como fallback

Quando o processamento determinístico não conseguir produzir informações suficientes ou confiáveis, o sistema poderá encaminhar o conteúdo extraído para um modelo de IA gratuito.

A IA não será responsável pela confirmação do pagamento.

Sua responsabilidade será exclusivamente auxiliar na transformação do conteúdo do comprovante em dados estruturados.

Fluxo:

```text
Comprovante
    ↓
Extração de texto
    ↓
Parser determinístico
    ↓
Resultado suficiente?
    ├── SIM → revisão do usuário
    │
    └── NÃO
          ↓
       IA fallback
          ↓
      revisão do usuário
```

Mesmo quando a IA for utilizada, o usuário deverá revisar os dados antes da confirmação.

---

# 3. Frontend

## 3.1. Next.js

O frontend será desenvolvido utilizando Next.js.

Responsabilidades:

* interface web;
* autenticação no lado da aplicação;
* upload de comprovantes;
* apresentação do processamento;
* formulário de revisão;
* histórico de pagamentos;
* filtros e consultas;
* experiência responsiva.

---

## 3.2. React

React será utilizado como biblioteca principal de construção da interface.

---

## 3.3. TypeScript

TypeScript será utilizado no frontend para:

* tipagem;
* contratos entre componentes;
* redução de erros;
* manutenção do código;
* melhor suporte ao desenvolvimento.

---

## 3.4. Tailwind CSS

Tailwind CSS será utilizado para estilização da aplicação.

---

## 3.5. PWA

A aplicação deverá ser preparada como Progressive Web App.

O objetivo é permitir uma experiência adequada em smartphones sem necessidade de desenvolver inicialmente um aplicativo nativo.

A aplicação deverá oferecer como alternativas:

* seleção tradicional de arquivo;
* seleção de imagem;
* compartilhamento pelo sistema operacional quando suportado.

O compartilhamento pelo sistema operacional não deverá ser considerado o único mecanismo de envio, pois o suporte a Web Share Target varia entre navegadores e plataformas.

---

# 4. Backend

## 4.1. Python

Python será utilizado no backend.

A escolha também tem como objetivo permitir evolução técnica e aprofundamento do conhecimento em Python.

---

## 4.2. FastAPI

FastAPI será utilizado como framework HTTP do backend.

Responsabilidades:

* API REST;
* autenticação;
* recebimento de arquivos;
* processamento das requisições;
* regras de negócio;
* consultas;
* persistência;
* comunicação com serviços externos.

A aplicação deverá manter separadas as responsabilidades de API, domínio e processamento de documentos.

---

# 5. ORM

## 5.1. SQLAlchemy

SQLAlchemy será utilizado como ORM e camada de acesso ao banco de dados.

Responsabilidades:

* mapeamento dos modelos;
* consultas;
* relacionamentos;
* transações;
* persistência;
* integração com PostgreSQL.

---

## 5.2. Alembic

Alembic será utilizado para controle das migrações do banco de dados.

---

# 6. Validação e contratos

## 6.1. Pydantic

Pydantic será utilizado para:

* validação de dados;
* contratos da API;
* serialização;
* validação dos dados extraídos;
* validação dos dados enviados pelo frontend.

Os dados produzidos pelos parsers também deverão passar por modelos estruturados antes de serem utilizados pelo domínio.

---

# 7. Banco de dados

## 7.1. PostgreSQL

PostgreSQL será utilizado como banco de dados principal.

Responsabilidades:

* usuários;
* comprovantes;
* pagamentos;
* beneficiários;
* instituições;
* estados de processamento;
* consultas;
* relacionamentos;
* dados estruturados.

O PostgreSQL será utilizado para dados estruturados.

Os arquivos originais dos comprovantes não deverão ser armazenados diretamente no banco.

---

## 7.2. Serviço gratuito

Para o ambiente inicial poderá ser utilizado um serviço PostgreSQL com plano gratuito, como Neon, desde que permaneça dentro das cotas disponíveis.

A escolha definitiva do provedor de hospedagem poderá ser feita durante a implementação.

---

# 8. Armazenamento de arquivos

## 8.1. Cloudflare R2

O armazenamento dos arquivos originais deverá utilizar preferencialmente um serviço com camada gratuita.

A opção inicial considerada é Cloudflare R2.

Responsabilidades:

* armazenamento do PDF original;
* armazenamento das imagens originais;
* recuperação do arquivo;
* exclusão do arquivo;
* preservação do comprovante original.

O banco armazenará apenas a referência ao arquivo.

---

## 8.2. Abstração de storage

O domínio da aplicação não deverá depender diretamente do Cloudflare R2.

Deverá existir uma abstração semelhante a:

```text
ReceiptStorage
    │
    └── R2ReceiptStorage
```

Isso permitirá trocar o provedor futuramente sem alterar as regras de negócio.

---

# 9. Processamento de documentos

O processamento deverá aceitar inicialmente:

* PDF;
* imagens.

O processamento deverá seguir uma estratégia de menor complexidade e menor custo.

---

# 10. Extração de texto de PDF

## 10.1. pdfplumber

O primeiro mecanismo para PDFs será `pdfplumber`.

Objetivo:

* extrair texto diretamente do PDF;
* evitar OCR quando o documento já possuir texto;
* reduzir custo;
* aumentar velocidade;
* preservar maior fidelidade das informações.

Fluxo:

```text
PDF
 ↓
pdfplumber
 ↓
Texto encontrado?
 ├── SIM → continuar processamento
 └── NÃO → OCR
```

---

# 11. OCR

## 11.1. Tesseract

Tesseract será utilizado inicialmente como mecanismo gratuito de OCR.

Será utilizado quando:

* o PDF não possuir texto extraível;
* o PDF for essencialmente uma imagem;
* o arquivo recebido for uma imagem;
* a extração direta apresentar resultado insuficiente.

Fluxo:

```text
PDF / Imagem
      ↓
Existe texto utilizável?
      ├── SIM → parser
      │
      └── NÃO → Tesseract
                    ↓
                  texto
```

O OCR externo pago não será necessário no MVP.

---

# 12. Interpretação dos comprovantes

## 12.1. Parser determinístico

O sistema deverá tentar interpretar o texto utilizando regras determinísticas antes de utilizar IA.

O parser deverá buscar informações como:

* data;
* valor;
* beneficiário;
* instituição de origem;
* instituição de destino.

Exemplo:

```text
VALOR: R$ 387,42
```

Resultado:

```text
amount = 387.42
```

Exemplo:

```text
DATA: 12/09/2026
```

Resultado:

```text
date = 2026-09-12
```

---

# 13. Identificação de instituições

A identificação das instituições deverá utilizar normalização.

Exemplos:

```text
ITAÚ UNIBANCO S.A.
ITAU UNIBANCO
BANCO ITAÚ
ITAÚ
```

poderão representar:

```text
Itaú
```

Da mesma forma:

```text
NU PAGAMENTOS S.A.
NUBANK
```

poderão representar:

```text
Nubank
```

A aplicação deverá separar:

* texto original encontrado no comprovante;
* instituição normalizada utilizada pelo sistema.

---

# 14. Parsers específicos

Quando uma instituição possuir um formato conhecido, poderá existir um parser específico.

Exemplo:

```text
ReceiptParser
    │
    ├── ItauReceiptParser
    ├── NubankReceiptParser
    └── GenericReceiptParser
```

O parser específico deverá ser utilizado quando a instituição puder ser identificada com segurança.

Caso contrário, poderá ser utilizado um parser genérico.

---

# 15. IA como fallback

## 15.1. Gemini API

Uma API de IA com camada gratuita poderá ser utilizada como fallback.

A opção inicialmente considerada é Gemini.

A IA não fará parte do caminho principal de processamento.

Ela somente será acionada quando o parser determinístico não produzir um resultado suficiente.

---

## 15.2. Responsabilidade da IA

A IA receberá o texto extraído e deverá produzir dados estruturados.

Exemplo:

```json
{
  "date": "2026-09-12",
  "amount": 387.42,
  "beneficiary": "Neoenergia",
  "source_institution": "Itaú",
  "destination_institution": null
}
```

A resposta deverá ser validada pelo backend antes de ser apresentada ao usuário.

---

## 15.3. IA não confirma pagamentos

A IA jamais deverá registrar automaticamente um pagamento.

Mesmo que a IA produza um resultado considerado válido:

```text
IA
 ↓
Dados extraídos
 ↓
Usuário revisa
 ↓
Usuário confirma
 ↓
Pagamento registrado
```

A confirmação continuará sendo responsabilidade exclusiva do usuário.

---

## 15.4. Critérios para acionamento da IA

A IA deverá ser utilizada somente quando o processamento determinístico não produzir um resultado suficiente para apresentação ao usuário.

Os campos obrigatórios para considerar o resultado determinístico suficiente são:

* data;
* valor;
* beneficiário;
* instituição de origem.

A instituição de destino poderá permanecer ausente quando não puder ser identificada no comprovante.

A IA deverá ser acionada quando ocorrer pelo menos uma das condições abaixo:

### Campo obrigatório ausente

Qualquer campo obrigatório não for identificado.

```text
date = NOT_FOUND
amount = FOUND
beneficiary = FOUND
sourceInstitution = FOUND
```

Resultado:

```text
→ IA
```

### Campo obrigatório ambíguo

O parser encontrar mais de uma possibilidade e não conseguir determinar qual é a correta.

Exemplo:

```text
Valor: R$ 100,00
Valor pago: R$ 98,50
```

Se não for possível determinar qual representa o valor do pagamento:

```text
→ IA
```

### Instituição de origem não identificada

Se a instituição responsável pela origem do pagamento não puder ser identificada:

```text
sourceInstitution = NOT_FOUND
```

Resultado:

```text
→ IA
```

### Parser específico falhar

Se a instituição for identificada, mas o parser específico não conseguir produzir os campos obrigatórios:

```text
Itaú
  ↓
ItauReceiptParser
  ↓
resultado insuficiente
```

Resultado:

```text
→ IA
```

### Informações inconsistentes

Quando o parser encontrar informações conflitantes.

Exemplo:

```text
Data extraída: 12/09/2026
Outra data relevante encontrada: 12/08/2026
```

ou:

```text
Valor identificado: R$ 3,87
Valor indicado em outro trecho: R$ 387,42
```

Se as regras determinísticas não conseguirem resolver a inconsistência:

```text
→ IA
```

---

## 15.5. Situações que não devem acionar a IA

A IA não deverá ser utilizada apenas porque o documento pode ser interpretado de maneira mais sofisticada.

Também não deverá ser utilizada quando o problema estiver na qualidade do arquivo.

Por exemplo:

```text
Tesseract
   ↓
texto ilegível/incompleto
```

Nesse caso, o problema é de OCR ou qualidade do documento, e não de interpretação.

A IA não deverá ser utilizada para tentar recuperar informações que não foram corretamente extraídas.

---

## 15.6. Resultado objetivo

O processamento deverá produzir um resultado estruturado com o estado de cada campo:

```text
FOUND
NOT_FOUND
AMBIGUOUS
```

Exemplo:

```text
date                FOUND
amount              FOUND
beneficiary         FOUND
sourceInstitution   FOUND
destinationInstitution NOT_FOUND
```

Nesse caso, como todos os campos obrigatórios foram encontrados:

```text
→ não utiliza IA
→ apresenta para revisão
```

Outro exemplo:

```text
date                FOUND
amount              FOUND
beneficiary         AMBIGUOUS
sourceInstitution   FOUND
destinationInstitution NOT_FOUND
```

Como existe um campo obrigatório ambíguo:

```text
→ utiliza IA
```

A decisão de utilização da IA deverá ser determinística e testável.

---

# 16. Estratégia de processamento

O processamento completo será:

```text
                    Comprovante
                         │
                         ▼
                    Validação
                         │
                         ▼
                Extração de texto
                         │
                  ┌──────┴──────┐
                  │             │
                  ▼             ▼
             Texto PDF       Tesseract
                  │             │
                  └──────┬──────┘
                         ▼
                Parser determinístico
                         │
                         ▼
                  Resultado estruturado
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
          Resultado válido    Insuficiente
                │                 │
                │                 ▼
                │             IA fallback
                │                 │
                │                 ▼
                │          Resultado estruturado
                │                 │
                └────────┬────────┘
                         ▼
                 Validação backend
                         │
                         ▼
                  Revisão do usuário
                         │
                    ┌────┴────┐
                    │         │
                 Corrigir   Confirmar
                    │         │
                    └────┬────┘
                         ▼
                    Persistência
```

---

# 17. Testes

## 17.1. Frontend

Serão utilizados:

* Jest;
* Testing Library.

## 17.2. Backend

Será utilizado:

* pytest.

Deverão existir testes principalmente para:

* parsers;
* normalização de instituições;
* extração de valores;
* extração de datas;
* identificação de beneficiários;
* identificação de instituições;
* tratamento de documentos inválidos;
* fluxo de processamento;
* critérios de acionamento da IA;
* fallback para IA;
* validação dos dados retornados pela IA;
* regras de confirmação;
* persistência.

Os critérios de acionamento da IA deverão possuir testes determinísticos que garantam que a IA não seja chamada quando o resultado já for suficiente.

---

# 18. Containerização

Docker será utilizado para padronizar o ambiente de desenvolvimento e facilitar implantação.

---

# 19. CI/CD

GitHub Actions será utilizado inicialmente para:

* instalação das dependências;
* lint;
* testes;
* validações;
* build;
* verificações antes de publicação.

---

# 20. API

A API será documentada utilizando OpenAPI, disponibilizada automaticamente pelo FastAPI.

---

# 21. Observabilidade

Inicialmente deverá existir pelo menos:

* logs estruturados;
* identificação de falhas de processamento;
* registro do estado do processamento;
* tratamento de erros.

Ferramentas externas de observabilidade poderão ser adicionadas posteriormente.

---

# 22. Arquitetura tecnológica consolidada

A stack inicial fica:

```text
Frontend
├── Next.js
├── React
├── TypeScript
├── Tailwind CSS
└── PWA

Backend
├── Python
├── FastAPI
├── Pydantic
├── SQLAlchemy
└── Alembic

Database
└── PostgreSQL

Database hosting
└── Preferência por Free Tier

Storage
└── Cloudflare R2 / Free Tier

Document processing
├── pdfplumber
└── Tesseract OCR

Document interpretation
├── Parser determinístico
├── Parsers específicos por instituição
└── Gemini como fallback

Testing
├── Jest
├── Testing Library
└── pytest

Infrastructure
├── Docker
└── GitHub Actions

API
└── OpenAPI
```

---

# 23. Decisões ainda não definidas

Ainda não foram definidos:

* provedor definitivo de hospedagem do frontend;
* provedor definitivo de hospedagem do FastAPI;
* configuração definitiva do PostgreSQL;
* limites máximos dos arquivos;
* formatos de imagem aceitos;
* estratégia definitiva de autenticação;
* política de retenção dos comprovantes;
* implementação detalhada dos parsers;
* estrutura definitiva das tabelas;
* mecanismo de processamento assíncrono;
* configuração específica do Gemini fallback;
* estratégia de segurança para arquivos enviados.

Essas decisões serão tomadas nas próximas etapas do projeto.

---

# 24. Princípio fundamental

O Comprovante deverá seguir a seguinte regra:

> **Não utilizar uma tecnologia complexa quando uma solução simples for suficiente.**

O processamento deverá seguir esta ordem de preferência:

```text
1. Texto existente no PDF
2. Regras determinísticas
3. OCR gratuito
4. IA gratuita como fallback
5. Serviços pagos somente se necessários
```

O usuário deverá permanecer como autoridade final sobre os dados antes do registro do pagamento.
