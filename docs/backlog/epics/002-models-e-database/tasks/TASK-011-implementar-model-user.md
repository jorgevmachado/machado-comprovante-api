# TASK-011 — Implementar User

**Status:** `DONE`

**Prioridade:** `P0`

**Dependências:**
- TASK-010.

## Objetivo

Implementar o Model `User`, responsável por representar a identidade e o estado do usuário da aplicação.

## Referências

- `05-domain.md`
- `06-database.md`
- `09-domain-contracts.md`

## Escopo

- Criar o Model `User`;
- Configurar identificação do usuário;
- Configurar username;
- Configurar email;
- Configurar status;
- Configurar relacionamento com Role;
- Configurar timestamps;
- Configurar relacionamentos necessários com as demais entidades;
- Garantir constraints de unicidade.

## Critérios de aceite

- [X] Model `User` está implementado;
- [X] Username possui constraint de unicidade;
- [X] Email possui constraint de unicidade;
- [X] User possui Role;
- [X] User possui Status;
- [X] Timestamps necessários estão configurados;
- [X] Relacionamentos necessários estão preparados;
- [X] O Model pode ser persistido pelo SQLAlchemy;
- [X] O Model pode ser incluído em migrations.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

- TASK-010 deve estar concluída.

## Notas

A definição da Role durante o cadastro pertence ao domínio de autenticação e não deve ser delegada ao cliente.

---

**Status final:** `DONE`

## Status disponíveis

| Status | Significado |
|---|---|
| `TODO` | Ainda não iniciada |
| `PROGRESS` | Em desenvolvimento |
| `READY` | Implementação concluída, aguardando dependência ou validação |
| `BLOCKED` | Bloqueada por uma dependência ainda não concluída |
| `DONE` | Critérios de aceite atendidos e task oficialmente concluída |