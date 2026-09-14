# Comprovante — Modelo de banco de dados

## 1. Objetivo

Este documento define o modelo de persistência do Comprovante utilizando PostgreSQL.

A estrutura deve representar o domínio definido em `05-domain.md` e os contratos definidos em `09-domain-contracts.md`, mantendo:

* simplicidade;
* integridade dos dados;
* isolamento dos dados financeiros por usuário;
* facilidade de manutenção;
* possibilidade de evolução;
* baixo acoplamento entre domínio e infraestrutura.

Este documento define:

* tabelas;
* colunas;
* tipos;
* chaves primárias;
* chaves estrangeiras;
* restrições;
* índices;
* relacionamentos;
* regras de integridade;
* estratégia de soft delete.

A implementação utilizando SQLAlchemy e Alembic será realizada posteriormente.

---

# 2. Banco de dados

O banco de dados escolhido é:

**PostgreSQL**

O PostgreSQL será responsável pelo armazenamento dos dados estruturados da aplicação.

Arquivos originais dos comprovantes não serão armazenados diretamente no PostgreSQL.

Os arquivos serão armazenados no serviço de storage definido na arquitetura, enquanto o banco armazenará apenas sua referência.

---

# 3. Convenções

As tabelas utilizarão nomes no plural e `snake_case`.

Exemplos:

```text
users
roles
passwords
authentications
receipts
payments
beneficiaries
institutions
```

As colunas também utilizarão `snake_case`.

Exemplo:

```text
created_at
updated_at
deleted_at
last_authenticated_at
```

---

# 4. Identificadores

Todas as entidades persistidas possuirão uma chave primária:

```text
id
```

O tipo exato do identificador será definido na implementação do banco/SQLAlchemy.

O identificador deve ser:

* único;
* estável;
* não reutilizado;
* independente de dados de negócio.

O `id` não deve representar `username`, `email`, nome ou qualquer outro atributo mutável.

---

# 5. Timestamps

As entidades que possuem ciclo de vida persistente utilizarão:

```text
created_at
updated_at
deleted_at
```

### `created_at`

Momento em que o registro foi criado.

### `updated_at`

Momento da última alteração do registro.

### `deleted_at`

Momento da exclusão lógica.

Quando `deleted_at` for `NULL`, o registro está ativo.

Quando `deleted_at` possuir valor, o registro está logicamente excluído.

---

# 6. Soft Delete

O sistema utilizará soft delete para entidades que precisem preservar histórico ou integridade referencial.

A exclusão lógica será representada por:

```text
deleted_at IS NULL
```

para registros ativos.

Registros com:

```text
deleted_at IS NOT NULL
```

não devem aparecer nas consultas normais da aplicação.

A aplicação não deve utilizar exclusão física como comportamento padrão.

Para entidades globais, como `Beneficiary` e `Institution`, a existência de um registro excluído logicamente não deve permitir duplicação indevida de uma entidade equivalente.

A estratégia de unicidade considerando soft delete será definida nas migrations.

---

# 7. Tabela `roles`

Representa os perfis de acesso da aplicação.

### Colunas

| Coluna        | Tipo conceitual | Obrigatório | Regra          |
| ------------- | --------------- | ----------: | -------------- |
| `id`          | identifier      |         SIM | PK             |
| `name`        | string          |         SIM | Nome do perfil |
| `name_code`   | string          |         SIM | Código único   |
| `description` | string          |         NÃO | Descrição      |
| `created_at`  | timestamp       |         SIM | Criação        |
| `updated_at`  | timestamp       |         SIM | Atualização    |
| `deleted_at`  | timestamp       |         NÃO | Soft delete    |

### Restrições

```text
PRIMARY KEY (id)
UNIQUE (name_code)
```

`name_code` será utilizado pelo sistema para identificar o perfil de forma estável.

Exemplo:

```text
name = "Usuário"
name_code = "USER"
```

---

# 8. Tabela `users`

Representa os usuários da aplicação.

### Colunas

| Coluna          | Tipo conceitual | Obrigatório | Regra                    |
| --------------- | --------------- | ----------: | ------------------------ |
| `id`            | identifier      |         SIM | PK                       |
| `role_id`       | identifier      |         SIM | FK → roles               |
| `name`          | string          |         SIM | Nome                     |
| `username`      | string          |         SIM | Único                    |
| `email`         | string          |         SIM | Único                    |
| `status`        | enum            |         SIM | ACTIVE, LOCKED, INACTIVE |
| `date_of_birth` | date            |         NÃO | Data de nascimento       |
| `created_at`    | timestamp       |         SIM | Criação                  |
| `updated_at`    | timestamp       |         SIM | Atualização              |
| `deleted_at`    | timestamp       |         NÃO | Soft delete              |

### Status

```text
ACTIVE
LOCKED
INACTIVE
```

### Restrições

```text
PRIMARY KEY (id)

FOREIGN KEY (role_id)
REFERENCES roles(id)

UNIQUE (username)

UNIQUE (email)
```

### Regras

Usuários `LOCKED` e `INACTIVE` não podem realizar login.

Usuários com `deleted_at IS NOT NULL` também não podem realizar login.

---

# 9. Tabela `passwords`

Representa as credenciais do usuário.

### Colunas

| Coluna       | Tipo conceitual | Obrigatório | Regra                  |
| ------------ | --------------- | ----------: | ---------------------- |
| `id`         | identifier      |         SIM | PK                     |
| `user_id`    | identifier      |         SIM | FK → users             |
| `value`      | string          |         SIM | Hash da senha atual    |
| `last_value` | string          |         NÃO | Hash da senha anterior |
| `created_at` | timestamp       |         SIM | Criação                |
| `updated_at` | timestamp       |         SIM | Atualização            |
| `deleted_at` | timestamp       |         NÃO | Soft delete            |

### Restrições

```text
PRIMARY KEY (id)

FOREIGN KEY (user_id)
REFERENCES users(id)

UNIQUE (user_id)
```

Um usuário possui apenas uma credencial ativa no MVP.

### Regra de segurança

`value` nunca deve conter a senha em texto puro.

O mesmo vale para `last_value`.

Exemplo:

```text
senha:
MinhaSenha123

armazenado:

value:
$hash...
```

Nunca:

```text
value:
MinhaSenha123
```

---

# 10. Tabela `authentications`

Representa o histórico resumido e o estado de autenticação do usuário.

### Colunas

| Coluna                  | Tipo conceitual | Obrigatório | Regra               |
| ----------------------- | --------------- | ----------: | ------------------- |
| `id`                    | identifier      |         SIM | PK                  |
| `user_id`               | identifier      |         SIM | FK → users          |
| `total`                 | integer         |         SIM | Total de tentativas |
| `total_success`         | integer         |         SIM | Total de sucessos   |
| `total_failures`        | integer         |         SIM | Total de falhas     |
| `failed_attempts`       | integer         |         SIM | Falhas consecutivas |
| `last_authenticated_at` | timestamp       |         NÃO | Último login válido |
| `created_at`            | timestamp       |         SIM | Criação             |
| `updated_at`            | timestamp       |         SIM | Atualização         |
| `deleted_at`            | timestamp       |         NÃO | Soft delete         |

### Valores iniciais

Ao criar o usuário:

```text
total = 0
total_success = 0
total_failures = 0
failed_attempts = 0
last_authenticated_at = NULL
```

### Restrições

```text
PRIMARY KEY (id)

FOREIGN KEY (user_id)
REFERENCES users(id)

UNIQUE (user_id)
```

Existe apenas um registro de autenticação por usuário no MVP.

---

# 11. Relacionamento de autenticação

O relacionamento é:

```text
Role
  1
  │
  N
User
  │
  ├──────── 1 Password
  │
  └──────── 1 Authentication
```

Portanto:

* um `Role` pode possuir vários usuários;
* um `User` possui um `Password`;
* um `User` possui um `Authentication`.

---

# 12. Tabela `institutions`

Representa instituições financeiras normalizadas.

`Institution` é uma entidade global e compartilhada entre os usuários.

### Colunas

| Coluna       | Tipo conceitual | Obrigatório | Regra            |
| ------------ | --------------- | ----------: | ---------------- |
| `id`         | identifier      |         SIM | PK               |
| `name`       | string          |         SIM | Nome normalizado |
| `name_code`  | string          |         SIM | Código único     |
| `created_at` | timestamp       |         SIM | Criação          |
| `updated_at` | timestamp       |         SIM | Atualização      |
| `deleted_at` | timestamp       |         NÃO | Soft delete      |

### Restrições

```text
PRIMARY KEY (id)

UNIQUE (name_code)
```

Exemplo:

```text
name = "Itaú"
name_code = "ITAU"
```

---

# 13. Escopo global de `Institution`

Uma `Institution` não pertence a um usuário.

Se o usuário X for o primeiro a utilizar o Itaú:

```text
User X
   ↓
Itaú não existe
   ↓
cria Institution
```

A Institution criada é global.

Posteriormente:

```text
User Y
   ↓
utiliza Itaú
   ↓
reutiliza a mesma Institution
```

Portanto:

```text
User X ──┐
User Y ──┼── Institution: Itaú
User Z ──┘
```

Não devem existir registros separados de Itaú para cada usuário.

---

# 14. Normalização de instituições

A informação original extraída do comprovante não deve ser confundida com a instituição normalizada.

Exemplo:

```text
Texto extraído:
ITAÚ UNIBANCO S.A.

Instituição:
Itaú

name_code:
ITAU
```

Representações equivalentes da mesma instituição devem ser resolvidas para uma única Institution quando houver informação suficiente para determinar a equivalência.

Exemplos:

```text
Itaú
Itau
ITAU
Banco Itaú
Itaú Unibanco
```

podem resultar em:

```text
name = "Itaú"
name_code = "ITAU"
```

A informação original poderá permanecer nos dados extraídos do `Receipt`, quando necessário para rastreabilidade.

---

# 15. Tabela `beneficiaries`

Representa beneficiários normalizados.

`Beneficiary` é uma entidade global e compartilhada entre os usuários.

### Colunas

| Coluna       | Tipo conceitual | Obrigatório | Regra                     |
| ------------ | --------------- | ----------: | ------------------------- |
| `id`         | identifier      |         SIM | PK                        |
| `name`       | string          |         SIM | Nome confirmado           |
| `name_code`  | string          |         SIM | Identificador normalizado |
| `created_at` | timestamp       |         SIM | Criação                   |
| `updated_at` | timestamp       |         SIM | Atualização               |
| `deleted_at` | timestamp       |         NÃO | Soft delete               |

### Restrições

```text
PRIMARY KEY (id)

UNIQUE (name_code)
```

O `name_code` representa a forma normalizada utilizada para identificar o beneficiário.

---

# 16. Escopo global de `Beneficiary`

Um `Beneficiary` não pertence a um usuário.

Se o usuário X for o primeiro a utilizar `AMAZON`:

```text
User X
   ↓
AMAZON não existe
   ↓
cria Beneficiary
```

O Beneficiary criado é global.

Posteriormente:

```text
User Y
   ↓
utiliza AMAZON
   ↓
reutiliza o mesmo Beneficiary
```

Portanto:

```text
User X ──┐
User Y ──┼── Beneficiary: AMAZON
User Z ──┘
```

Não devem existir registros separados de `AMAZON` para cada usuário.

---

# 17. Normalização de beneficiários

A identificação do Beneficiary deve ser case-insensitive.

Assim:

```text
AMAZON
Amazon
amazon
AmAzOn
```

devem resultar no mesmo `name_code`.

A normalização deve, no mínimo:

* remover espaços desnecessários no início e no fim;
* normalizar diferenças de capitalização;
* utilizar uma representação canônica para comparação.

Exemplo conceitual:

```text
name:
Amazon

name_code:
AMAZON
```

A forma armazenada em `name` pode permanecer amigável para apresentação.

A identificação lógica deve utilizar `name_code`.

---

# 18. Beneficiários diferentes

A normalização não deve remover informações que diferenciem entidades distintas.

Portanto:

```text
Amazon
Amazon.com
```

são beneficiários diferentes.

Consequentemente:

```text
AMAZON
AMAZON.COM
```

devem possuir `name_code` diferentes.

Da mesma forma:

```text
Empresa X
Empresa X LTDA
```

não devem ser considerados automaticamente o mesmo beneficiário.

O sistema não deve utilizar aproximação semântica para decidir que dois nomes representam a mesma entidade.

---

# 19. Tabela `receipts`

Representa o comprovante enviado pelo usuário.

### Colunas

| Coluna              | Tipo conceitual | Obrigatório | Regra                   |
| ------------------- | --------------- | ----------: | ----------------------- |
| `id`                | identifier      |         SIM | PK                      |
| `user_id`           | identifier      |         SIM | FK → users              |
| `file_reference`    | string          |         SIM | Referência no storage   |
| `file_name`         | string          |         SIM | Nome original           |
| `file_type`         | string          |         SIM | MIME/type               |
| `file_size`         | integer         |         SIM | Tamanho                 |
| `processing_status` | enum            |         SIM | Estado do processamento |
| `extracted_data`    | structured data |         NÃO | Dados extraídos         |
| `received_at`       | timestamp       |         SIM | Recebimento             |
| `created_at`        | timestamp       |         SIM | Criação                 |
| `updated_at`        | timestamp       |         SIM | Atualização             |
| `deleted_at`        | timestamp       |         NÃO | Soft delete             |

### Status

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
```

### Restrições

```text
PRIMARY KEY (id)

FOREIGN KEY (user_id)
REFERENCES users(id)
```

---

# 20. Arquivo do comprovante

O arquivo original não será armazenado diretamente na tabela `receipts`.

O banco armazenará uma referência:

```text
file_reference
```

Exemplo conceitual:

```text
receipts.file_reference
        ↓
Cloudflare R2
        ↓
arquivo PDF/JPG/PNG
```

Isso mantém o banco responsável por dados estruturados e o storage responsável pelos arquivos.

---

# 21. Dados extraídos do comprovante

`extracted_data` representa o resultado do processamento automático.

Pode conter:

```text
date
amount
beneficiary
source_institution
destination_institution
field_states
parser
```

Esses dados não representam necessariamente os valores definitivos do pagamento.

O formato estruturado exato será definido na implementação do processamento.

---

# 22. Armazenamento dos dados extraídos

Os dados extraídos pertencem ao contexto do `Receipt`.

Eles não devem ser transformados automaticamente em registros definitivos de:

* `Payment`;
* `Beneficiary`;
* `Institution`.

A criação ou associação definitiva acontece durante a confirmação do usuário.

Nesse momento:

```text
Receipt
   ↓
normalização
   ↓
resolve Beneficiary
   ↓
resolve Institution
   ↓
create Payment
```

---

# 23. Tabela `payments`

Representa pagamentos confirmados.

### Colunas

| Coluna                       | Tipo conceitual | Obrigatório | Regra              |
| ---------------------------- | --------------- | ----------: | ------------------ |
| `id`                         | identifier      |         SIM | PK                 |
| `user_id`                    | identifier      |         SIM | FK → users         |
| `receipt_id`                 | identifier      |         SIM | FK → receipts      |
| `beneficiary_id`             | identifier      |         SIM | FK → beneficiaries |
| `source_institution_id`      | identifier      |         SIM | FK → institutions  |
| `destination_institution_id` | identifier      |         NÃO | FK → institutions  |
| `amount`                     | monetary        |         SIM | Valor pago         |
| `payment_date`               | date            |         SIM | Data do pagamento  |
| `created_at`                 | timestamp       |         SIM | Registro           |
| `updated_at`                 | timestamp       |         SIM | Atualização        |
| `deleted_at`                 | timestamp       |         NÃO | Soft delete        |

### Restrições

```text
PRIMARY KEY (id)

FOREIGN KEY (user_id)
REFERENCES users(id)

FOREIGN KEY (receipt_id)
REFERENCES receipts(id)

FOREIGN KEY (beneficiary_id)
REFERENCES beneficiaries(id)

FOREIGN KEY (source_institution_id)
REFERENCES institutions(id)

FOREIGN KEY (destination_institution_id)
REFERENCES institutions(id)
```

---

# 24. Receipt → Payment

Um `Receipt` pode originar no máximo um `Payment`.

Portanto:

```text
UNIQUE (receipt_id)
```

deve existir em `payments`.

Relacionamento:

```text
Receipt
   │
   └──── 0..1 Payment
```

Isso impede que o mesmo comprovante seja confirmado duas vezes.

---

# 25. Payment → Beneficiary

Um pagamento possui exatamente um beneficiário.

```text
Payment
   │
   └──── 1 Beneficiary
```

Um beneficiário global pode possuir pagamentos de vários usuários:

```text
                ┌── Payment User A
                │
Beneficiary ────┼── Payment User B
                │
                └── Payment User C
```

O `Beneficiary` não possui `user_id`.

O isolamento dos pagamentos ocorre através de `payments.user_id`.

---

# 26. Payment → Institution

Um pagamento possui:

```text
source_institution_id
```

obrigatório.

E:

```text
destination_institution_id
```

opcional.

Relacionamento:

```text
Payment
 ├── 1 Source Institution
 └── 0..1 Destination Institution
```

A mesma tabela `institutions` representa ambos os papéis.

Uma Institution pode ser referenciada por Payments de diferentes usuários.

---

# 27. Payment → User

Todo pagamento pertence a exatamente um usuário.

```text
User
  │
  └──── N Payments
```

O `user_id` deve existir diretamente em `payments`.

Mesmo que o Receipt também possua `user_id`, o `Payment` mantém explicitamente seu proprietário.

Isso facilita:

* isolamento;
* autorização;
* consultas;
* índices;
* regras de segurança.

`Beneficiary` e `Institution` não possuem `user_id`, pois são entidades globais.

---

# 28. Integridade entre usuários

O isolamento por usuário aplica-se aos dados privados do sistema, especialmente:

```text
User
Receipt
Payment
```

`Beneficiary` e `Institution` são catálogos globais e, portanto, não são isolados por usuário.

Exemplo válido:

```text
User A
   ↓
Payment A
   ↓
Beneficiary: AMAZON
```

e:

```text
User B
   ↓
Payment B
   ↓
Beneficiary: AMAZON
```

Ambos podem referenciar o mesmo registro:

```text
beneficiaries.id = 123
```

O mesmo vale para instituições:

```text
User A → Payment A → Institution Itaú
User B → Payment B → Institution Itaú
```

O banco e a aplicação devem impedir apenas relacionamentos inválidos com dados que sejam efetivamente privados de outro usuário.

Por exemplo:

```text
Payment.user_id = User A

Payment.receipt_id = Receipt de User B
```

é inválido.

Já:

```text
Payment.user_id = User A

Payment.beneficiary_id = Beneficiary global
```

é válido.

---

# 29. Valor monetário

O valor de `payments.amount` deve utilizar representação decimal adequada para valores financeiros.

Não será utilizado `float` para armazenar valores monetários.

Conceitualmente:

```text
NUMERIC
```

Exemplo:

```text
387.42
```

O tipo e a precisão exatos serão definidos na migration.

---

# 30. Data do pagamento

`payment_date` representa somente a data em que o pagamento ocorreu.

Não deve ser utilizado timestamp quando a regra de negócio exigir apenas a data.

Exemplo:

```text
payment_date = 2026-09-12
```

Já:

```text
created_at = 2026-09-13T10:30:00
```

representa quando o registro foi criado.

---

# 31. Índices

Os principais índices esperados são:

### `users`

```text
username
email
status
```

### `receipts`

```text
user_id
processing_status
received_at
```

### `payments`

```text
user_id
payment_date
beneficiary_id
source_institution_id
destination_institution_id
```

### `beneficiaries`

```text
name_code
```

### `institutions`

```text
name_code
```

`name_code` deve possuir índice único nas entidades globais.

A necessidade de índices adicionais será avaliada após a implementação das consultas.

---

# 32. Consultas previstas

O modelo deve permitir consultas como:

### Quantidade de pagamentos no período

```text
COUNT(payments)
WHERE user_id = ?
AND payment_date BETWEEN ? AND ?
```

### Total pago no período

```text
SUM(payments.amount)
WHERE user_id = ?
AND payment_date BETWEEN ? AND ?
```

### Maior pagamento

```text
MAX(payments.amount)
WHERE user_id = ?
AND payment_date BETWEEN ? AND ?
```

### Pagamentos de um beneficiário

```text
WHERE user_id = ?
AND beneficiary_id = ?
```

### Total pago a um beneficiário

```text
SUM(payments.amount)
WHERE user_id = ?
AND beneficiary_id = ?
```

Essas consultas serão implementadas posteriormente pela API.

---

# 33. Relacionamento geral

O modelo principal fica:

```text
                    ┌───────────┐
                    │   roles   │
                    └─────┬─────┘
                          │
                          │ 1:N
                          ▼
                    ┌───────────┐
                    │   users   │
                    └─────┬─────┘
                          │
              ┌───────────┼────────────┐
              │           │            │
             1:1         1:1          1:N
              │           │            │
              ▼           ▼            ▼
        ┌──────────┐ ┌──────────────┐ ┌───────────┐
        │passwords │ │authentications│ │ receipts  │
        └──────────┘ └──────────────┘ └─────┬─────┘
                                            │
                                            │ 0:1
                                            ▼
                                      ┌───────────┐
                                      │ payments  │
                                      └──┬────┬───┘
                                         │    │
                         ┌───────────────┘    └───────────────┐
                         ▼                                    ▼
                  ┌─────────────┐                      ┌─────────────┐
                  │ beneficiaries│                     │ institutions│
                  │   GLOBAL     │                     │   GLOBAL    │
                  └─────────────┘                      └─────────────┘
```

Os catálogos globais podem ser utilizados por Payments pertencentes a diferentes usuários.

---

# 34. Modelo resumido das tabelas

```text
roles
 ├── id
 ├── name
 ├── name_code
 ├── description
 ├── created_at
 ├── updated_at
 └── deleted_at

users
 ├── id
 ├── role_id
 ├── name
 ├── username
 ├── email
 ├── status
 ├── date_of_birth
 ├── created_at
 ├── updated_at
 └── deleted_at

passwords
 ├── id
 ├── user_id
 ├── value
 ├── last_value
 ├── created_at
 ├── updated_at
 └── deleted_at

authentications
 ├── id
 ├── user_id
 ├── total
 ├── total_success
 ├── total_failures
 ├── failed_attempts
 ├── last_authenticated_at
 ├── created_at
 ├── updated_at
 └── deleted_at

institutions
 ├── id
 ├── name
 ├── name_code
 ├── created_at
 ├── updated_at
 └── deleted_at

beneficiaries
 ├── id
 ├── name
 ├── name_code
 ├── created_at
 ├── updated_at
 └── deleted_at

receipts
 ├── id
 ├── user_id
 ├── file_reference
 ├── file_name
 ├── file_type
 ├── file_size
 ├── processing_status
 ├── extracted_data
 ├── received_at
 ├── created_at
 ├── updated_at
 └── deleted_at

payments
 ├── id
 ├── user_id
 ├── receipt_id
 ├── beneficiary_id
 ├── source_institution_id
 ├── destination_institution_id
 ├── amount
 ├── payment_date
 ├── created_at
 ├── updated_at
 └── deleted_at
```

---

# 35. Regras de integridade

O banco deve garantir, diretamente ou através da combinação entre constraints e camada de domínio:

1. `users.role_id` deve referenciar um `roles` existente.
2. `passwords.user_id` deve referenciar um `users` existente.
3. Cada usuário possui no máximo uma credencial ativa.
4. `authentications.user_id` deve referenciar um `users` existente.
5. Cada usuário possui no máximo um registro de autenticação ativo.
6. `receipts.user_id` deve referenciar um `users` existente.
7. `payments.user_id` deve referenciar um `users` existente.
8. `payments.receipt_id` deve referenciar um `receipts` existente.
9. Um `receipt` pode originar no máximo um `payment`.
10. `payments.beneficiary_id` deve referenciar um `beneficiary` existente.
11. `payments.source_institution_id` deve referenciar uma `institution` existente.
12. `payments.destination_institution_id` pode ser `NULL`.
13. Um pagamento não pode possuir valor monetário `NULL`.
14. Um pagamento não pode possuir data `NULL`.
15. Um pagamento não pode possuir beneficiário `NULL`.
16. Um pagamento não pode possuir instituição de origem `NULL`.
17. Um Payment somente pode referenciar um Receipt pertencente ao mesmo usuário.
18. Beneficiaries são globais e podem ser utilizados por Payments de diferentes usuários.
19. Institutions são globais e podem ser utilizadas por Payments de diferentes usuários.
20. `beneficiaries.name_code` deve ser único entre os registros ativos.
21. `institutions.name_code` deve ser único entre os registros ativos.
22. Usuários não devem acessar Payments ou Receipts pertencentes a outros usuários.
23. Registros excluídos logicamente não devem participar das consultas normais.
24. Senhas nunca devem ser armazenadas em texto puro.
25. O mesmo comprovante não pode ser confirmado duas vezes.

---

# 36. Transação de confirmação

A confirmação de um comprovante deve ocorrer dentro de uma operação transacional.

Conceitualmente:

```text
User confirms
      ↓
BEGIN TRANSACTION
      ↓
validar Receipt e ownership
      ↓
normalizar Beneficiary
      ↓
obter/criar Beneficiary global
      ↓
normalizar Source Institution
      ↓
obter/criar Source Institution global
      ↓
normalizar Destination Institution
      ↓
obter/criar Destination Institution global
      ↓
criar Payment
      ↓
associar Payment ao Receipt
      ↓
COMMIT
```

Se qualquer etapa falhar:

```text
ROLLBACK
```

Nenhum pagamento parcialmente criado deve permanecer no banco.

A criação concorrente do mesmo `Beneficiary` ou `Institution` deve ser protegida pelas constraints de unicidade e pela transação.

---

# 37. Exclusão de usuário

A exclusão do usuário será lógica.

Exemplo:

```text
users.deleted_at = 2026-09-12T...
```

Os dados históricos relacionados não devem ser automaticamente destruídos.

A estratégia definitiva de retenção e anonimização será definida posteriormente.

---

# 38. Exclusão de comprovante

A exclusão lógica de um `Receipt` não deve permitir que seu `Payment` confirmado seja inadvertidamente perdido.

O relacionamento entre comprovante e pagamento deve preservar a integridade histórica.

A política definitiva de exclusão de comprovantes e seus arquivos será definida na documentação de segurança e armazenamento.

---

# 39. Exclusão de Beneficiary e Institution

`Beneficiary` e `Institution` são entidades globais.

A exclusão lógica dessas entidades deve considerar seus relacionamentos históricos com Payments.

Uma entidade global que possua referências históricas não deve ser fisicamente removida.

Caso deixe de ser utilizada para novos registros, sua exclusão lógica deve preservar as referências existentes.

O comportamento exato de exclusão e reutilização será definido nas migrations e regras de serviço.

---

# 40. Enums

Os principais valores controlados do banco são:

### User status

```text
ACTIVE
LOCKED
INACTIVE
```

### Receipt processing status

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
```

A estratégia exata de implementação desses enums no PostgreSQL será definida durante a criação das migrations.

---

# 41. O que não será armazenado no banco

Não serão armazenados diretamente no PostgreSQL:

* arquivo PDF;
* arquivo JPG;
* arquivo PNG;
* senha em texto puro;
* token de autenticação como regra do MVP;
* dados temporários de processamento que não tenham valor para o domínio.

Os arquivos ficarão no storage.

As senhas serão armazenadas somente como hashes.

---

# 42. Princípios do modelo de banco

### 42.1 Banco como fonte de dados persistentes

O PostgreSQL é a fonte oficial dos dados estruturados do sistema.

### 42.2 Storage separado

Arquivos não fazem parte do banco relacional.

### 42.3 Integridade

Relacionamentos importantes devem possuir chaves estrangeiras e restrições adequadas.

### 42.4 Segurança

Credenciais nunca são armazenadas em texto puro.

### 42.5 Isolamento

Os dados financeiros e documentos pertencem explicitamente a um usuário.

`Beneficiary` e `Institution` são exceções por serem catálogos globais compartilhados.

### 42.6 Histórico

Dados importantes não devem ser fisicamente removidos sem necessidade.

### 42.7 Simplicidade

O modelo deve possuir apenas as tabelas necessárias ao domínio atual.

Complexidade será adicionada somente quando existir uma necessidade real.

---

# 43. Estrutura final do MVP

O banco inicial possui oito tabelas principais:

```text
roles
users
passwords
authentications
institutions
beneficiaries
receipts
payments
```

Relacionamentos principais:

```text
roles
  │
  └── users
       ├── passwords
       ├── authentications
       ├── receipts
       └── payments
             ├── beneficiaries (global)
             ├── institutions (source/global)
             └── institutions (destination/global)

receipts
  └── payments
```

`Beneficiaries` e `Institutions` são catálogos globais.

Exemplo:

```text
                  ┌──────────────┐
User A ──Payment──┤              │
                  │  Beneficiary │
User B ──Payment──┤    AMAZON    │
                  │              │
User C ──Payment──┤              │
                  └──────────────┘
```

E:

```text
                  ┌──────────────┐
User A ──Payment──┤              │
                  │  Institution │
User B ──Payment──┤    ITAÚ      │
                  │              │
User C ──Payment──┤              │
                  └──────────────┘
```

Este modelo representa o domínio atual sem introduzir tabelas de sessão, tentativas individuais de login, auditoria avançada ou outros mecanismos que não fazem parte do MVP.
