# 09 — Domain Contracts

## 1. Objetivo

Este documento define os contratos de negócio dos aggregates da aplicação Comprovante.

O objetivo é estabelecer:

* responsabilidade de cada aggregate;
* Aggregate Root;
* entidades pertencentes ao aggregate;
* operações permitidas;
* regras de negócio;
* relacionamentos entre aggregates;
* limites de responsabilidade;
* regras de consistência.

Este documento não define detalhes de persistência, SQLAlchemy ou estrutura de banco de dados. Essas responsabilidades pertencem ao `06-database.md`.

---

# 2. Aggregates

A aplicação possui os seguintes aggregates:

```text
domain/
├── auth/
├── receipt/
├── payment/
├── beneficiary/
└── institution/
```

Cada aggregate possui uma responsabilidade de negócio específica.

| Aggregate   | Aggregate Root | Escopo  | Responsabilidade                                          |
| ----------- | -------------- | ------- | --------------------------------------------------------- |
| Auth        | User           | Usuário | Identidade, autenticação e controle de acesso             |
| Receipt     | Receipt        | Usuário | Recebimento, processamento e interpretação do comprovante |
| Payment     | Payment        | Usuário | Registro do fato financeiro confirmado                    |
| Beneficiary | Beneficiary    | Global  | Identificação e reutilização de beneficiários             |
| Institution | Institution    | Global  | Identificação e reutilização de instituições financeiras  |

`Beneficiary` e `Institution` são aggregates globais.

Eles não pertencem a um usuário específico e podem ser utilizados por diferentes usuários.

---

# 3. Auth

## 3.1 Aggregate Root

```text
User
```

O `User` é o Aggregate Root do aggregate de autenticação.

O aggregate contém:

```text
User
├── Role
├── Password
└── Authentication
```

Essas entidades não possuem significado de negócio independente dentro da aplicação.

---

## 3.2 Responsabilidade

O aggregate `Auth` é responsável por:

* cadastro de usuários;
* autenticação;
* validação de credenciais;
* controle de status do usuário;
* controle de tentativas de autenticação;
* bloqueio de usuários;
* identificação do usuário autenticado;
* controle de role;
* desbloqueio administrativo.

---

## 3.3 Operações

### Registrar usuário

```text
register()
```

Responsável por criar um novo usuário.

Regras:

* username deve ser único;
* email deve ser único;
* senha deve ser armazenada somente como hash;
* o usuário recebe o role padrão do sistema;
* o usuário não pode escolher o próprio role;
* o usuário inicia com status `ACTIVE`;
* os dados de autenticação são inicializados.

O role utilizado no cadastro é definido pelo backend.

---

### Autenticar usuário

```text
authenticate()
```

A autenticação pode utilizar:

```text
username
ou
email
```

Regras:

* usuário `ACTIVE` pode autenticar;
* usuário `INACTIVE` não pode autenticar;
* usuário `LOCKED` não pode autenticar;
* credencial inválida incrementa `failed_attempts`;
* ao atingir 3 falhas consecutivas, o usuário passa para `LOCKED`;
* autenticação válida zera `failed_attempts`;
* autenticação válida incrementa `total_success`;
* falha de autenticação incrementa `total_failures`;
* toda tentativa incrementa `total`;
* autenticação válida atualiza `last_authenticated_at`.

---

## 3.4 Regra de LOCKED

O limite de tentativas consecutivas é:

```text
3
```

Ao atingir três falhas consecutivas:

```text
ACTIVE
  ↓
LOCKED
```

O usuário não poderá realizar login enquanto estiver `LOCKED`.

O desbloqueio, neste momento, é exclusivamente administrativo.

```text
ADM
 ↓
unlock user
 ↓
ACTIVE
```

O desbloqueio não é disponibilizado ao próprio usuário no MVP.

---

## 3.5 Regra de INACTIVE

Usuários com:

```text
status = INACTIVE
```

não podem realizar autenticação.

`INACTIVE` é diferente de `LOCKED`:

```text
INACTIVE
→ usuário desativado

LOCKED
→ usuário bloqueado por falhas de autenticação
```

---

## 3.6 Role

O usuário não escolhe seu próprio role durante o cadastro.

A definição do role é responsabilidade do backend.

Exemplo:

```text
register()
   ↓
User
   ↓
Role padrão
```

A alteração de role não faz parte das operações públicas do MVP.

---

# 4. Receipt

## 4.1 Aggregate Root

```text
Receipt
```

O `Receipt` representa o comprovante original enviado pelo usuário.

Ele é a evidência documental utilizada para produzir um Payment.

---

## 4.2 Responsabilidade

O aggregate `Receipt` é responsável por:

* receber o arquivo;
* preservar o arquivo original;
* validar o arquivo;
* controlar o processamento;
* extrair informações;
* armazenar os dados extraídos;
* permitir correção dos dados extraídos;
* disponibilizar os dados para confirmação;
* iniciar a criação do Payment através da confirmação.

---

## 4.3 Lifecycle

O processamento possui os seguintes estados:

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

Um Receipt `FAILED` pode voltar para processamento:

```text
FAILED
   ↓
PROCESSING
```

Um Receipt `PROCESSED` não pode ser processado novamente.

---

## 4.4 Reenvio do mesmo arquivo

O mesmo arquivo não pode ser enviado novamente.

Quando o sistema identificar que o arquivo já foi recebido, a nova tentativa deve resultar em erro.

A identificação do arquivo duplicado deve ser baseada em uma representação determinística do conteúdo do arquivo, e não somente no nome.

O nome:

```text
comprovante.pdf
```

não é suficiente para determinar duplicidade.

---

## 4.5 Dados obrigatórios

Para que um Receipt possa ser confirmado, os seguintes dados devem estar disponíveis:

```text
payment_date
amount
beneficiary
source_institution
```

A instituição de destino é opcional:

```text
destination_institution = null
```

Caso algum campo obrigatório esteja ausente ou inválido, a confirmação deve ser recusada.

---

## 4.6 Correção dos dados

Os dados extraídos não são considerados definitivos.

O usuário pode corrigir os dados antes da confirmação.

Exemplo:

```text
Comprovante
    ↓
Extração
    ↓
Dados encontrados
    ↓
Usuário corrige
    ↓
Confirmação
```

A confirmação utiliza os dados finais apresentados pelo usuário.

---

## 4.7 Confirmação

A confirmação é uma operação de negócio, e não um estado adicional do processamento.

Não existe:

```text
CONFIRMED
```

em `Receipt.processing_status`.

A confirmação representa:

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
```

Depois da confirmação, o Receipt permanece como documento/evidência original e passa a possuir uma associação com o Payment criado.

A relação é:

```text
Receipt 1 ───── 0..1 Payment
```

---

## 4.8 Regra de confirmação

Um Receipt somente pode ser confirmado quando:

* pertence ao usuário autenticado;
* está em estado `PROCESSED`;
* possui todos os campos obrigatórios;
* os dados possuem formato válido;
* ainda não possui Payment associado.

A confirmação deve ser idempotente.

---

# 5. Payment

## 5.1 Aggregate Root

```text
Payment
```

O `Payment` representa o fato financeiro confirmado.

Ele não representa o processamento do documento.

A distinção fundamental é:

```text
Receipt
= evidência documental

Payment
= fato financeiro confirmado
```

---

## 5.2 Responsabilidade

O aggregate `Payment` é responsável por representar:

* valor pago;
* data do pagamento;
* beneficiário;
* instituição de origem;
* instituição de destino;
* usuário proprietário do registro;
* comprovante que originou o pagamento.

---

## 5.3 Criação

O Payment não é criado diretamente pelo usuário através de um endpoint próprio.

Ele é criado como consequência da confirmação de um Receipt:

```text
POST /receipts/{receipt_id}/confirm
```

Fluxo:

```text
Receipt
   ↓
validar
   ↓
obter/criar Beneficiary
   ↓
obter/criar Institution
   ↓
criar Payment
   ↓
associar Receipt
   ↓
commit
```

A operação deve ocorrer dentro de uma única transação.

---

## 5.4 Imutabilidade

Payment é imutável no MVP.

Depois de confirmado:

```text
Payment
   ↓
não pode ser alterado
```

Não existem operações públicas de:

```text
POST /payments
PUT /payments/{id}
PATCH /payments/{id}
DELETE /payments/{id}
```

A alteração dos dados deve acontecer no Receipt antes da confirmação.

---

## 5.5 Integridade

Um Payment deve:

* pertencer a um usuário;
* possuir um beneficiário;
* possuir uma instituição de origem;
* possuir data;
* possuir valor;
* possuir o Receipt que originou sua criação;
* possuir instituição de destino somente quando identificada.

O valor deve utilizar representação decimal, nunca `float`.

---

# 6. Beneficiary

## 6.1 Aggregate Root

```text
Beneficiary
```

O Beneficiary representa uma entidade para a qual pagamentos podem ser realizados.

---

## 6.2 Escopo

O Beneficiary é um aggregate **global**.

Ele não pertence a um usuário específico.

Um único Beneficiary pode ser utilizado por vários usuários.

Exemplo:

```text
User A ──┐
         │
User B ──┼── AMAZON
         │
User C ──┘
```

Existe somente um Beneficiary correspondente a `AMAZON`.

O usuário que provocou a criação do Beneficiary não se torna proprietário da entidade.

---

## 6.3 Responsabilidade

O aggregate é responsável por:

* identificar beneficiários;
* normalizar nomes;
* evitar duplicação lógica;
* permitir reutilização de um beneficiário;
* fornecer uma referência estável para Payments.

---

## 6.4 Normalização

A identificação do Beneficiary deve ser case-insensitive.

Assim:

```text
AMAZON
Amazon
amazon
AmAzOn
```

representam o mesmo Beneficiary.

A normalização deve, no mínimo:

* remover espaços desnecessários no início e no fim;
* normalizar diferenças de capitalização;
* utilizar uma representação canônica para comparação.

A forma apresentada ao usuário pode permanecer em uma representação amigável, mas a identificação deve utilizar o valor normalizado.

---

## 6.5 Beneficiários diferentes

A normalização não deve remover informações que diferenciem entidades distintas.

Portanto:

```text
Amazon
Amazon.com
```

são Beneficiaries diferentes.

Da mesma forma:

```text
Empresa X
Empresa X LTDA
```

não devem ser considerados automaticamente o mesmo beneficiário.

O sistema não deve utilizar aproximação semântica para decidir que dois nomes representam a mesma entidade.

---

## 6.6 Criação e reutilização

O Beneficiary é criado ou reutilizado durante a confirmação do Receipt.

Fluxo:

```text
nome extraído/corrigido
        ↓
normalização
        ↓
buscar Beneficiary global
        ↓
┌───────────────┐
│ encontrado?   │
└───────┬───────┘
        │
    sim │ não
        ↓
    reutiliza
          ou
        cria
```

Não existe criação manual pública no MVP.

---

# 7. Institution

## 7.1 Aggregate Root

```text
Institution
```

O aggregate representa uma instituição financeira normalizada.

Exemplos:

```text
Itaú
Nubank
Bradesco
Caixa
Santander
```

---

## 7.2 Escopo

A Institution é um aggregate **global**.

Ela não pertence a um usuário específico.

Uma única Institution pode ser utilizada por vários usuários.

Exemplo:

```text
User X ──┐
         │
User Y ──┼── Itaú
         │
User Z ──┘
```

Se o usuário X for o primeiro a utilizar o Itaú, o sistema pode criar a Institution.

A Institution criada não pertence ao usuário X.

Quando o usuário Y utilizar o Itaú, o sistema deve reutilizar a mesma Institution.

Portanto:

```text
User X
   ↓
cria/resolve Itaú
   ↓
Institution global

User Y
   ↓
resolve Itaú
   ↓
reutiliza a mesma Institution
```

---

## 7.3 Responsabilidade

O aggregate é responsável por:

* identificar instituições;
* normalizar instituições;
* evitar duplicação de instituições equivalentes;
* fornecer uma referência consistente para Receipts e Payments;
* permitir reutilização da instituição por qualquer usuário.

---

## 7.4 Normalização

A aplicação não deve tratar diferentes representações da mesma instituição como instituições distintas quando houver informação suficiente para determinar que representam a mesma instituição.

Exemplo:

```text
Itaú
Itau
ITAU
Banco Itaú
Itaú Unibanco
```

devem ser resolvidos para uma única Institution canônica quando representarem a mesma instituição financeira.

A identificação deve utilizar um código estável:

```text
name
name_code
```

O `name_code` deve ser único globalmente.

Exemplo:

```text
name      = Itaú
name_code = ITAU
```

---

## 7.5 Criação e reutilização

A Institution é criada ou reutilizada durante o processamento/confirmação do Receipt.

Fluxo:

```text
instituição extraída/corrigida
          ↓
      normalização
          ↓
   buscar Institution global
          ↓
    ┌───────────────┐
    │ encontrada?   │
    └───────┬───────┘
            │
        sim │ não
            ↓
        reutiliza
              ou
            cria
```

A criação de uma Institution não estabelece qualquer vínculo de propriedade com o usuário que provocou sua criação.

---

## 7.6 Instituições diferentes

A normalização deve evitar duplicações da mesma instituição, mas não deve unir instituições diferentes.

Exemplo:

```text
Itaú
Nubank
```

são Institutions distintas.

O sistema não deve utilizar aproximação semântica para determinar que duas instituições diferentes são a mesma instituição.

---

## 7.7 Manutenção

Institutions não possuem CRUD público no MVP.

A aplicação utiliza as instituições durante:

* processamento de Receipt;
* interpretação do comprovante;
* confirmação do Payment.

A manutenção da base de instituições é responsabilidade interna do sistema.

---

# 8. Relacionamento entre Aggregates

Os aggregates possuem as seguintes relações:

```text
                    ┌───────────┐
                    │   Auth    │
                    │   User    │
                    └─────┬─────┘
                          │
                          │ owner
                          ├───────────────────┐
                          ↓                   │
                    ┌───────────┐             │
                    │  Receipt  │             │
                    └─────┬─────┘             │
                          │                   │
                     confirm                  │
                          │                   │
                          ↓                   │
                    ┌───────────┐             │
                    │  Payment  │◄────────────┘
                    └──┬────┬───┘
                       │    │
             ┌─────────┘    └──────────┐
             ↓                         ↓
      ┌─────────────┐           ┌─────────────┐
      │ Beneficiary │           │ Institution │
      │   GLOBAL    │           │   GLOBAL    │
      └─────────────┘           └─────────────┘
```

O Payment referencia:

```text
Receipt
Beneficiary
Institution (source)
Institution (destination)
User
```

`Beneficiary` e `Institution` são referências globais.

O `User` não possui uma cópia particular dessas entidades.

---

# 9. Limites de responsabilidade

## Auth

Responsável por:

```text
identidade
autenticação
status
roles
bloqueio
```

Não é responsável por:

```text
Receipt
Payment
Beneficiary
Institution
```

---

## Receipt

Responsável por:

```text
arquivo
processamento
extração
dados extraídos
confirmação
```

Não é responsável por manter regras próprias de Payment.

---

## Payment

Responsável por:

```text
fato financeiro confirmado
```

Não é responsável por:

```text
processamento de arquivo
OCR
extração
autenticação
```

---

## Beneficiary

Responsável por:

```text
identificação global
normalização
reutilização
```

Não é responsável por:

```text
pagamento
usuário
comprovante
```

---

## Institution

Responsável por:

```text
identificação global
normalização
reutilização
```

Não é responsável por:

```text
processamento de comprovante
pagamento
autenticação
```

---

# 10. Regras de consistência entre Aggregates

Os aggregates não devem manipular diretamente o estado interno uns dos outros.

A interação ocorre através de operações explícitas.

Exemplo:

```text
Receipt
   ↓
confirm
   ↓
resolve Beneficiary
   ↓
resolve Institution
   ↓
create Payment
```

O Receipt não altera diretamente atributos internos do Payment.

Da mesma forma, Payment não altera o estado interno de Beneficiary ou Institution.

A resolução de Beneficiary e Institution deve respeitar suas regras globais de normalização e reutilização.

---

# 11. Regras fundamentais do domínio

As seguintes regras são consideradas invariantes do sistema.

### Regra 1 — Payment somente nasce de Receipt confirmado

```text
Payment
    ↑
Receipt.confirm()
```

---

### Regra 2 — Receipt pode existir sem Payment

```text
Receipt
  ↓
0..1 Payment
```

---

### Regra 3 — Payment é imutável

Após confirmação:

```text
Payment = somente leitura
```

---

### Regra 4 — Receipt FAILED pode ser reprocessado

```text
FAILED
  ↓
PROCESSING
```

---

### Regra 5 — Receipt PROCESSED não pode ser reprocessado

```text
PROCESSED
  ↓
não permitido
```

---

### Regra 6 — Campos obrigatórios devem existir antes da confirmação

Obrigatórios:

```text
date
amount
beneficiary
source_institution
```

---

### Regra 7 — Beneficiary é global

O mesmo Beneficiary pode ser utilizado por vários usuários.

```text
User A ──┐
User B ──┼── AMAZON
User C ──┘
```

Não existe um Beneficiary específico por usuário.

---

### Regra 8 — Beneficiary é case-insensitive

```text
AMAZON
Amazon
amazon
```

representam o mesmo Beneficiary.

---

### Regra 9 — Beneficiários diferentes permanecem diferentes

```text
Amazon
Amazon.com
```

são Beneficiaries distintos.

---

### Regra 10 — Institution é global

A mesma Institution pode ser utilizada por vários usuários.

```text
User X ──┐
User Y ──┼── Itaú
User Z ──┘
```

A Institution não possui proprietário.

---

### Regra 11 — Institution deve ser reutilizada

Se uma Institution equivalente já existir:

```text
Receipt
   ↓
resolve Institution
   ↓
Institution encontrada
   ↓
reutilizar
```

Não deve ser criada uma nova Institution.

---

### Regra 12 — Institution é identificada por código normalizado

Representações equivalentes devem apontar para o mesmo `name_code`.

Exemplo:

```text
Itaú
Itau
ITAU
```

→

```text
name_code = ITAU
```

---

### Regra 13 — Instituições diferentes permanecem diferentes

```text
Itaú
Nubank
```

são Institutions distintas.

---

### Regra 14 — Usuário INACTIVE não autentica

```text
INACTIVE
   ↓
login = rejeitado
```

---

### Regra 15 — Três falhas consecutivas bloqueiam o usuário

```text
failed_attempts >= 3
        ↓
     LOCKED
```

---

### Regra 16 — Somente ADM desbloqueia usuário

O próprio usuário não pode desbloquear sua conta no MVP.

---

# 12. Resultado esperado

Com este contrato, os próximos componentes do backend possuem responsabilidades claras:

```text
Route
  ↓
Schema
  ↓
Service
  ↓
Aggregate rules
  ↓
Repository
  ↓
Model
```

Os Services serão responsáveis por orquestrar operações entre aggregates quando necessário, enquanto as regras definidas neste documento deverão ser preservadas independentemente da camada que execute a operação.

Os aggregates globais `Beneficiary` e `Institution` devem ser tratados como catálogos compartilhados da aplicação, sem associação direta com um usuário.

Este documento passa a ser a referência funcional para a implementação dos domínios.
