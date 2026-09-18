# 10 — Backlog de Implementação

## 1. Objetivo

Este documento define o backlog técnico para implementação do MVP da aplicação Comprovante.

A documentação `01` a `09` define os requisitos, arquitetura, tecnologia, domínio, persistência, API e contratos de negócio.

Este documento transforma essas definições em unidades executáveis de trabalho.

O backlog não deve introduzir novas regras de negócio.

Quando existir conflito entre uma task e a documentação arquitetural, a documentação deve prevalecer.

---

# 2. Convenções

## 2.1 Identificação

As tasks utilizam o formato:

```text
TASK-001
TASK-002
TASK-003
...
```

---

## 2.2 Prioridade

| Prioridade | Significado                                       |
| ---------- | ------------------------------------------------- |
| P0         | Bloqueia o MVP                                    |
| P1         | Necessária para completar o MVP                   |
| P2         | Importante, mas pode ser concluída posteriormente |

---

## 2.3 Status

| Status      | Significado               |
| ----------- | ------------------------- |
| TODO        | Ainda não iniciada        |
| IN_PROGRESS | Em desenvolvimento        |
| BLOCKED     | Bloqueada por dependência |
| DONE        | Concluída                 |

Todas as tasks iniciam como:

```text
TODO
```

---

# 3. Ordem geral de implementação

A implementação seguirá aproximadamente esta sequência:

```text
Fundação
   ↓
Database
   ↓
Auth
   ↓
Storage
   ↓
Receipt
   ↓
Beneficiary / Institution
   ↓
Receipt Processing
   ↓
Payment
   ↓
API
   ↓
Queries
   ↓
Testes
   ↓
Observabilidade
   ↓
Deploy
```

A ordem pode ser ajustada durante a execução quando uma dependência técnica justificar a mudança.

---

# 4. [Épico A — Fundação do Backend](epics/done/001-fundacao-do-backend/README.md)

Objetivo:

Estabelecer a infraestrutura básica da aplicação FastAPI.

**Status:** `DONE`

---

# 5. [Épico B — Models e Database](epics/done/002-models-e-database/README.md)

Objetivo:

Implementar a persistência definida em [`../06-database.md`](../06-database.md).

**Status:** `DONE`
---

# 6. [Épico C — Repository](epics/done/003-repository/README.md)

Objetivo:

Implementar acesso aos dados sem acoplar os Services diretamente ao SQLAlchemy.

**Status:** `DONE`

---

# 7. [Épico D — Auth](epics/done/004-auth/README.md)

Objetivo:

Implementar o aggregate Auth conforme `../09-domain-contracts.md`.

**Status:** `DONE`

---

# 8. [Épico E — Storage](./epics/005-storage/README.md)

Objetivo:

Implementar armazenamento dos arquivos originais.

**Status:** `TODO`

---

# 9. [Épico F — Receipt](epics/done/006-receipt/README.md)

Objetivo:

Implementar a criação, consulta e ciclo de vida dos receipts conforme as regras do domínio e do processamento.

**Status:** `DONE`

---

# 10. [Épico G — Beneficiary e Institution](epics/done/007-beneficiary-e-institution/README.md)

Objetivo:

Implementar a normalização, resolução e relacionamento entre beneficiários e instituições, mantendo consistência e organização dos dados.

**Status:** `DONE`

---
# 11. [Épico H — Receipt Processing](epics/done/008-receipt-processing/README.md)

Objetivo:

Transformar o documento original em dados estruturados.

**Status:** `DONE`
---

# 12. [Épico I — Review e Confirmation](epics/done/009-review-e-confirmation/README.md)

Objetivo:

Implementar a revisão dos dados extraídos e a confirmação do receipt, garantindo consistência, idempotência e integridade do pagamento.

**Status:** `DONE`

---

# 13. [Épico J — Payment API](epics/done/010-payment-api/README.md)

Objetivo:

Implementar a API de listagem e consulta de pagamentos, garantindo o contrato de negócio e o isolamento por usuário.

**Status:** `DONE`

---

# 14. [Épico K — Beneficiary API](epics/done/011-beneficiary-api/README.md)

Objetivo:

Implementar a API de consulta de beneficiários e garantir o acesso consistente e isolado por usuário.

**Status:** `DONE`

---

# 15. [Épico L — Queries Financeiras](epics/done/012-queries-financeiras/README.md)

Objetivo:

Implementar as consultas financeiras agregadas para acompanhamento do volume e do valor dos pagamentos.

**Status:** `DONE`

# 16. [Épico M — Segurança](epics/done/013-seguranca/README.md)

Objetivo:

Fortalecer a segurança da aplicação, validando upload de arquivos e protegendo secrets, conforme as exigências do MVP.

**Status:** `TODO`

---

# 17. [Épico N — Testes](epics/done/014-testes/README.md)

### TASK-070 — Testes dos models

Objetivo:

Cobrir os módulos críticos do sistema com testes automatizados de domínio, integração e regressão.

**Status:** `TODO`
---

# 18. [Épico O — API e OpenAPI](./epics/015-api-e-openapi/README.md)

Objetivo:

Documentar e padronizar a API pública, garantindo visibilidade do contrato e respostas consistentes.

**Status:** `TODO`
---

# 19. [Épico P — Docker e Ambiente](epics/done/016-docker-e-ambiente/README.md)

Objetivo:

Preparar o ambiente de desenvolvimento com contêinerização e configuração local da aplicação.

**Status:** `DONE`
---

# 20. [Épico Q — CI](epics/done/017-ci/README.md)

Objetivo:

Configurar a integração contínua para automatizar validação, lint e testes do projeto.

**Status:** `TODO`
---

# 21. [Épico R — Observabilidade](epics/done/018-observabilidade/README.md)

Objetivo:

Implementar logs e rastreio de erros para monitoramento do processamento e das operações críticas.

**Status:** `DONE`

---

# 22. [Épico S — Deploy](./epics/019-deploy/README.md)

Objetivo:

Preparar o deploy do backend em ambiente de produção com infraestrutura e configuração adequadas.

**Status:** `TODO`
---

# 23. [Épico T — MVP End-to-End](./epics/020-mvp-end-to-end/README.md)

Objetivo:

Validar o fluxo completo do MVP, cobrindo isolamento, idempotência e imutabilidade do pagamento.

**Status:** `TODO`
---

# 24. Definition of Done

Uma task somente pode ser marcada como `DONE` quando:

* implementação concluída;
* critérios de aceite atendidos;
* testes relevantes implementados;
* testes passando;
* nenhuma regra existente foi quebrada;
* documentação necessária atualizada;
* código revisado;
* nenhuma credencial ou secret foi incluída no repositório.

---

# 25. Definition of Done do MVP

O MVP será considerado concluído quando:

```text
Auth
  ✓ registro
  ✓ login
  ✓ bloqueio
  ✓ identificação

Receipt
  ✓ upload
  ✓ armazenamento
  ✓ duplicidade
  ✓ processamento
  ✓ extração
  ✓ review
  ✓ confirmação

Payment
  ✓ criação
  ✓ consulta
  ✓ imutabilidade

Beneficiary
  ✓ normalização
  ✓ reutilização
  ✓ catálogo global

Institution
  ✓ normalização
  ✓ reutilização
  ✓ catálogo global

Queries
  ✓ quantidade
  ✓ total
  ✓ maior pagamento
  ✓ consulta por beneficiário

Security
  ✓ isolamento
  ✓ upload seguro
  ✓ secrets

Quality
  ✓ testes
  ✓ CI
  ✓ OpenAPI

Infrastructure
  ✓ PostgreSQL
  ✓ storage
  ✓ deploy
```