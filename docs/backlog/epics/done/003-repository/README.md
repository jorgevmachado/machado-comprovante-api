# Epic 003 — Repository

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Implementar a camada de repositórios da aplicação Comprovante conforme o contrato de domínio, persistência e arquitetura backend.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-019 | Definir contrato de Repository | P0 | DONE |
| TASK-020 | Implementar UserRepository | P0 | DONE |
| TASK-021 | Implementar ReceiptRepository | P0 | DONE |
| TASK-022 | Implementar PaymentRepository | P0 | DONE |
| TASK-023 | Implementar BeneficiaryRepository | P0 | DONE |
| TASK-024 | Implementar InstitutionRepository | P0 | DONE |

## Ordem de implementação

```text
TASK-019
    ├── TASK-020
    ├── TASK-021
    ├── TASK-022
    ├── TASK-023
    └── TASK-024
```

## Escopo

Este Epic contempla:

* Definir contrato de Repository;
* Implementar UserRepository;
* Implementar ReceiptRepository;
* Implementar PaymentRepository;
* Implementar BeneficiaryRepository;
* Implementar InstitutionRepository;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] Todos os contratos e repositórios do MVP estiverem implementados.;
* [X] Os repositórios estiverem alinhados ao contrato de base do sistema.;
* [X] Os métodos de leitura e escrita estiverem cobrindo os cenários principais do domínio.;
* [X] Consultas de listing, query por usuário e query por identificadores estiverem funcionais.;
* [X] As regras de isolamento por usuário estiverem respeitadas.;
* [X] Os testes relacionados estiverem passando.;
* [X] A documentação dos contratos e integrações estiver atualizada.;

