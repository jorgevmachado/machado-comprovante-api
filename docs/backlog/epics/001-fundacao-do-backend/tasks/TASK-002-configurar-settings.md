# TASK-002 — Configurar Settings

**Status:** `DONE`

**Prioridade:** `P0`

**Dependências:**
- TASK-001.

## Objetivo

Criar o sistema centralizado de configurações da aplicação, permitindo que valores específicos do ambiente sejam definidos externamente.

## Referências

- `03-architecture.md`
- `04-technology.md`
- `08-backend-architecture.md`

## Escopo

- Criar o módulo de configurações da aplicação;
- Centralizar configurações utilizadas pelo backend;
- Configurar valores relacionados ao ambiente;
- Configurar banco de dados;
- Configurar segurança;
- Configurar storage;
- Configurar demais variáveis necessárias à aplicação;
- Permitir configuração por variáveis de ambiente;
- Impedir que secrets sejam armazenados diretamente no código.

## Critérios de aceite

- [X] Existe um módulo centralizado de Settings;
- [X] As configurações são carregadas por variáveis de ambiente;
- [X] Configurações de banco de dados estão contempladas;
- [X] Configurações de segurança estão contempladas;
- [X] Configurações de storage estão contempladas;
- [X] Configurações específicas do ambiente estão contempladas;
- [X] Nenhum secret está hardcoded;
- [X] A aplicação consegue inicializar suas configurações corretamente.

## Implementação

Registrar aqui os principais pontos implementados durante a execução da task.

## Dependências para conclusão

- TASK-001 deve estar concluída.

## Notas

Nenhuma.

---

**Status final:** `DONE`

## Status disponíveis

| Status | Significado |
|---|---|
| `TODO` | Ainda não iniciada |
| `PROGRESS` | Em desenvolvimento |
| `READY` | Implementação concluída, aguardando dependência, validação ou condição externa |
| `BLOCKED` | Bloqueada por uma dependência ainda não concluída |
| `DONE` | Critérios de aceite atendidos e task oficialmente concluída |