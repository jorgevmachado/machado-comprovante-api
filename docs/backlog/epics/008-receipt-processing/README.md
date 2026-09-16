# Epic 008 — Receipt Processing

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Implementar o pipeline de processamento de comprovantes, extração de texto, OCR, parsers, identificação de instituição e integração ao ciclo de vida do receipt.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-045 | Criar pipeline de processamento | P0 | DONE |
| TASK-046 | Implementar extração de texto PDF | P0 | DONE |
| TASK-047 | Implementar OCR | P0 | DONE |
| TASK-048 | Criar contrato de parser | P0 | DONE |
| TASK-049 | Implementar Itaú Receipt Parser | P0 | DONE |
| TASK-050 | Implementar Nubank Receipt Parser | P0 | DONE |
| TASK-051 | Implementar Generic Receipt Parser | P0 | DONE |
| TASK-052 | Implementar identificação de instituição | P0 | DONE |
| TASK-053 | Implementar validação de suficiência | P0 | DONE |
| TASK-054 | Implementar AI fallback | P1 | DONE |
| TASK-055 | Integrar processamento ao Receipt | P0 | DONE |
| TASK-056 | Implementar reprocessamento de FAILED | P0 | DONE |

## Ordem de implementação

```text
TASK-045
    ├── TASK-046
    │      ├── TASK-047
    │      └── TASK-048
    │             ├── TASK-049
    │             ├── TASK-050
    │             ├── TASK-051
    │             └── TASK-052
    ├── TASK-053
    ├── TASK-054
    ├── TASK-055
    └── TASK-056
```

## Escopo

Este Epic contempla:

* Criar pipeline de processamento;
* Implementar extração de texto PDF;
* Implementar OCR;
* Criar contrato de parser;
* Implementar Itaú Receipt Parser;
* Implementar Nubank Receipt Parser;
* Implementar Generic Receipt Parser;
* Implementar identificação de instituição;
* Implementar validação de suficiência;
* Implementar AI fallback;
* Integrar processamento ao Receipt;
* Implementar reprocessamento de FAILED;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] O pipeline de processamento estiver criado e integrado ao fluxo do receipt.;
* [X] A extração de texto PDF e OCR estiverem funcionando.;
* [X] Os parsers de Itaú, Nubank e genérico estiverem implementados e cobertos por testes.;
* [X] A identificação de instituição estiver correta.;
* [X] A validação de suficiência e o AI fallback estiverem implementados quando necessário.;
* [X] O reprocessamento de receipts em FAILED estiver funcional.;
* [X] Os testes do processamento estiverem passando.;

