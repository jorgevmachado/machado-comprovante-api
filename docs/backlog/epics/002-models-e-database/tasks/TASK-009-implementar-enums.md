# TASK-009 — Implementar Enums

**Status:** `DONE`

**Prioridade:** `P0`

**Dependências:**
- Nenhuma.

## Objetivo

Implementar os Enums utilizados pelos Models da aplicação.

## Referências

- [05-domain.md](../../../../05-domain.md)
- [06-database.md](../../../../06-database.md)
- [09-domain-contracts.md](../../../../09-domain-contracts.md)

## Escopo

- Criar o módulo de Enums;
- Implementar `Status`;
- Implementar `ProcessingStatus`;
- Garantir que os valores utilizados pelos Models sejam centralizados;
- Preparar os Enums para utilização pelo SQLAlchemy.

## Enums

### Status

Representa o estado de entidades que possuem ciclo de vida.

Valores:

```text
ACTIVE
INACTIVE
LOCKED
````

### ProcessingStatus

Representa o estado de processamento de um Receipt.

Valores:

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
```

## Critérios de aceite

* [X] Existe um módulo centralizado para os Enums;
* [X] `Status` está implementado;
* [X] `ProcessingStatus` está implementado;
* [X] Os valores estão definidos conforme o domínio;
* [X] Os Enums podem ser utilizados pelos Models;
* [X] Não existem strings duplicadas para esses estados nos Models.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

* Nenhuma.

## Notas

Nenhuma.

---

**Status final:** `DONE`

## Status disponíveis

| Status     | Significado                                                  |
| ---------- | ------------------------------------------------------------ |
| `TODO`     | Ainda não iniciada                                           |
| `PROGRESS` | Em desenvolvimento                                           |
| `READY`    | Implementação concluída, aguardando dependência ou validação |
| `BLOCKED`  | Bloqueada por uma dependência ainda não concluída            |
| `DONE`     | Critérios de aceite atendidos e task oficialmente concluída  |
