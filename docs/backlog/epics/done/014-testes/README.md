# Epic 014 — Testes

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Cobrir os módulos críticos do sistema com testes automatizados de domínio, integração e regressão.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-070 | Testes dos models | P0 | DONE |
| TASK-071 | Testes do Auth | P0 | DONE |
| TASK-072 | Testes do Receipt | P0 | DONE |
| TASK-073 | Testes dos Parsers | P0 | DONE |
| TASK-074 | Testes do Payment | P0 | DONE |
| TASK-075 | Testes de Beneficiary | P0 | DONE |
| TASK-076 | Testes de Institution | P0 | DONE |
| TASK-077 | Testes de integração da confirmação | P0 | DONE |

## Ordem de implementação

```text
TASK-070
    ├── TASK-071
    ├── TASK-072
    ├── TASK-073
    ├── TASK-074
    ├── TASK-075
    ├── TASK-076
    └── TASK-077
```

## Escopo

Este Epic contempla:

* Testes dos models;
* Testes do Auth;
* Testes do Receipt;
* Testes dos Parsers;
* Testes do Payment;
* Testes de Beneficiary;
* Testes de Institution;
* Testes de integração da confirmação;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] Os testes dos models, auth, receipt, parsers, payment, beneficiary e institution estiverem implementados.;
* [X] A integração da confirmação estiver coberta por testes.;
* [X] Os testes forem executados com sucesso e a regressão for controlada.;
* [X] A suíte de testes estiver alinhada às regras de negócio do MVP.;

* [X] Todos os testes relacionados estiverem passando;
* [X] A documentação do Epic estiver atualizada;
* [X] Nenhuma regra de negócio foi alterada sem respaldo da documentação.
