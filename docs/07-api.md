# Comprovante — API

## 1. Objetivo

Este documento define o contrato da API REST do Comprovante.

A API será responsável por:

* autenticação;
* cadastro de usuários;
* recebimento de comprovantes;
* processamento dos comprovantes;
* disponibilização dos dados extraídos;
* confirmação de pagamentos;
* consulta do histórico;
* consulta por beneficiário;
* consultas agregadas por período.

A API será implementada utilizando **FastAPI** e disponibilizará documentação OpenAPI.

A API será a autoridade sobre:

* autenticação;
* autorização;
* validação;
* regras de negócio;
* processamento;
* persistência;
* isolamento dos dados entre usuários.

O frontend não terá autoridade para registrar pagamentos diretamente.

---

# 2. Princípios

## 2.1 API REST

A comunicação entre frontend e backend será realizada por HTTP utilizando uma API REST.

Os recursos principais serão:

* `/auth`
* `/receipts`
* `/payments`
* `/beneficiaries`
* `/institutions`

---

## 2.2 Usuário autenticado

Endpoints protegidos exigem autenticação.

A identidade do usuário será obtida a partir do token de autenticação.

O cliente não poderá informar livremente um `user_id` para acessar ou modificar recursos pertencentes a outro usuário.

---

## 2.3 Isolamento

Toda operação protegida deverá considerar o usuário autenticado.

Exemplo:

```text
Usuário A → /payments
              ↓
        somente pagamentos
        pertencentes ao Usuário A
```

O backend nunca deverá confiar em identificadores enviados pelo frontend para determinar o proprietário de um recurso.

---

# 3. Autenticação

## 3.1 Cadastro

### `POST /auth/register`

Cria um novo usuário.

### Request

```json
{
  "name": "João Machado",
  "username": "joao",
  "email": "joao@example.com",
  "password": "senha",
  "date_of_birth": "1990-01-01"
}
```

### Regras

* `username` deve ser único;
* `email` deve ser único;
* senha nunca será armazenada em texto puro;
* a senha será transformada em hash antes da persistência;
* o usuário será criado com status `ACTIVE`;
* será criado seu registro de senha;
* será criado seu registro de autenticação;
* o papel padrão será definido pelo backend.

### Response

```json
{
  "id": "uuid",
  "name": "João Machado",
  "username": "joao",
  "email": "joao@example.com",
  "status": "ACTIVE"
}
```

---

# 4. Login

### `POST /auth/login`

Autentica um usuário.

### Request

```json
{
  "credential": "joao",
  "password": "senha"
}
```

`credential` poderá representar o `username` ou `email`.

### Fluxo

```text
credential + password
        ↓
localizar usuário
        ↓
validar status
        ↓
obter hash da senha
        ↓
comparar senha
        ↓
sucesso?
   ┌────┴────┐
  NÃO       SIM
   ↓         ↓
falha      token
```

### Sucesso

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

### Falha

Credencial inválida deverá retornar erro de autenticação sem informar se:

* o usuário existe;
* o email existe;
* o username existe;
* a senha estava incorreta.

Exemplo:

```json
{
  "detail": "Invalid credentials"
}
```

---

# 5. Controle de tentativas

Cada tentativa de autenticação deverá atualizar `authentications`.

### Sucesso

* `total` +1
* `total_success` +1
* `failed_attempts` = 0
* `last_authenticated_at` atualizado

### Falha

* `total` +1
* `total_failures` +1
* `failed_attempts` +1

Ao atingir o limite definido pela regra de segurança:

```text
failed_attempts >= threshold
```

o usuário poderá ter seu status alterado para:

```text
LOCKED
```

O valor definitivo do threshold será definido na implementação.

---

# 6. Usuário autenticado

### `GET /auth/me`

Retorna os dados do usuário associado ao token.

### Request

Não recebe `user_id`.

### Response

```json
{
  "id": "uuid",
  "name": "João Machado",
  "username": "joao",
  "email": "joao@example.com",
  "status": "ACTIVE",
  "date_of_birth": "1990-01-01"
}
```

---

# 7. Recebimento de comprovantes

## 7.1 Upload

### `POST /receipts`

Recebe um comprovante.

O endpoint deverá utilizar `multipart/form-data`.

### Request

```text
file=<arquivo>
```

Arquivos inicialmente suportados:

* PDF;
* imagens.

Os formatos e limites definitivos serão definidos na implementação.

---

# 8. Criação do Receipt

O upload cria um registro em `receipts`.

Inicialmente:

```text
processing_status = RECEIVED
```

O arquivo original será armazenado no storage.

O banco armazenará apenas a referência ao arquivo.

### Response

```json
{
  "id": "uuid",
  "file_name": "comprovante.pdf",
  "file_type": "application/pdf",
  "file_size": 152340,
  "processing_status": "RECEIVED",
  "created_at": "2026-09-12T23:00:00"
}
```

O upload não cria um Payment.

---

# 9. Processamento

Após o recebimento, o comprovante será processado.

Fluxo:

```text
RECEIVED
   ↓
PROCESSING
   ↓
extração
   ↓
parser determinístico
   ↓
resultado suficiente?
   ├── SIM → PROCESSED
   │
   └── NÃO → AI fallback
                 ↓
              PROCESSED
```

Se ocorrer uma falha que impeça o processamento:

```text
PROCESSING → FAILED
```

---

# 10. Consulta do Receipt

### `GET /receipts/{receipt_id}`

Retorna o estado e os dados processados do comprovante.

### Response

```json
{
  "id": "uuid",
  "file_name": "comprovante.pdf",
  "file_type": "application/pdf",
  "file_size": 152340,
  "processing_status": "PROCESSED",
  "extracted_data": {
		"fine": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"payer": {
			"value": "PAYER",
			"status": "FOUND"
		},
		"barcode": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"due_date": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"discount": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"interest": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"paid_amount": {
			"value": "4186.17",
			"status": "FOUND"
		},
		"beneficiary": {
			"value": "ITAU UNIBANCO HOLDING S.A.",
			"status": "FOUND"
		},
		"payment_date": {
			"value": "2026-09-08",
			"status": "FOUND"
		},
		"total_charges": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"authentication": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"transaction_id": {
			"value": null,
			"status": "NOT_FOUND"
		},
		"effective_payer": {
			"value": "PAYER",
			"status": "FOUND"
		},
		"document_amount": {
			"value": "4186.17",
			"status": "FOUND"
		},
		"source_institution": {
			"value": "SOURCE INSTITUTION",
			"status": "FOUND"
		},
		"destination_institution": {
			"value": null,
			"status": "NOT_FOUND"
		}
	},
  "created_at": "2026-09-12T23:00:00"
}
```

Os dados retornados são candidatos à confirmação.

Não representam ainda um pagamento definitivo.

---

# 11. Estados do Receipt

Os estados possíveis são:

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
```

### `RECEIVED`

Arquivo recebido e aguardando processamento.

### `PROCESSING`

Processamento em andamento.

### `PROCESSED`

Processamento concluído e dados disponíveis para revisão.

### `FAILED`

Processamento não concluído.

---

# 12. Confirmação do pagamento

## 12.1 Criar Payment

### `POST /receipts/{receipt_id}/confirm`

Confirma os dados do comprovante e cria o Payment.

O frontend deverá enviar os dados revisados pelo usuário.

### Request

```json
{
	"fine": "0.00",
		"payer": "PAYER",
		"barcode": "00190000090360004100200002433175915650000474175",
		"due_date": "2026-09-10",
		"discount": "0.00",
		"interest": "0.00",
		"paid_amount": "4741.75",
		"beneficiary": "BENEFICIARY",
		"payment_date": "2026-09-03",		
		"transaction_id": "71207347056",
		"effective_payer": "PAYER",
		"document_amount": "4741.75",
		"source_institution": "Caixa",
		"destination_institution": "DESTINATION INSTITUTION"
}
```

A confirmação representa uma ação explícita do usuário.

---

# 13. Regras de confirmação

O backend deverá:

1. localizar o Receipt;
2. validar que pertence ao usuário autenticado;
3. validar o estado do Receipt;
4. validar os dados recebidos;
5. localizar ou criar o Beneficiary;
6. localizar as Institutions;
7. criar o Payment;
8. associar o Payment ao Receipt;
9. executar tudo dentro de uma transação.

Fluxo:

```text
POST /receipts/{id}/confirm
          ↓
      validar Receipt
          ↓
      validar dados
          ↓
   Beneficiary existente?
      ├── SIM
      └── NÃO → criar
          ↓
     Institutions
          ↓
       Payment
          ↓
    associar Receipt
          ↓
        COMMIT
```

Qualquer erro deverá provocar rollback da operação.

---

# 14. Idempotência da confirmação

Um Receipt não poderá gerar dois Payments.

O backend deverá impedir:

```text
Receipt A → Payment A
Receipt A → Payment B ❌
```

O relacionamento será protegido também pela restrição definida no banco.

Caso um Receipt já tenha sido confirmado, uma nova confirmação deverá retornar erro de negócio.

---

# 15. Payment

## 15.1 Consulta individual

### `GET /payments/{payment_id}`

Retorna um pagamento pertencente ao usuário autenticado.

### Response

```json
{
  "id": "uuid",
  "receipt_id": "uuid",
  "beneficiary": {
    "id": "uuid",
    "name": "Neoenergia"
  },
  "source_institution": {
    "id": "uuid",
    "name": "Itaú"
  },
  "destination_institution": null,
  "amount": 387.42,
  "payment_date": "2026-09-12",
  "created_at": "2026-09-12T23:05:00"
}
```

---

# 16. Histórico de pagamentos

### `GET /payments`

Retorna os pagamentos do usuário.

### Filtros

Inicialmente:

* período inicial;
* período final;
* beneficiário.

Exemplo conceitual:

```text
GET /payments?start_date=2026-09-01&end_date=2026-09-30
```

O backend deverá retornar apenas Payments pertencentes ao usuário autenticado.

---

# 17. Beneficiários

## 17.1 Listagem

### `GET /beneficiaries`

Retorna os beneficiários utilizados pelo usuário.

### Response

```json
[
  {
    "id": "uuid",
    "name": "Neoenergia"
  },
  {
    "id": "uuid",
    "name": "Claro"
  }
]
```

---

# 18. Busca de beneficiário

A API deverá permitir localizar pagamentos relacionados a um beneficiário.

Exemplo:

```text
GET /payments?beneficiary=Neoenergia
```

A busca deverá considerar somente os beneficiários do usuário autenticado.

---

# 19. Consultas agregadas

As consultas definidas no domínio serão disponibilizadas pela API.

## 19.1 Quantidade de pagamentos

### `GET /payments/summary/count`

Exemplo:

```text
GET /payments/summary/count?start_date=2026-09-01&end_date=2026-09-30
```

Response:

```json
{
  "count": 8
}
```

---

# 20. Total pago

### `GET /payments/summary/total`

Exemplo:

```text
GET /payments/summary/total?start_date=2026-09-01&end_date=2026-09-30
```

Response:

```json
{
  "total": 2450.73
}
```

---

# 21. Maior pagamento

### `GET /payments/summary/max`

Exemplo:

```text
GET /payments/summary/max?start_date=2026-09-01&end_date=2026-09-30
```

Response:

```json
{
  "payment": {
    "id": "uuid",
    "beneficiary": "Neoenergia",
    "amount": 850.00,
    "payment_date": "2026-09-12"
  }
}
```

Quando não houver pagamentos no período:

```json
{
  "payment": null
}
```

---

# 22. Total por beneficiário

### `GET /payments/summary/beneficiary`

Exemplo:

```text
GET /payments/summary/beneficiary?beneficiary=Neoenergia&start_date=2026-09-01&end_date=2026-09-30
```

Response:

```json
{
  "beneficiary": "Neoenergia",
  "total": 850.00
}
```

---

# 23. Período

As consultas deverão utilizar datas explícitas.

Exemplo:

```text
start_date=2026-09-01
end_date=2026-09-30
```

O `payment_date` será utilizado para determinar se o pagamento pertence ao período.

`created_at` não será utilizado para determinar o período financeiro.

---

# 24. Institutions

Institutions serão utilizadas pelo backend para normalizar e relacionar instituições financeiras.

Inicialmente não será necessário disponibilizar CRUD público de instituições.

A criação e manutenção das instituições será responsabilidade do backend.

O frontend receberá as instituições necessárias para apresentação ou confirmação quando aplicável.

---

# 25. Beneficiary e Institution na confirmação

O frontend poderá enviar o nome revisado pelo usuário.

O backend será responsável por:

* localizar registro existente;
* normalizar;
* criar quando necessário;
* manter o relacionamento correto.

O frontend não deverá controlar diretamente IDs de instituições ou beneficiários pertencentes a outros usuários.

---

# 26. Validação

Os contratos de entrada e saída serão definidos utilizando **Pydantic**.

A validação ocorrerá em camadas:

```text
HTTP Request
     ↓
Pydantic
     ↓
Application / Domain
     ↓
Database
```

A validação do Pydantic não substitui as regras de negócio.

---

# 27. Erros HTTP

A API deverá utilizar códigos HTTP adequados.

Principais:

| Código | Uso                                |
| ------ | ---------------------------------- |
| `200`  | Operação concluída                 |
| `201`  | Recurso criado                     |
| `400`  | Requisição inválida                |
| `401`  | Não autenticado                    |
| `403`  | Operação não permitida             |
| `404`  | Recurso não encontrado             |
| `409`  | Conflito                           |
| `422`  | Dados incompatíveis com o contrato |
| `500`  | Erro interno                       |

---

# 28. Erros de negócio

Erros de negócio deverão possuir mensagens claras e previsíveis.

Exemplos:

```json
{
  "detail": "Receipt has already been confirmed"
}
```

```json
{
  "detail": "Receipt processing has not finished"
}
```

```json
{
  "detail": "User account is locked"
}
```

---

# 29. Autorização

O backend deverá verificar a propriedade do recurso antes de qualquer operação protegida.

Exemplo:

```text
GET /payments/payment-do-usuario-B

Usuário A
   ↓
token → user_id = A
   ↓
Payment pertence a B
   ↓
acesso negado
```

O backend não deverá permitir que o cliente contorne essa regra alterando IDs na URL ou no payload.

---

# 30. Dados sensíveis

A API não deverá retornar:

* senha;
* hash da senha;
* `last_value`;
* informações internas de autenticação;
* tokens armazenados;
* informações internas desnecessárias do processamento.

O `extracted_data` poderá retornar informações necessárias para a revisão do usuário.

---

# 31. Upload e segurança

O endpoint de upload deverá validar:

* extensão;
* MIME type;
* tamanho;
* integridade do arquivo;
* arquivo vazio;
* formato suportado.

O arquivo recebido não deverá ser tratado como confiável simplesmente por possuir uma extensão válida.

A estratégia definitiva de segurança de arquivos será detalhada durante a implementação.

---

# 32. Processamento assíncrono

O processamento poderá ser assíncrono.

Nesse caso:

```text
POST /receipts
      ↓
201 RECEIVED
      ↓
processamento
      ↓
GET /receipts/{id}
      ↓
PROCESSING / PROCESSED / FAILED
```

O frontend não deverá depender de uma requisição HTTP longa para concluir o processamento.

A tecnologia utilizada para fila/background processing será definida durante a implementação.

---

# 33. Contratos e domínio

Os contratos HTTP não deverão representar diretamente os modelos SQLAlchemy.

Estrutura conceitual:

```text
HTTP
 ↓
Pydantic Schema
 ↓
Application / Use Case
 ↓
Domain
 ↓
Repository / SQLAlchemy
 ↓
PostgreSQL
```

Isso evita acoplamento direto entre:

* API;
* ORM;
* banco;
* domínio.

---

# 34. Organização da API

A implementação poderá ser organizada por domínio:

```text
auth/
receipts/
payments/
beneficiaries/
institutions/
```

Cada domínio deverá concentrar:

* endpoints;
* schemas;
* regras específicas;
* serviços;
* dependências necessárias.

A organização interna definitiva será definida durante a implementação.

---

# 35. OpenAPI

FastAPI deverá gerar automaticamente a especificação OpenAPI.

A documentação deverá permitir visualizar:

* endpoints;
* métodos;
* parâmetros;
* schemas;
* respostas;
* erros;
* autenticação.

A especificação deverá permanecer alinhada com os contratos reais da API.

---

# 36. API inicial do MVP

A API mínima será composta por:

### Auth

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Receipts

```text
POST /receipts
GET  /receipts/{receipt_id}
POST /receipts/{receipt_id}/confirm
```

### Payments

```text
GET /payments
GET /payments/{payment_id}
```

### Beneficiaries

```text
GET /beneficiaries
```

### Queries

```text
GET /payments/summary/count
GET /payments/summary/total
GET /payments/summary/max
GET /payments/summary/beneficiary
```

Institutions não terão CRUD público no MVP.

---

# 37. Fluxo completo da API

```text
                 ┌──────────────┐
                 │    CLIENT    │
                 └──────┬───────┘
                        │
                        ▼
                 POST /receipts
                        │
                        ▼
                 ┌──────────────┐
                 │    RECEIPT   │
                 │   RECEIVED   │
                 └──────┬───────┘
                        │
                        ▼
                    PROCESSING
                        │
                        ▼
              extração + interpretação
                        │
                        ▼
                    PROCESSED
                        │
                        ▼
               GET /receipts/{id}
                        │
                        ▼
                  revisão do usuário
                        │
                        ▼
            POST /receipts/{id}/confirm
                        │
                        ▼
                 ┌──────────────┐
                 │   PAYMENT    │
                 │  CONFIRMED   │
                 └──────┬───────┘
                        │
                        ▼
                 GET /payments
                        │
                        ▼
                    consultas
```

---

# 38. Responsabilidades

### Frontend

Responsável por:

* enviar arquivos;
* apresentar processamento;
* apresentar dados extraídos;
* permitir correção;
* solicitar confirmação;
* apresentar histórico;
* apresentar consultas.

### API

Responsável por:

* autenticação;
* autorização;
* validação;
* processamento;
* interpretação;
* persistência;
* regras de negócio;
* isolamento;
* consultas.

### Banco

Responsável por:

* persistência;
* integridade referencial;
* constraints;
* índices;
* transações.

### Storage

Responsável por:

* armazenar o arquivo original;
* preservar o comprovante;
* disponibilizar o arquivo quando necessário.

---

# 39. Fora do escopo da API

Não serão implementados no MVP:

* integração direta com bancos;
* Open Finance;
* realização de pagamentos;
* conciliação bancária;
* controle de saldo;
* orçamento;
* cartões;
* investimentos;
* notificações;
* WhatsApp API;
* múltiplos usuários;
* processamento em lote;
* aplicativo nativo;
* CRUD público de instituições;
* logout específico;
* MFA;
* refresh token;
* sessões avançadas.

Esses recursos poderão ser considerados posteriormente caso façam sentido para o produto.

---

# 40. Princípio fundamental

A API deve permanecer simples.

O fluxo principal deve continuar sendo:

```text
Receber
   ↓
Processar
   ↓
Apresentar
   ↓
Revisar
   ↓
Confirmar
   ↓
Registrar
   ↓
Consultar
```

A API não deve antecipar funcionalidades que ainda não possuem necessidade no produto.

A complexidade deverá ser adicionada somente quando existir uma necessidade real.
