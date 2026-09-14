# TASK-012 — Implementar Password

**Status:** `DONE`

**Prioridade:** `P0`

**Dependências:**
- TASK-011.

## Objetivo

Implementar o Model responsável pelo armazenamento das informações necessárias relacionadas à senha do usuário.

## Referências

- `05-domain.md`
- `06-database.md`
- `09-domain-contracts.md`

## Escopo

- Criar o Model `Password`;
- Relacionar Password ao User;
- Armazenar somente o hash da senha;
- Configurar integridade do relacionamento;
- Configurar timestamps ou demais atributos definidos no banco.

## Critérios de aceite

- [X] Model `Password` está implementado;
- [X] Password está relacionada a User;
- [X] Apenas o hash da senha é persistido;
- [X] Senha em texto puro não é persistida;
- [X] O relacionamento possui integridade referencial;
- [X] O Model pode ser persistido pelo SQLAlchemy;
- [X] O Model pode ser incluído em migrations.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

- TASK-011 deve estar concluída.

## Notas

A geração e validação do hash serão utilizadas posteriormente pelo domínio de autenticação.

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