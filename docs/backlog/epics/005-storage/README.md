# Epic 005 — Storage

**Status:** `TODO`

**Prioridade:** `P0`

## Objetivo

Implementar a camada de armazenamento de arquivos com validação, segurança e integração ao fluxo de recebimento de comprovantes.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-033 | Definir contrato de Storage | P0 | TODO |
| TASK-034 | Implementar Cloudflare R2 Storage | P0 | TODO |
| TASK-035 | Implementar validação de upload | P0 | TODO |
| TASK-036 | Implementar hash do arquivo | P0 | TODO |

## Ordem de implementação

```text
TASK-033
    ├── TASK-034
    ├── TASK-035
    └── TASK-036
```

## Escopo

Este Epic contempla:

* Definir contrato de Storage;
* Implementar Cloudflare R2 Storage;
* Implementar validação de upload;
* Implementar hash do arquivo;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [ ] O contrato de storage estiver definido e coerente com o restante da arquitetura.;
* [ ] A integração com Cloudflare R2 estiver funcional.;
* [ ] O upload de arquivos estiver validado contra regras de segurança.;
* [ ] O hash do arquivo estiver calculado e associado ao registro do comprovante.;
* [ ] Arquivos inválidos não forem aceitos.;
* [ ] Os testes de storage e validação estiverem passando.;

