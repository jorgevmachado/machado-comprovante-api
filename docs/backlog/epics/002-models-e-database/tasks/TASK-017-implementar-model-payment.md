# TASK-017 — Implementar Payment

**Status:** `TODO`

**Prioridade:** `P0`

**Dependências:**
- TASK-004;
- TASK-014;
- TASK-015;
- TASK-016.

## Objetivo

Implementar o Model `Payment`, responsável por representar um pagamento confirmado pela aplicação.

## Referências

- `05-domain.md`
- `06-database.md`
- `09-domain-contracts.md`

## Escopo

- Criar o Model `Payment`;
- Relacionar Payment ao User;
- Relacionar Payment ao Beneficiary;
- Relacionar Payment à Institution de origem;
- Relacionar Payment à Institution de destino;
- Relacionar Payment ao Receipt;
- Armazenar data do pagamento;
- Armazenar valor monetário utilizando precisão adequada;
- Configurar integridade referencial;
- Preparar constraints e índices necessários.

## Regras

Payment representa um pagamento confirmado.

Payment deve ser criado somente durante a confirmação de um Receipt.

Payment é imutável após sua criação.

A aplicação não deve oferecer operações públicas de alteração ou exclusão de Payment no MVP.

## Relacionamentos

Payment deve possuir referência para:

```text
User
Beneficiary
Source Institution
Destination Institution
Receipt
````

A Institution de destino pode ser nula quando não estiver disponível no comprovante.

## Critérios de aceite

* [ ] Model `Payment` está implementado;
* [ ] Payment possui relacionamento com User;
* [ ] Payment possui relacionamento com Beneficiary;
* [ ] Payment possui Institution de origem;
* [ ] Payment possui Institution de destino opcional;
* [ ] Payment possui relacionamento com Receipt;
* [ ] Data do pagamento está implementada;
* [ ] Valor utiliza `Decimal`/tipo monetário apropriado;
* [ ] Foreign Keys estão configuradas;
* [ ] Constraints necessárias estão configuradas;
* [ ] Índices necessários estão configurados;
* [ ] O Model pode ser persistido;
* [ ] O Model pode ser incluído em migrations;
* [ ] O Model não possui operações de atualização/exclusão no contrato de domínio.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

* TASK-004 deve estar concluída;
* TASK-014 deve estar concluída;
* TASK-015 deve estar concluída;
* TASK-016 deve estar concluída.

## Notas

Existe uma inconsistência a ser alinhada antes da implementação definitiva deste Model:

* `09-domain-contracts.md` define Payment como imutável;
* `06-database.md` possui campos `updated_at` e `deleted_at` para Payment.

Essa definição deve ser reconciliada antes da implementação final da persistência de Payment.

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
