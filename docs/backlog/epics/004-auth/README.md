# Epic 004 — Auth

**Status:** `DONE`

**Prioridade:** `P0`

## Objetivo

Implementar autenticação, autorização e fluxo de registro/login da aplicação Comprovante conforme as regras de segurança e domínio.

## Tasks

| ID | Task | Prioridade | Status |
|---|---|---|---|
| TASK-025 | Implementar hash de senha | P0 | DONE |
| TASK-026 | Implementar registro | P0 | DONE |
| TASK-027 | Implementar autenticação | P0 | DONE |
| TASK-028 | Implementar bloqueio após três falhas | P0 | DONE |
| TASK-029 | Implementar autenticação por token | P0 | DONE |
| TASK-030 | Implementar `/auth/register` | P0 | DONE |
| TASK-031 | Implementar `/auth/login` | P0 | DONE |
| TASK-032 | Implementar `/auth/me` | P0 | DONE |

## Ordem de implementação

```text
TASK-025
    ├── TASK-026
    │      └── TASK-030
    ├── TASK-027
    │      ├── TASK-028
    │      └── TASK-029
    │             ├── TASK-031
    │             └── TASK-032
```

## Escopo

Este Epic contempla:

* Implementar hash de senha;
* Implementar registro;
* Implementar autenticação;
* Implementar bloqueio após três falhas;
* Implementar autenticação por token;
* Implementar `/auth/register`;
* Implementar `/auth/login`;
* Implementar `/auth/me`;

## Regras importantes

- Manter o escopo do Epic alinhado com a documentação arquitetural e de domínio.
- Garantir que cada task seja implementada na camada correta da aplicação.
- Validar o comportamento com testes e contratos de API quando aplicável.

## Definition of Done do Epic

O Epic será considerado `DONE` quando:

* [X] A autenticação do sistema estiver implementada e funcional.;
* [X] O hash de senha estiver correto e seguro.;
* [X] O registro de usuários estiver operacional.;
* [X] O login e a autenticação por token estiverem funcionando conforme o contrato.;
* [X] A proteção contra falhas repetidas estiver implementada.;
* [X] O endpoint `/auth/me` estiver retornando o usuário autenticado corretamente.;
* [X] Os testes automatizados do auth estiverem passando.;
* [X] Nenhum segredo ou dado sensível estiver exposto.;

