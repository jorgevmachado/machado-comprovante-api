# Epic 012 — Queries Financeiras

**Status:** `TODO`

**Prioridade:** `P1`

## Objetivo

Implementar as consultas financeiras agregadas para acompanhamento do volume e do valor dos pagamentos.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-063 | Implementar quantidade de Payments | P1 | DONE |
| TASK-064 | Implementar total de pagamentos | P1 | DONE |
| TASK-065 | Implementar maior pagamento | P1 | DONE |

## Ordem de implementação

```text
TASK-063
    ├── TASK-064
    └── TASK-065
```

## Escopo

Este Epic contempla:

* Implementar quantidade de Payments;
* Implementar total de pagamentos;
* Implementar maior pagamento;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [ ] As consultas financeiras agregadas estiverem implementadas corretamente.;
* [ ] Os resultados forem calculados com precisão e consistência.;
* [ ] Os filtros e isolamentos por usuário estiverem respeitados.;
* [ ] Os testes das queries financeiras estiverem passando.;

* [ ] Todos os testes relacionados estiverem passando;
* [ ] A documentação do Epic estiver atualizada;
* [ ] Nenhuma regra de negócio foi alterada sem respaldo da documentação.
