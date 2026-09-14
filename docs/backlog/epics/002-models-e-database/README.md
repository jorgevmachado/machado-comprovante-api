# Epic 002 — Models e Database

**Status:** `PROGRESS`

**Prioridade:** `P0`

## Objetivo

Implementar os Models e a estrutura de persistência da aplicação Comprovante conforme definido na documentação de banco de dados e nos contratos de domínio.

Este Epic estabelece as entidades persistidas necessárias para autenticação, processamento de comprovantes, beneficiários, instituições e pagamentos.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-009 | Implementar Enums | P0 | DONE |
| TASK-010 | Implementar Role | P0 | DONE |
| TASK-011 | Implementar User | P0 | DONE |
| TASK-012 | Implementar Password | P0 | DONE |
| TASK-013 | Implementar Authentication | P0 | DONE |
| TASK-014 | Implementar Institution | P0 | DONE |
| TASK-015 | Implementar Beneficiary | P0 | DONE |
| TASK-016 | Implementar Receipt | P0 | TODO |
| TASK-017 | Implementar Payment | P0 | TODO |
| TASK-018 | Criar migration inicial | P0 | TODO |

## Ordem de implementação

```text
TASK-009
   │
   ├── TASK-010
   │      └── TASK-011
   │             ├── TASK-012
   │             └── TASK-013
   │
   ├── TASK-014
   │
   ├── TASK-015
   │
   └── TASK-016
           │
           └── TASK-017
                    │
                    └── TASK-018
````

## Escopo

Este Epic contempla:

* Enums utilizados pelos Models;
* Role;
* User;
* Password;
* Authentication;
* Institution;
* Beneficiary;
* Receipt;
* Payment;
* Relacionamentos entre as entidades;
* Constraints;
* Foreign Keys;
* Índices;
* Unicidade;
* Migration inicial do banco.

## Regras importantes

### User

O usuário possui estado de autenticação e relacionamento com suas entidades pertencentes.

### Institution

Instituições são globais e não pertencem a um usuário específico.

A identificação canônica utiliza `name_code`.

### Beneficiary

Beneficiários são globais e não pertencem a um usuário específico.

A identificação canônica utiliza `name_code`.

### Receipt

O comprovante pertence a um usuário e representa o documento recebido e processado pela aplicação.

### Payment

Payment representa o pagamento confirmado.

Payment deve ser criado somente durante a confirmação de um Receipt.

Após criado, Payment é tratado como imutável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [ ] Todos os Models do MVP estiverem implementados;
* [ ] Enums estiverem implementados;
* [ ] Relacionamentos estiverem configurados;
* [ ] Constraints estiverem implementadas;
* [ ] Foreign Keys estiverem configuradas;
* [ ] Índices necessários estiverem criados;
* [ ] Regras de unicidade estiverem implementadas;
* [ ] Migration inicial estiver criada;
* [ ] Migration puder ser executada;
* [ ] Rollback puder ser executado;
* [ ] Testes relacionados estiverem passando;
* [ ] Não houver quebra das regras de domínio;
* [ ] A documentação necessária estiver atualizada.
