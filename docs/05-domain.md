# Comprovante — Modelo de domínio

## 1. Objetivo

Este documento define o modelo conceitual do domínio do Comprovante, suas entidades, responsabilidades, estados e regras de negócio.

O documento não define implementação específica de banco de dados, SQLAlchemy, endpoints, infraestrutura ou detalhes de UI.

O domínio é dividido principalmente em:

* autenticação e usuários;
* comprovantes;
* pagamentos;
* beneficiários;
* instituições.

---

# 2. Principais conceitos

As principais entidades do domínio são:

* `User`
* `Role`
* `Password`
* `Authentication`
* `Receipt`
* `Payment`
* `Beneficiary`
* `Institution`

Relacionamentos conceituais:

```text
User
 ├── Role
 ├── Password
 ├── Authentication
 ├── Receipt
 │    └── Payment
 └── Payment
      ├── Beneficiary
      ├── Source Institution
      └── Destination Institution
```

---

# 3. User

`User` representa o usuário da aplicação.

É o proprietário dos comprovantes e pagamentos registrados.

### Dados conceituais

* `id`
* `role_id`
* `name`
* `username`
* `email`
* `status`
* `date_of_birth`
* `created_at`
* `updated_at`
* `deleted_at`

### Status

Os estados possíveis são:

* `ACTIVE`
* `LOCKED`
* `INACTIVE`

### Significado

**ACTIVE**

Usuário habilitado para utilizar a aplicação normalmente.

**LOCKED**

Usuário temporariamente bloqueado em consequência de falhas consecutivas de autenticação.

**INACTIVE**

Usuário desativado e sem acesso à aplicação.

A desativação pode ocorrer por decisão administrativa ou por uma regra de negócio que determine a inativação da conta.

### Regras

* `username` deve identificar unicamente o usuário.
* `email` deve identificar unicamente o usuário.
* Usuário `LOCKED` ou `INACTIVE` não pode realizar autenticação normal.
* Usuário removido logicamente não deve ser autenticado.
* Todo `Receipt` pertence a um único `User`.
* Todo `Payment` pertence a um único `User`.

---

# 4. Role

`Role` representa o perfil de acesso do usuário.

### Dados conceituais

* `id`
* `name`
* `name_code`
* `description`
* `created_at`
* `updated_at`
* `deleted_at`

### Exemplos

```text
USER
ADMIN
```

O modelo permite adicionar novos perfis posteriormente sem alterar a estrutura de `User`.

No MVP, a aplicação pode possuir apenas o perfil necessário para o usuário comum e um perfil administrativo caso seja necessário.

---

# 5. Password

`Password` representa as credenciais de autenticação do usuário.

### Dados conceituais

* `id`
* `user_id`
* `value`
* `last_value`
* `created_at`
* `updated_at`
* `deleted_at`

### Regra de segurança

`value` **não representa a senha original**.

O sistema nunca deve armazenar a senha em texto puro.

Os valores armazenados devem representar hashes seguros das senhas.

```text
senha informada
      ↓
algoritmo de hash
      ↓
Password.value
```

### Última senha

`last_value` representa o hash da senha anterior.

Seu objetivo é permitir uma regra de não reutilização de senha.

Exemplo:

```text
Senha atual:       hash(A)
Senha anterior:    hash(B)

Usuário tenta trocar para B
          ↓
comparação com last_value
          ↓
rejeitada
```

A quantidade de senhas anteriores armazenadas pode ser expandida futuramente caso seja necessário implementar histórico de senhas.

---

# 6. Authentication

`Authentication` representa o estado e o histórico resumido das autenticações do usuário.

### Dados conceituais

* `id`
* `user_id`
* `total`
* `total_success`
* `total_failures`
* `failed_attempts`
* `last_authenticated_at`
* `created_at`
* `updated_at`
* `deleted_at`

### Significado

`total`

Quantidade total de tentativas de autenticação.

`total_success`

Quantidade de autenticações realizadas com sucesso.

`total_failures`

Quantidade total de autenticações que falharam.

`failed_attempts`

Quantidade de falhas consecutivas desde a última autenticação bem-sucedida.

`last_authenticated_at`

Data/hora da última autenticação bem-sucedida.

### Exemplo

```text
total = 8
total_success = 5
total_failures = 3
failed_attempts = 2
```

Isso significa que o usuário possui oito tentativas no histórico, cinco bem-sucedidas e três falhas, sendo duas falhas consecutivas desde o último login válido.

---

# 7. Bloqueio por falhas de autenticação

O domínio deve permitir o bloqueio automático do usuário após uma quantidade determinada de falhas consecutivas.

Exemplo conceitual:

```text
LOGIN
  ↓
senha incorreta
  ↓
failed_attempts++
  ↓
atingiu limite?
  ├── NÃO → autenticação falhou
  └── SIM → User.status = LOCKED
```

Após autenticação bem-sucedida:

```text
failed_attempts = 0
total_success++
last_authenticated_at = agora
```

O número máximo de tentativas não deve ser definido diretamente na entidade `User`.

Essa regra pertence à política de autenticação e será definida posteriormente na implementação.

---

# 8. Estados LOCKED e INACTIVE

Os estados possuem responsabilidades diferentes.

### LOCKED

Representa um bloqueio temporário relacionado à segurança da autenticação.

Exemplo:

```text
5 senhas incorretas
        ↓
User.status = LOCKED
```

O bloqueio pode possuir uma regra de desbloqueio posteriormente.

Após o desbloqueio:

```text
LOCKED
   ↓
desbloqueio
   ↓
ACTIVE
```

### INACTIVE

Representa uma conta que não está habilitada para utilização.

Exemplo:

```text
ação administrativa
        ↓
User.status = INACTIVE
```

O usuário não consegue autenticar enquanto permanecer nesse estado.

Caso a conta seja reativada:

```text
INACTIVE
   ↓
reativação
   ↓
ACTIVE
```

`LOCKED` e `INACTIVE` não são equivalentes:

* `LOCKED` representa uma condição de segurança temporária;
* `INACTIVE` representa a desativação da conta.

---

# 9. Autenticação

A autenticação possui o seguinte fluxo conceitual:

```text
credential + password
        ↓
localizar User
        ↓
validar status
        ↓
recuperar Password
        ↓
comparar senha com hash
        ↓
┌───────────────┴───────────────┐
│                               │
válida                        inválida
│                               │
↓                               ↓
sucesso                     registrar falha
│                               │
↓                               ↓
gerar token                 incrementar
                            failed_attempts
│                               │
↓                          atingiu limite?
retornar token                    │
                              ┌───┴───┐
                              │       │
                             não      sim
                              │       │
                              ↓       ↓
                           falha    LOCKED
```

O sistema nunca deve retornar ao cliente informações que permitam descobrir se o usuário existe ou se apenas a senha está incorreta.

---

# 10. Token

Após uma autenticação bem-sucedida, o backend gera um token de autenticação.

O token representa a identidade autenticada do usuário.

O domínio não depende de uma implementação específica de token.

A tecnologia utilizada para geração, assinatura, expiração e validação do token será definida posteriormente na documentação técnica.

---

# 11. Endpoint `register`

O `register` representa o cadastro de um novo usuário.

Responsabilidades conceituais:

* validar os dados de cadastro;
* verificar unicidade de `username`;
* verificar unicidade de `email`;
* criar o usuário;
* definir seu perfil;
* criar sua credencial;
* armazenar somente o hash da senha;
* inicializar os dados de autenticação.

O cadastro não deve criar `Receipt` ou `Payment`.

---

# 12. Endpoint `login`

O `login` representa a autenticação do usuário.

Entrada conceitual:

```text
credential
password
```

`credential` pode representar o identificador utilizado para localizar o usuário, por exemplo:

```text
username
```

ou

```text
email
```

O serviço:

1. localiza o usuário;
2. verifica o status;
3. valida a senha;
4. registra sucesso ou falha;
5. atualiza os dados de `Authentication`;
6. aplica a política de bloqueio quando necessário;
7. gera o token quando a autenticação é válida.

---

# 13. Endpoint `me`

O `me` retorna as informações do usuário autenticado.

O identificador do usuário não deve ser recebido pelo cliente como parâmetro para determinar quem será consultado.

O fluxo é:

```text
Request
   ↓
Token
   ↓
validação do token
   ↓
user_id
   ↓
User
   ↓
dados tratados
   ↓
Response
```

O serviço utiliza a identidade presente no token para localizar o usuário.

O endpoint pode retornar informações apropriadas para o contexto da aplicação, por exemplo:

```text
id
name
username
email
role
status
```

Informações sensíveis de autenticação não devem ser retornadas.

---

# 14. Endpoints de autenticação do MVP

O domínio de autenticação inicialmente possui apenas três operações públicas:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Não será criado endpoint específico de logout no MVP.

A necessidade de logout, revogação de tokens ou gerenciamento avançado de sessões poderá ser avaliada posteriormente.

---

# 15. Receipt

`Receipt` representa o documento enviado pelo usuário.

O comprovante é a origem dos dados de um possível pagamento.

Ele não representa, por si só, um pagamento confirmado.

### Dados conceituais

* `id`
* `user`
* `original file`
* `type/format`
* `receivedAt`
* `processing state`
* `extracted information`
* `reference to confirmed payment`

---

# 16. Receipt vs Payment

São conceitos diferentes.

### Receipt

Representa:

> “O usuário enviou este documento.”

### Payment

Representa:

> “O usuário confirmou que este pagamento ocorreu.”

Portanto:

```text
Upload
  ↓
Receipt
  ↓
Processing
  ↓
Candidate data
  ↓
User review
  ↓
Confirmation
  ↓
Payment
```

O upload de um comprovante nunca deve criar automaticamente um pagamento confirmado.

---

# 17. Receipt states

Os estados do comprovante são:

* `RECEIVED`
* `PROCESSING`
* `PROCESSED`
* `FAILED`

### RECEIVED

Arquivo recebido e validado.

### PROCESSING

Documento sendo processado.

### PROCESSED

Processamento concluído e dados candidatos disponíveis para revisão.

`PROCESSED` não significa que o pagamento foi confirmado.

### FAILED

Não foi possível processar o documento adequadamente.

---

# 18. Payment

`Payment` representa um pagamento confirmado pelo usuário.

### Dados conceituais

* `id`
* `owner user`
* `payment date`
* `beneficiary`
* `amount`
* `source institution`
* `destination institution`
* `source receipt`
* `createdAt`

---

# 19. Confirmation

Um `Payment` somente pode existir após confirmação explícita do usuário.

Nem:

* parser;
* OCR;
* IA;
* processamento do documento

pode confirmar automaticamente um pagamento.

A autoridade final é sempre o usuário.

```text
Extração automática
        ↓
Dados candidatos
        ↓
Revisão do usuário
        ↓
Correção
        ↓
Confirmação
        ↓
Payment
```

---

# 20. Beneficiary

`Beneficiary` representa a pessoa ou instituição que recebeu o pagamento.

O nome extraído do comprovante pode ser diferente do nome utilizado pelo usuário.

Exemplo:

```text
Extraído:
NEOENERGIA DISTRIBUIÇÃO BRASÍLIA

Confirmado:
Neoenergia
```

O valor confirmado será utilizado nas consultas posteriores.

---

# 21. Extracted vs Confirmed Beneficiary

O sistema deve distinguir:

```text
valor extraído
```

de

```text
valor confirmado
```

O valor extraído representa a interpretação automática do documento.

O valor confirmado representa a informação validada pelo usuário.

---

# 22. Institution

`Institution` representa uma instituição financeira identificada no comprovante.

Exemplos:

* Itaú
* Nubank
* Banco do Brasil
* Caixa

Uma instituição pode atuar como origem ou destino do dinheiro.

---

# 23. Source Institution

Representa a instituição de onde o dinheiro saiu.

Exemplo:

```text
Itaú → Neoenergia
```

Nesse caso:

```text
source_institution = Itaú
```

---

# 24. Destination Institution

Representa a instituição para a qual o dinheiro foi enviado.

Essa informação pode não existir ou não ser identificada no comprovante.

Portanto:

```text
destination_institution = null
```

é um estado válido.

---

# 25. Institution Normalization

O sistema deve evitar que diferentes representações da mesma instituição criem entidades distintas.

Exemplo:

```text
ITAÚ UNIBANCO S.A.
ITAU UNIBANCO
BANCO ITAÚ
ITAÚ
```

devem ser normalizados para:

```text
Itaú
```

Da mesma forma:

```text
NU PAGAMENTOS S.A.
NUBANK
```

devem representar:

```text
Nubank
```

O valor original extraído pode ser preservado separadamente do valor normalizado.

---

# 26. Amount

`Amount` representa o valor efetivamente pago.

O domínio deve tratar o valor monetário sem utilizar representação inadequada que provoque problemas de precisão.

A representação técnica exata será definida no modelo de persistência.

---

# 27. Payment Date

A data do pagamento representa a data em que a transação ocorreu.

Ela é diferente da data de criação do registro.

Exemplo:

```text
payment_date = 12/09/2026
created_at   = 13/09/2026
```

O pagamento pode ter ocorrido antes de seu registro no sistema.

---

# 28. Receipt → Payment

Um comprovante pode gerar no máximo um pagamento confirmado.

```text
Receipt
   |
   └── 0..1 Payment
```

Portanto:

* um comprovante pode ainda não ter pagamento;
* um comprovante pode possuir um pagamento confirmado;
* o mesmo comprovante não pode gerar dois pagamentos confirmados.

---

# 29. ExtractedPaymentData

O processamento produz dados candidatos:

* date;
* amount;
* beneficiary;
* source institution;
* destination institution.

Esses dados não são definitivos até a confirmação do usuário.

---

# 30. Origin of Extracted Data

A origem dos dados segue a estratégia tecnológica definida:

```text
PDF text
   ↓
deterministic parser
   ↓
resultado suficiente?
   ├── SIM → revisão
   └── NÃO → AI fallback
                  ↓
                revisão
```

Independentemente da origem, os dados sempre passam pela revisão do usuário.

---

# 31. Field States

Cada campo extraído pode possuir um estado:

* `FOUND`
* `NOT_FOUND`
* `AMBIGUOUS`

### FOUND

Informação identificada com confiança suficiente.

### NOT_FOUND

Informação não encontrada.

### AMBIGUOUS

Existem múltiplas interpretações possíveis ou a informação não possui confiança suficiente.

---

# 32. Required Fields

Para considerar o processamento suficiente para apresentação ao usuário, os campos obrigatórios são:

* date;
* amount;
* beneficiary;
* source institution.

`destination institution` pode permanecer ausente.

Exemplo válido:

```text
date = FOUND
amount = FOUND
beneficiary = FOUND
sourceInstitution = FOUND
destinationInstitution = NOT_FOUND
```

Esse resultado pode seguir diretamente para revisão.

---

# 33. User Correction

O usuário pode alterar qualquer informação extraída antes da confirmação:

* date;
* amount;
* beneficiary;
* source institution;
* destination institution.

Após a confirmação, os valores passam a representar os dados definitivos do `Payment`.

---

# 34. Authority Rule

A cadeia de autoridade do sistema é:

```text
Documento
   ↓
Extração automática
   ↓
Dados candidatos
   ↓
Correção do usuário
   ↓
Dados confirmados
```

Dados confirmados pelo usuário não devem ser sobrescritos posteriormente por uma nova interpretação automática do documento.

---

# 35. Domain Queries

O domínio deve permitir:

1. quantidade de pagamentos por período;
2. valor total pago por período;
3. maior pagamento por período;
4. pesquisa por beneficiário;
5. valor pago a um beneficiário por mês;
6. valor pago a um beneficiário por ano;
7. valor pago a um beneficiário em determinado período.

---

# 36. Data Isolation

Todos os recursos do sistema pertencem a um usuário.

O backend deve garantir que um usuário somente consiga acessar:

* seus próprios `Receipt`;
* seus próprios `Payment`;
* seus próprios dados de autenticação;
* seus próprios dados relacionados.

A identidade utilizada para essa autorização deve ser obtida do contexto autenticado, e não confiada a um `user_id` enviado livremente pelo cliente.

---

# 37. Integrity Rules

As principais regras de integridade do domínio são:

1. `User` pode possuir um `Role`.
2. `User` possui suas credenciais de autenticação.
3. `User` possui seu estado de autenticação.
4. `Password` nunca armazena senha em texto puro.
5. `Payment` pertence exatamente a um `User`.
6. `Receipt` pertence exatamente a um `User`.
7. `Payment` deve possuir um `Receipt` de origem.
8. `Receipt` possui zero ou um `Payment` confirmado.
9. `Payment` somente existe após confirmação.
10. `Payment` deve possuir data.
11. `Payment` deve possuir valor.
12. `Payment` deve possuir beneficiário.
13. `Payment` deve possuir instituição de origem.
14. Instituição de destino pode ser nula.
15. Usuário somente acessa seus próprios recursos.
16. Dados confirmados pelo usuário não podem ser sobrescritos automaticamente.
17. Usuário `LOCKED` ou `INACTIVE` não pode autenticar normalmente.
18. Falhas consecutivas de autenticação podem provocar `LOCKED`.
19. `failed_attempts` deve ser zerado após autenticação bem-sucedida.

---

# 38. Domain Flow

O fluxo completo do domínio é:

```text
                    AUTENTICAÇÃO

Register
   ↓
User + Password + Authentication
   ↓
Login
   ↓
Token
   ↓
Me


                    COMPROVANTE

Upload
   ↓
Receipt
   ↓
Processing
   ↓
Candidate data
   ↓
User review
   ↓
Correction
   ↓
Confirmation
   ↓
Payment
   ↓
Queries
```

---

# 39. Out of Scope

O domínio não contempla neste momento:

* saldo bancário;
* contas bancárias completas;
* orçamento;
* categorias financeiras;
* cartão de crédito;
* investimentos;
* patrimônio;
* conciliação bancária;
* Open Finance;
* integração direta com bancos;
* realização de pagamentos;
* pagamentos compartilhados entre usuários;
* pagamentos recorrentes automáticos;
* gerenciamento avançado de sessões;
* múltiplos níveis complexos de autorização.

O foco permanece:

> registrar e consultar pagamentos a partir de comprovantes enviados pelo usuário.

---

# 40. Princípios do domínio

### Princípio 1 — Identidade

O usuário autenticado é a autoridade sobre seus próprios recursos.

### Princípio 2 — Segurança

Credenciais nunca são armazenadas em texto puro.

### Princípio 3 — Separação

`Receipt` é documento/evidência.

`Payment` é registro financeiro confirmado.

### Princípio 4 — Extração não é confirmação

Processamento automático produz uma sugestão.

Somente o usuário confirma.

### Princípio 5 — Simplicidade

O domínio de autenticação do MVP possui apenas as operações necessárias:

```text
register
login
me
```

### Princípio 6 — Evolução

O modelo permite adicionar posteriormente:

* recuperação de senha;
* alteração de senha;
* histórico de senhas;
* revogação de sessões;
* refresh tokens;
* autenticação multifator;
* permissões mais granulares;
* auditoria detalhada.

Esses recursos não fazem parte do MVP atual.
