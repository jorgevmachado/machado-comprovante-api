# Epic 006 — Receipt

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Implementar a criação, consulta e ciclo de vida dos receipts conforme as regras do domínio e do processamento.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-037 | Implementar criação de Receipt | P0 | DONE |
| TASK-038 | Implementar proteção contra Receipt duplicado | P0 | DONE |
| TASK-039 | Implementar máquina de estados do Receipt | P0 | DONE |
| TASK-040 | Implementar consulta de Receipt | P0 | DONE |

## Ordem de implementação

```text
TASK-037
    ├── TASK-038
    ├── TASK-039
    └── TASK-040
```

## Escopo

Este Epic contempla:

* Implementar criação de Receipt;
* Implementar proteção contra Receipt duplicado;
* Implementar máquina de estados do Receipt;
* Implementar consulta de Receipt;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] A criação de receipt estiver implementada conforme o contrato.;
* [X] Receipts duplicados estiverem protegidos.;
* [X] A máquina de estados do receipt estiver coerente com o fluxo do domínio.;
* [X] A consulta de receipt estiver disponível e filtrando corretamente por usuário e status.;
* [X] Os testes do módulo de receipt estiverem passando.;

