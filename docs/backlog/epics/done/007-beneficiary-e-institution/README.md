# Epic 007 — Beneficiary e Institution

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Implementar a normalização, resolução e relacionamento entre beneficiários e instituições, mantendo consistência e organização dos dados.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-041 | Implementar normalização de Beneficiary | P0 | DONE |
| TASK-042 | Implementar resolução de Beneficiary | P0 | DONE |
| TASK-043 | Implementar normalização de Institution | P0 | DONE |
| TASK-044 | Implementar resolução de Institution | P0 | DONE |

## Ordem de implementação

```text
TASK-041
    ├── TASK-042
    ├── TASK-043
    └── TASK-044
```

## Escopo

Este Epic contempla:

* Implementar normalização de Beneficiary;
* Implementar resolução de Beneficiary;
* Implementar normalização de Institution;
* Implementar resolução de Institution;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] Beneficiários e instituições estiverem normalizados e deduplicados corretamente.;
* [X] A resolução de beneficiários e instituições estiver funcionando em cenários reais de ingestão.;
* [X] Os identificadores canônicos estiverem consistentes com as regras do domínio.;
* [X] Relacionamentos e regras de unicidade estiverem validados.;
* [X] Os testes associados estiverem passando.;

