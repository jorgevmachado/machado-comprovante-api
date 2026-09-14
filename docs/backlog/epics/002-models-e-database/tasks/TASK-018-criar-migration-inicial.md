# TASK-018 — Criar migration inicial

**Status:** `TODO`

**Prioridade:** `P0`

**Dependências:**
- TASK-010;
- TASK-011;
- TASK-012;
- TASK-013;
- TASK-014;
- TASK-015;
- TASK-016;
- TASK-017.

## Objetivo

Criar a migration inicial do banco de dados contendo todas as tabelas, constraints, relacionamentos, índices e regras de unicidade necessárias para o MVP.

## Referências

- [05-domain.md](../../../../05-domain.md)
- [06-database.md](../../../../06-database.md)
- [09-domain-contracts.md](../../../../09-domain-contracts.md)

## Escopo

A migration inicial deve contemplar:

- Role;
- User;
- Password;
- Authentication;
- Institution;
- Beneficiary;
- Receipt;
- Payment;
- Enums necessários;
- Foreign Keys;
- Índices;
- Constraints;
- Unicidade;
- Campos obrigatórios e opcionais;
- Relacionamentos entre entidades.

## Critérios de aceite

- [ ] Todas as tabelas do MVP estão presentes;
- [ ] Foreign Keys estão configuradas;
- [ ] Constraints estão configuradas;
- [ ] Índices necessários estão presentes;
- [ ] Constraints de unicidade estão presentes;
- [ ] Enums estão corretamente representados;
- [ ] Campos obrigatórios possuem as restrições necessárias;
- [ ] Campos opcionais aceitam `NULL` quando definido pelo domínio;
- [ ] A migration pode ser executada em um banco vazio;
- [ ] A migration cria a estrutura completa do MVP;
- [ ] O rollback da migration funciona;
- [ ] A estrutura gerada corresponde aos Models implementados.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

- TASK-010 deve estar concluída;
- TASK-011 deve estar concluída;
- TASK-012 deve estar concluída;
- TASK-013 deve estar concluída;
- TASK-014 deve estar concluída;
- TASK-015 deve estar concluída;
- TASK-016 deve estar concluída;
- TASK-017 deve estar concluída.

## Notas

A migration deve representar o estado efetivamente implementado dos Models.

Antes da conclusão desta task, qualquer inconsistência entre `06-database.md`, `09-domain-contracts.md` e os Models deve ser resolvida ou registrada explicitamente.

---

**Status final:** `TODO`

## Status disponíveis

| Status | Significado |
|---|---|
| `TODO` | Ainda não iniciada |
| `PROGRESS` | Em desenvolvimento |
| `READY` | Implementação concluída, aguardando dependência ou validação |
| `BLOCKED` | Bloqueada por uma dependência ainda não concluída |
| `DONE` | Critérios de aceite atendidos e task oficialmente concluída |
