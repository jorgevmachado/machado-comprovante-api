# TASK-015 — Implementar Beneficiary

**Status:** `TODO`

**Prioridade:** `P0`

**Dependências:**
- TASK-004.

## Objetivo

Implementar o Model `Beneficiary`, responsável por representar beneficiários de forma global na aplicação.

## Referências

- `05-domain.md`
- `06-database.md`
- `09-domain-contracts.md`

## Escopo

- Criar o Model `Beneficiary`;
- Implementar identificação canônica por `name_code`;
- Garantir que Beneficiary não pertença a User;
- Configurar unicidade de `name_code`;
- Configurar timestamps;
- Configurar soft delete conforme definido no banco;
- Preparar relacionamento com Payment.

## Regras

Beneficiary é uma entidade global.

Não deve existir `user_id` em Beneficiary.

Representações equivalentes devem utilizar o mesmo `name_code`.

Exemplo:

```text
Amazon
AMAZON
amazon
````

devem representar o mesmo beneficiário canônico.

Representações semanticamente diferentes devem permanecer distintas.

Exemplo:

```text
Amazon
Amazon.com
```

não devem ser tratados automaticamente como o mesmo beneficiário.

## Critérios de aceite

* [ ] Model `Beneficiary` está implementado;
* [ ] `name_code` possui constraint de unicidade;
* [ ] Beneficiary não possui `user_id`;
* [ ] Timestamps estão configurados;
* [ ] Soft delete está configurado conforme o modelo definido;
* [ ] Relacionamento com Payment está preparado;
* [ ] O Model pode ser persistido;
* [ ] O Model pode ser incluído em migrations.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

* TASK-004 deve estar concluída.

## Notas

A normalização e resolução de beneficiários serão implementadas posteriormente no Epic G.

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