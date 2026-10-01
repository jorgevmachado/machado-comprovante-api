# Epic 015 — API e OpenAPI

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Documentar e padronizar a API pública, garantindo visibilidade do contrato e respostas consistentes.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-078 | Documentar endpoints OpenAPI | P0 | DONE |
| TASK-079 | Padronizar respostas HTTP | P0 | DONE |

## Ordem de implementação

```text
TASK-078
    └── TASK-079
```

## Escopo

Este Epic contempla:

* Documentar endpoints OpenAPI;
* Padronizar respostas HTTP;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [x] Os endpoints estiverem documentados no OpenAPI.;
* [x] As respostas HTTP estiverem padronizadas e consistentes.;
* [x] A API pública estiver alinhada ao contrato da aplicação e aos testes aplicáveis.;

* [x] Todos os testes relacionados estiverem passando;
* [x] A documentação do Epic estiver atualizada;
* [x] Nenhuma regra de negócio foi alterada sem respaldo da documentação.
