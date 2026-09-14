# 08 — Backend Architecture

## 1. Objetivo

Este documento define a arquitetura do backend da aplicação Comprovante.

O backend será responsável por:

* autenticação e autorização;
* isolamento dos dados por usuário;
* recebimento e processamento de comprovantes;
* extração e interpretação dos dados dos comprovantes;
* confirmação dos pagamentos;
* persistência dos dados;
* consulta dos pagamentos e beneficiários;
* aplicação das regras de negócio;
* validação dos dados recebidos pela API.

A arquitetura deve permanecer simples e compatível com o tamanho e as necessidades do projeto, evitando a introdução de padrões arquiteturais desnecessários.

---

# 2. Stack

O backend será desenvolvido utilizando:

* Python;
* FastAPI;
* Pydantic;
* SQLAlchemy;
* Alembic;
* PostgreSQL.

A API seguirá o padrão REST e disponibilizará documentação OpenAPI através do FastAPI.

---

# 3. Estrutura do backend

A estrutura principal do backend será:

```text
app/
├── core/
│   ├── cache/
│   ├── context/
│   ├── database/
│   ├── exceptions/
│   ├── logging/
│   ├── pagination/
│   ├── repository/
│   ├── security/
│   ├── service/
│   └── settings/
│
├── models/
│   ├── enum.py
│   ├── user.py
│   ├── role.py
│   ├── password.py
│   ├── authentication.py
│   ├── institution.py
│   ├── beneficiary.py
│   ├── receipt.py
│   └── payment.py
│
├── shared/
│
└── domain/
    ├── auth/
    ├── receipt/
    ├── payment/
    ├── beneficiary/
    └── institution/
```

A organização é baseada em responsabilidades.

---

# 4. Core

O diretório `core` contém funcionalidades fundamentais da aplicação.

Essas funcionalidades são reutilizáveis por diferentes domínios e não devem depender de um domínio específico.

## 4.1 Cache

Responsável por mecanismos de cache utilizados pela aplicação.

```text
core/cache/
```

---

## 4.2 Context

Responsável por informações contextuais da execução da requisição.

Exemplos:

* usuário autenticado;
* contexto da requisição;
* informações necessárias para isolamento dos dados.

```text
core/context/
```

---

## 4.3 Database

Responsável pela configuração e infraestrutura de acesso ao banco de dados.

```text
core/database/
```

Inclui, entre outros:

* conexão;
* sessão SQLAlchemy;
* configuração do banco;
* gerenciamento das sessões.

---

## 4.4 Exceptions

Centraliza exceções e mecanismos relacionados ao tratamento de erros.

```text
core/exceptions/
```

---

## 4.5 Logging

Responsável pela configuração e padronização dos logs da aplicação.

```text
core/logging/
```

---

## 4.6 Pagination

Contém estruturas e funcionalidades genéricas de paginação.

```text
core/pagination/
```

---

## 4.7 Repository

Contém funcionalidades genéricas relacionadas ao acesso a dados.

```text
core/repository/
```

Pode conter:

* repository base;
* operações CRUD genéricas;
* funcionalidades comuns de persistência.

Os repositories específicos de cada domínio permanecem dentro do respectivo domínio.

---

## 4.8 Security

Responsável por funcionalidades de segurança compartilhadas pela aplicação.

```text
core/security/
```

Exemplos:

* hash de senha;
* validação de senha;
* geração e validação de tokens;
* recuperação do usuário autenticado;
* mecanismos de autorização.

---

## 4.9 Service

Contém funcionalidades genéricas de serviço.

```text
core/service/
```

Pode fornecer:

* service base;
* relacionamento entre service e repository;
* comportamentos genéricos reutilizáveis.

As regras de negócio específicas permanecem nos services dos respectivos domínios.

---

## 4.10 Settings

Centraliza as configurações da aplicação.

```text
core/settings/
```

Exemplos:

* variáveis de ambiente;
* configuração do banco;
* configurações de autenticação;
* configurações de armazenamento;
* configurações de serviços externos.

---

# 5. Models

O diretório `models` representa o modelo de persistência da aplicação.

```text
models/
```

Os models são responsáveis pela representação das tabelas e relacionamentos do PostgreSQL utilizando SQLAlchemy.

Os models representam a persistência dos dados.

Eles não devem concentrar as regras de negócio dos agregados.

A regra de negócio deve permanecer nos respectivos domínios.

---

# 6. Enums dos Models

Todos os enums utilizados na definição das entidades persistidas devem ser centralizados em:

```text
models/enum.py
```

O objetivo é evitar que diferentes models criem definições próprias para os mesmos estados ou que enums de persistência fiquem espalhados pelos arquivos das entidades.

Qualquer campo que represente um conjunto **fechado e previamente definido de valores** deverá ser avaliado para utilização de um enum.

## 6.1 Enum de Status

O status das entidades que utilizarem esse conceito deverá utilizar o enum definido em `models/enum.py`.

Para o usuário:

```text
ACTIVE
INACTIVE
LOCKED
```

O enum deverá ser utilizado pelo model, e não deverá existir uma nova definição de status dentro de `user.py`.

Conceitualmente:

```python
# models/enum.py

class Status(...):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
```

E o model deverá importar a definição:

```python
from .enum import Status
```

Dessa forma, a entidade utiliza uma definição centralizada.

---

## 6.2 ProcessingStatus

O status de processamento do Receipt também representa um conjunto fechado de estados.

Portanto, deverá ser definido em `models/enum.py`.

Valores:

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
```

Conceitualmente:

```python
class ProcessingStatus(...):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
```

O model `receipt.py` deverá importar esse enum:

```python
from .enum import ProcessingStatus
```

---

## 6.3 Regra para novos enums

Sempre que um novo campo de uma entidade representar um conjunto fechado de valores, deve-se avaliar a criação de um enum em `models/enum.py`.

Exemplos de candidatos:

```text
Status
ProcessingStatus
```

Não devem ser criados enums apenas porque um campo possui alguns valores atualmente.

O enum deve representar uma definição estrutural e fechada da entidade.

Por exemplo, `Role.name` não será tratado como enum neste momento, pois os papéis são dados do sistema e podem possuir gerenciamento próprio.

Da mesma forma, `file_type` não será definido como enum enquanto os tipos de arquivo oficialmente suportados pelo sistema não estiverem estabelecidos.

---

# 7. Models atuais

Os models previstos são:

```text
models/
├── enum.py
├── user.py
├── role.py
├── password.py
├── authentication.py
├── institution.py
├── beneficiary.py
├── receipt.py
└── payment.py
```

### user.py

Representa a entidade `User`.

Campos principais:

* `id`;
* `role_id`;
* `name`;
* `username`;
* `email`;
* `status`;
* `date_of_birth`;
* `created_at`;
* `updated_at`;
* `deleted_at`.

O campo `status` utiliza `Status`, definido em `models/enum.py`.

---

### role.py

Representa a entidade `Role`.

Campos principais:

* `id`;
* `name`;
* `name_code`;
* `description`;
* timestamps.

`Role` não utiliza enum neste momento.

---

### password.py

Representa a entidade `Password`.

Campos principais:

* `id`;
* `user_id`;
* `value`;
* `last_value`;
* timestamps.

Os valores armazenados são hashes de senha.

---

### authentication.py

Representa a entidade `Authentication`.

Campos principais:

* `id`;
* `user_id`;
* `total`;
* `total_success`;
* `total_failures`;
* `failed_attempts`;
* `last_authenticated_at`;
* timestamps.

Não possui enum atualmente.

---

### institution.py

Representa a entidade `Institution`.

Campos principais:

* `id`;
* `name`;
* `name_code`;
* timestamps.

Não possui enum atualmente.

---

### beneficiary.py

Representa a entidade `Beneficiary`.

Campos principais:

* `id`;
* `user_id`;
* `name`;
* timestamps.

Não possui enum atualmente.

---

### receipt.py

Representa a entidade `Receipt`.

Campos principais:

* `id`;
* `user_id`;
* `file_reference`;
* `file_name`;
* `file_type`;
* `file_size`;
* `processing_status`;
* `extracted_data`;
* `received_at`;
* timestamps.

O campo `processing_status` utiliza `ProcessingStatus`, definido em `models/enum.py`.

---

### payment.py

Representa a entidade `Payment`.

Campos principais:

* `id`;
* `user_id`;
* `receipt_id`;
* `beneficiary_id`;
* `source_institution_id`;
* `destination_institution_id`;
* `amount`;
* `payment_date`;
* timestamps.

Não possui enum atualmente.

---

# 8. Shared

O diretório `shared` contém funcionalidades reutilizáveis que não pertencem ao `core` e também não possuem relação direta com um agregado específico.

```text
shared/
```

Exemplos possíveis:

* funções utilitárias;
* normalizações genéricas;
* constantes;
* tipos compartilhados;
* funções auxiliares.

O `shared` não deve se tornar um local para colocar código apenas porque não foi definido onde ele pertence.

A funcionalidade deve ser realmente compartilhável.

---

# 9. Domínios e agregados

A aplicação será organizada em cinco agregados funcionais:

```text
domain/
├── auth/
├── receipt/
├── payment/
├── beneficiary/
└── institution/
```

Os agregados representam limites de responsabilidade e consistência das regras de negócio.

Um agregado não é definido simplesmente pela existência de uma tabela ou pelo fato de duas tabelas possuírem um relacionamento.

Uma chave estrangeira também não significa que duas entidades pertençam ao mesmo agregado.

O principal critério é:

* quem controla o ciclo de vida;
* quais regras precisam ser mantidas em conjunto;
* quais operações pertencem ao mesmo contexto de negócio;
* qual entidade funciona como raiz do agregado.

---

# 10. Agregado Auth

O agregado `Auth` representa a identidade e autenticação do usuário.

```text
domain/auth/
```

Seu Aggregate Root é `User`.

Internamente:

```text
User
├── Role
├── Password
└── Authentication
```

## Responsabilidades

O agregado é responsável por:

* criação do usuário;
* identificação do usuário;
* credenciais;
* autenticação;
* controle de falhas de autenticação;
* bloqueio do usuário;
* papel/permissão básica do usuário;
* recuperação da identidade autenticada.

`Role`, `Password` e `Authentication` não possuem significado independente dentro do sistema e, portanto, permanecem associados ao agregado `User`.

## Endpoints

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

### POST /auth/register

Cria um novo usuário.

### POST /auth/login

Autentica o usuário utilizando username ou email e senha.

A autenticação atualiza os dados de `Authentication`.

### GET /auth/me

Retorna os dados do usuário autenticado.

A identidade é obtida através do token de autenticação.

Não será criado um endpoint de logout no MVP.

---

# 11. Agregado Receipt

O agregado `Receipt` representa o comprovante enviado pelo usuário.

```text
domain/receipt/
```

Seu Aggregate Root é `Receipt`.

O Receipt representa a evidência original de uma operação financeira.

## Responsabilidades

O agregado é responsável por:

* recebimento do arquivo;
* validação do arquivo;
* armazenamento da referência do arquivo original;
* processamento;
* extração dos dados;
* interpretação;
* controle do estado do processamento;
* apresentação dos dados extraídos para revisão;
* confirmação do comprovante.

## Ciclo de processamento

```text
RECEIVED
    ↓
PROCESSING
    ↓
PROCESSED
```

Em caso de erro:

```text
PROCESSING
    ↓
FAILED
```

Os estados são definidos pelo `ProcessingStatus` em:

```text
models/enum.py
```

O Receipt pode existir sem possuir um Payment.

Isso ocorre porque o usuário pode enviar um comprovante que ainda está sendo processado ou que apresentou erro durante o processamento.

## Dados extraídos

O processamento deve buscar:

* data;
* valor;
* beneficiário;
* instituição de origem;
* instituição de destino, quando disponível.

Os dados extraídos não são automaticamente considerados dados financeiros confirmados.

O usuário deve revisar os dados antes da confirmação.

## Endpoints

```http
POST /receipts
GET  /receipts/{receipt_id}
POST /receipts/{receipt_id}/confirm
```

### POST /receipts

Recebe o arquivo do comprovante.

Fluxo inicial:

```text
Upload
  ↓
Validação
  ↓
Receipt
  ↓
Processamento
  ↓
Extração
  ↓
Interpretação
  ↓
Dados para revisão
```

### GET /receipts/{receipt_id}

Retorna os dados do comprovante e o resultado atual do processamento.

### POST /receipts/{receipt_id}/confirm

Confirma os dados revisados pelo usuário.

Essa operação é responsável por transformar os dados extraídos em um Payment persistido.

---

# 12. Relação entre Receipt e Payment

Receipt e Payment são agregados diferentes.

```text
Receipt
   │
   │ confirmação
   ↓
Payment
```

O Receipt representa a **evidência/documento**.

O Payment representa o **fato financeiro confirmado**.

Um Receipt pode existir sem Payment.

Após a confirmação, um Receipt poderá estar associado a no máximo um Payment.

```text
Receipt 1 ───── 0..1 Payment
```

A existência da referência entre as duas entidades não significa que elas pertençam ao mesmo agregado.

O Receipt controla o ciclo de vida do comprovante.

O Payment controla o ciclo de vida do pagamento.

---

# 13. Agregado Payment

O agregado `Payment` representa o pagamento financeiro confirmado.

```text
domain/payment/
```

Seu Aggregate Root é `Payment`.

## Responsabilidades

O agregado é responsável por:

* representar o pagamento confirmado;
* valor;
* data;
* beneficiário;
* instituição de origem;
* instituição de destino;
* consultas dos pagamentos;
* consultas agregadas.

Um Payment não será criado diretamente pelo usuário através de um `POST /payments` no MVP.

O Payment nasce como consequência da confirmação de um Receipt.

```text
POST /receipts/{receipt_id}/confirm
```

Durante essa operação:

```text
Receipt
   ↓
validação
   ↓
Beneficiary
   ↓
Institution
   ↓
Payment
   ↓
persistência
```

## Endpoints

```http
GET /payments
GET /payments/{payment_id}

GET /payments/summary/count
GET /payments/summary/total
GET /payments/summary/max
GET /payments/summary/beneficiary
```

Não fazem parte do MVP:

```http
POST   /payments
PUT    /payments/{payment_id}
DELETE /payments/{payment_id}
```

O objetivo é impedir que um Payment seja criado sem passar pelo fluxo de comprovante e confirmação.

---

# 14. Agregado Beneficiary

O agregado `Beneficiary` representa um beneficiário associado aos pagamentos do usuário.

```text
domain/beneficiary/
```

Seu Aggregate Root é `Beneficiary`.

O beneficiário pertence ao contexto do usuário.

Um mesmo nome de beneficiário pode existir para usuários diferentes sem que exista compartilhamento entre eles.

## Responsabilidades

O agregado é responsável por:

* identificação do beneficiário;
* associação com o usuário;
* criação/reutilização do beneficiário;
* consulta dos beneficiários;
* busca utilizada durante a confirmação de pagamentos.

Durante a confirmação de um Receipt:

```text
dados extraídos
      ↓
identificação do beneficiário
      ↓
procura Beneficiary do usuário
      ↓
existe?
 ┌────┴────┐
sim       não
 ↓         ↓
usa      cria
 └────┬────┘
      ↓
   Payment
```

## Endpoints

No MVP:

```http
GET /beneficiaries
GET /beneficiaries/{beneficiary_id}
```

A criação explícita de beneficiários não é necessária inicialmente.

O beneficiário será criado automaticamente quando necessário durante a confirmação de um Payment.

Endpoints como:

```http
POST  /beneficiaries
PATCH /beneficiaries/{beneficiary_id}
DELETE /beneficiaries/{beneficiary_id}
```

ficam fora do MVP.

---

# 15. Agregado Institution

O agregado `Institution` representa uma instituição financeira normalizada.

```text
domain/institution/
```

Seu Aggregate Root é `Institution`.

Exemplos:

```text
Itaú
Nubank
Bradesco
Caixa
Santander
```

## Responsabilidades

O agregado é responsável por:

* identificação da instituição;
* nome normalizado;
* código interno;
* manutenção das instituições reconhecidas pelo sistema.

Durante o processamento de um Receipt, diferentes representações da mesma instituição devem ser normalizadas.

Exemplo:

```text
ITAÚ
Banco Itaú
Itaú Unibanco
Itaú S.A.
```

Essas representações devem ser normalizadas para uma mesma Institution.

## Endpoints

Não haverá endpoints públicos para Institution no MVP.

As instituições serão utilizadas internamente pelos demais agregados.

---

# 16. Endpoints da API

A API do MVP será composta por:

## Auth

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Receipts

```http
POST /receipts
GET  /receipts/{receipt_id}
POST /receipts/{receipt_id}/confirm
```

## Payments

```http
GET /payments
GET /payments/{payment_id}

GET /payments/summary/count
GET /payments/summary/total
GET /payments/summary/max
GET /payments/summary/beneficiary
```

## Beneficiaries

```http
GET /beneficiaries
GET /beneficiaries/{beneficiary_id}
```

## Institutions

Nenhum endpoint público no MVP.

---

# 17. Fluxo de dependência da API

A arquitetura seguirá a direção:

```text
Route
  ↓
Schema
  ↓
Service
  ↓
Repository
  ↓
Model
  ↓
Database
```

### Route

Responsável pela camada HTTP:

* endpoint;
* método HTTP;
* autenticação;
* recebimento da requisição;
* retorno da resposta.

### Schema

Responsável pela entrada e saída da API utilizando Pydantic.

### Service

Responsável pelas operações e regras de negócio do domínio.

### Repository

Responsável pelo acesso aos dados.

### Model

Representa a persistência através do SQLAlchemy.

### Database

Responsável pela persistência no PostgreSQL.

---

# 18. Exemplo de estrutura de domínio

Cada domínio poderá seguir a estrutura:

```text
domain/
└── receipt/
    ├── route.py
    ├── service.py
    ├── repository.py
    └── schema.py
```

Da mesma forma:

```text
domain/
├── auth/
│   ├── route.py
│   ├── service.py
│   ├── repository.py
│   └── schema.py
│
├── receipt/
│   ├── route.py
│   ├── service.py
│   ├── repository.py
│   └── schema.py
│
├── payment/
│   ├── route.py
│   ├── service.py
│   ├── repository.py
│   └── schema.py
│
├── beneficiary/
│   ├── route.py
│   ├── service.py
│   ├── repository.py
│   └── schema.py
│
└── institution/
    ├── route.py
    ├── service.py
    ├── repository.py
    └── schema.py
```

A existência desses arquivos representa a separação de responsabilidade do domínio e não significa que todos precisam necessariamente expor endpoints públicos.

Por exemplo, `Institution` possui domínio próprio, mas não possui API pública no MVP.

---

# 19. Regra de dependência entre domínios

Um domínio não deve acessar diretamente a implementação interna de outro domínio.

Quando uma operação envolver mais de um agregado, o fluxo deve ser coordenado pelo service responsável pela operação.

No caso da confirmação:

```text
Receipt Service
      │
      ├── valida Receipt
      │
      ├── resolve Beneficiary
      │
      ├── resolve Institution
      │
      └── cria Payment
```

A operação é tratada como uma única operação de negócio, mesmo envolvendo múltiplos agregados.

---

# 20. Confirmação do Receipt

A confirmação é uma das principais operações de negócio da aplicação.

Fluxo:

```text
POST /receipts/{receipt_id}/confirm
```

### Etapas

1. Autenticar usuário.
2. Recuperar Receipt.
3. Validar propriedade do Receipt.
4. Validar estado do Receipt.
5. Validar os dados confirmados.
6. Identificar ou criar Beneficiary.
7. Resolver Institution de origem.
8. Resolver Institution de destino, quando existente.
9. Criar Payment.
10. Associar Payment ao Receipt.
11. Persistir a operação em uma transação.
12. Retornar o Payment confirmado.

A operação deve ser transacional.

Se qualquer etapa necessária falhar, o Payment não deve ser parcialmente persistido.

---

# 21. Isolamento dos dados

Todo dado pertencente ao usuário deve respeitar isolamento por `user_id`.

Exemplo:

```text
User A
 ├── Receipts
 ├── Payments
 └── Beneficiaries

User B
 ├── Receipts
 ├── Payments
 └── Beneficiaries
```

Um usuário nunca poderá:

* consultar Receipt de outro usuário;
* consultar Payment de outro usuário;
* consultar Beneficiary de outro usuário;
* confirmar Receipt de outro usuário;
* alterar dados pertencentes a outro usuário.

O backend é responsável por garantir esse isolamento.

Não será confiado ao frontend o controle de acesso aos dados.

---

# 22. Aggregate x Entity x Table

A arquitetura não deve considerar os conceitos como equivalentes.

### Table

Representa a persistência no banco.

Exemplo:

```text
payments
```

### Entity

Representa um objeto com identidade dentro do domínio.

Exemplo:

```text
Payment
```

### Aggregate

Representa um limite de consistência e responsabilidade de negócio.

Exemplo:

```text
Payment
```

Uma tabela não precisa necessariamente representar um agregado.

Da mesma forma, uma entidade não precisa necessariamente possuir um domínio HTTP próprio.

No projeto:

```text
User
Role
Password
Authentication
```

são persistidos em tabelas diferentes, mas fazem parte do mesmo agregado de autenticação/usuário.

Enquanto:

```text
Receipt
Payment
```

possuem tabelas relacionadas, mas pertencem a agregados diferentes.

---

# 23. Mapa final dos agregados

O modelo atual fica:

```text
┌──────────────────────────────────────────┐
│                  AUTH                    │
│                                          │
│ User                                     │
│ ├── Role                                 │
│ ├── Password                             │
│ └── Authentication                       │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│                RECEIPT                   │
│                                          │
│ Receipt                                  │
│ └── processamento/extração              │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│                PAYMENT                   │
│                                          │
│ Payment                                  │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│              BENEFICIARY                 │
│                                          │
│ Beneficiary                              │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│              INSTITUTION                 │
│                                          │
│ Institution                              │
└──────────────────────────────────────────┘
```

As principais relações são:

```text
User
 │
 ├────────────── Receipt
 │                  │
 │                  │ confirmation
 │                  ↓
 │               Payment
 │                  │
 │          ┌───────┴────────┐
 │          ↓                ↓
 │     Beneficiary      Institution
 │
 └────── Beneficiary
```

As relações entre agregados representam referências e operações de negócio, não propriedade estrutural de um agregado sobre o outro.

---

# 24. Princípios arquiteturais

O backend seguirá os seguintes princípios:

1. **Simplicidade antes de abstração.**
2. **Cada agregado possui responsabilidade clara.**
3. **FK não define automaticamente um agregado.**
4. **Regras de negócio ficam nos services/domínios.**
5. **Models representam persistência, não regras de negócio.**
6. **Core não conhece os domínios.**
7. **Domínios não devem depender da implementação interna de outros domínios.**
8. **O backend é a autoridade sobre regras e permissões.**
9. **Dados de usuários são isolados por `user_id`.**
10. **Receipt e Payment são conceitos distintos.**
11. **Payment nasce através da confirmação de Receipt.**
12. **Institutions são normalizadas e controladas internamente.**
13. **Nem toda entidade precisa possuir endpoint público.**
14. **Nem toda tabela precisa possuir um domínio próprio.**
15. **Operações que envolvem múltiplos agregados devem ser transacionais quando necessário.**
16. **Enums de persistência são centralizados em `models/enum.py`.**
17. **Um enum não deve ser duplicado em diferentes models.**
18. **Campos com valores fechados devem utilizar enums centralizados quando a definição for estrutural da entidade.**

---

# 25. Estrutura arquitetural final

A visão geral do backend fica:

```text
                    HTTP
                     │
                     ↓
                  FastAPI
                     │
             ┌───────┴────────┐
             ↓                ↓
           Route           Pydantic
             │              Schema
             └───────┬────────┘
                     ↓
                  Service
                     │
             ┌───────┼────────┐
             ↓       ↓        ↓
        Repository  Domain   Rules
             │
             ↓
           Model
             │
             ↓
        PostgreSQL
```

Com os domínios:

```text
domain/
├── auth
├── receipt
├── payment
├── beneficiary
└── institution
```

Com os models:

```text
models/
├── enum.py
├── user.py
├── role.py
├── password.py
├── authentication.py
├── institution.py
├── beneficiary.py
├── receipt.py
└── payment.py
```

E a infraestrutura compartilhada:

```text
core/
├── cache
├── context
├── database
├── exceptions
├── logging
├── pagination
├── repository
├── security
├── service
└── settings

shared/
```

A pasta `models/enum.py` é a fonte única das definições de enum utilizadas pelos models de persistência.

Dessa forma, qualquer entidade que precise de uma definição fechada de valores utiliza o enum centralizado, evitando duplicação e mantendo o modelo de dados consistente.
