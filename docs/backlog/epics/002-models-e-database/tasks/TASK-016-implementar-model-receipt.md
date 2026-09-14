# TASK-016 — Implementar Receipt

**Status:** `TODO`

**Prioridade:** `P0`

**Dependências:**
- TASK-004;
- TASK-009.

## Objetivo

Implementar o Model `Receipt`, responsável por representar o comprovante enviado pelo usuário e seu estado de processamento.

## Referências

- [05-domain.md](../../../../05-domain.md)
- [06-database.md](../../../../06-database.md)
- [09-domain-contracts.md](../../../../09-domain-contracts.md)

## Escopo

- Criar o Model `Receipt`;
- Relacionar Receipt ao User;
- Implementar `ProcessingStatus`;
- Armazenar referência ao arquivo original;
- Armazenar hash do arquivo;
- Armazenar dados extraídos;
- Preparar relacionamento com Payment;
- Configurar timestamps;
- Garantir integridade dos dados.

## Regras

O Receipt pertence a um User.

O Receipt representa o documento original enviado para processamento.

O processamento possui estados controlados por `ProcessingStatus`.

Estados:

```text
RECEIVED
PROCESSING
PROCESSED
FAILED
````

O Receipt deve possuir uma referência ao arquivo original armazenado externamente.

## Critérios de aceite

* [ ] Model `Receipt` está implementado;
* [ ] Receipt possui relacionamento com User;
* [ ] Receipt possui `ProcessingStatus`;
* [ ] Referência ao arquivo original pode ser armazenada;
* [ ] Hash do arquivo pode ser armazenado;
* [ ] Dados extraídos podem ser armazenados;
* [ ] Relacionamento com Payment está preparado;
* [ ] Constraints necessárias estão configuradas;
* [ ] Foreign Keys estão configuradas;
* [ ] O Model pode ser persistido;
* [ ] O Model pode ser incluído em migrations.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

* TASK-004 deve estar concluída;
* TASK-009 deve estar concluída.

## Notas

As regras completas de processamento e transição de estados serão implementadas no Epic F e no Epic H.

---

**Status final:** `TODO`

## Status disponíveis

| Status     | Significado                                                  |
| ---------- | ------------------------------------------------------------ |
| `TODO`     | Ainda não iniciada                                           |
| `PROGRESS` | Em desenvolvimento                                           |
| `READY`    | Implementação concluída, aguardando dependência ou validação |
| `BLOCKED`  | Bloqueada por uma dependência ainda não concluída            |
| `DONE`     | Critérios de aceite atendidos e task oficialmente concluída  |
