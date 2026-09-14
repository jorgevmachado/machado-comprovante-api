# TASK-014 — Implementar Institution

**Status:** `TODO`

**Prioridade:** `P0`

**Dependências:**
- TASK-004.

## Objetivo

Implementar o Model `Institution`, responsável por representar instituições financeiras de forma global na aplicação.

## Referências

- `05-domain.md`
- `06-database.md`
- `09-domain-contracts.md`

## Escopo

- Criar o Model `Institution`;
- Implementar identificação canônica por `name_code`;
- Garantir que Institution não pertença a User;
- Configurar unicidade de `name_code`;
- Configurar timestamps;
- Configurar soft delete conforme definido no banco;
- Preparar relacionamentos com Receipt e Payment.

## Regras

Institution é uma entidade global.

Não deve existir `user_id` em Institution.

Representações equivalentes devem utilizar o mesmo `name_code`.

Exemplo:

```text
Itaú
Itau
ITAU
````

devem representar a mesma instituição canônica.

## Critérios de aceite

* [ ] Model `Institution` está implementado;
* [ ] `name_code` possui constraint de unicidade;
* [ ] Institution não possui `user_id`;
* [ ] Timestamps estão configurados;
* [ ] Soft delete está configurado conforme o modelo definido;
* [ ] Relacionamentos necessários estão preparados;
* [ ] O Model pode ser persistido;
* [ ] O Model pode ser incluído em migrations.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

* TASK-004 deve estar concluída.

## Notas

A normalização e resolução de instituições serão implementadas posteriormente no Epic G.

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