# Epic 017 — CI

**Status:** `TODO`

**Prioridade:** `P0`

## Objetivo

Configurar a integração contínua para automatizar validação, lint e testes do projeto.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-083 | Configurar GitHub Actions | P0 | TODO |
| TASK-084 | Executar testes automaticamente | P0 | TODO |

## Ordem de implementação

```text
TASK-083
    └── TASK-084
```

## Escopo

Este Epic contempla:

* Configurar GitHub Actions;
* Executar testes automaticamente;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [ ] O GitHub Actions estiver configurado para executar os checks do projeto.;
* [ ] Os testes forem executados automaticamente em pull requests e branches relevantes.;
* [ ] O pipeline estiver estável e documentado.;

* [ ] Todos os testes relacionados estiverem passando;
* [ ] A documentação do Epic estiver atualizada;
* [ ] Nenhuma regra de negócio foi alterada sem respaldo da documentação.
