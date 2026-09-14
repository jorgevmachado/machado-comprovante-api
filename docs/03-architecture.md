# Comprovante

## 1. Objetivo

Este documento define a arquitetura do sistema Comprovante.

A arquitetura tem como objetivo organizar os principais componentes da aplicação, suas responsabilidades e a comunicação entre eles.

As decisões deste documento deverão servir como base para a definição das tecnologias utilizadas no projeto.

---

## 2. Visão geral

O Comprovante será uma aplicação web composta por uma interface cliente e uma camada de serviços responsável pela autenticação, processamento dos comprovantes, registro dos pagamentos e consultas.

A arquitetura deverá separar:

* apresentação;
* regras de negócio;
* processamento de comprovantes;
* persistência;
* armazenamento de arquivos;
* infraestrutura.

A comunicação entre o cliente e o backend será realizada através de uma API.

Visão simplificada:

```text
┌──────────────────────────────┐
│          Cliente             │
│                              │
│  Desktop / Smartphone        │
└──────────────┬───────────────┘
               │
               │ HTTP
               ▼
┌──────────────────────────────┐
│             API              │
│                              │
│  Autenticação                │
│  Pagamentos                  │
│  Comprovantes                │
│  Consultas                   │
└───────┬───────────┬──────────┘
        │           │
        │           │
        ▼           ▼
┌──────────────┐ ┌──────────────────┐
│ Banco de     │ │ Armazenamento    │
│ dados        │ │ de arquivos      │
└──────────────┘ └──────────────────┘
        │
        │
        ▼
┌──────────────────────────────┐
│ Processamento de comprovante │
│                              │
│ Extração / OCR / interpretação│
└──────────────────────────────┘
```

---

## 3. Componentes principais

O sistema será dividido nos seguintes componentes lógicos:

```text
Comprovante
│
├── Cliente
│
├── API
│   ├── Autenticação
│   ├── Comprovantes
│   ├── Pagamentos
│   └── Consultas
│
├── Processamento
│   ├── Extração
│   ├── OCR
│   └── Interpretação
│
├── Banco de dados
│
└── Armazenamento de arquivos
```

Cada componente deverá possuir responsabilidade claramente definida.

---

# 4. Cliente

O cliente será responsável pela interação com o usuário.

Suas responsabilidades incluem:

* autenticação;
* envio de comprovantes;
* apresentação do progresso do processamento;
* apresentação das informações extraídas;
* edição das informações;
* confirmação do pagamento;
* consulta do histórico;
* filtros e pesquisas.

O cliente não deverá ser responsável por regras críticas de negócio.

Regras relacionadas à persistência, autorização e validação definitiva dos pagamentos deverão permanecer no backend.

---

## 4.1. Fluxo do cliente

O fluxo principal será:

```text
Usuário
   │
   ▼
Seleciona comprovante
   │
   ▼
Upload
   │
   ▼
Processamento
   │
   ▼
Resultado da extração
   │
   ▼
Revisão
   │
   ▼
Confirmação
   │
   ▼
Pagamento registrado
```

---

# 5. API

A API será o ponto central de comunicação entre o cliente e os serviços do sistema.

Suas responsabilidades incluem:

* autenticação;
* autorização;
* recebimento dos comprovantes;
* gerenciamento do processamento;
* disponibilização dos dados extraídos;
* confirmação dos pagamentos;
* consultas;
* validação das requisições;
* aplicação das regras de negócio.

A API não deverá depender da interface para garantir a integridade dos dados.

---

# 6. Autenticação e autorização

A autenticação será realizada através da API.

Após autenticar, o usuário deverá possuir uma identidade que será utilizada para determinar quais dados ele pode acessar.

Toda operação relacionada a pagamentos deverá considerar o usuário autenticado.

O backend deverá garantir que:

```text
Usuário A
   │
   ├── Pagamento A1
   └── Pagamento A2

Usuário B
   │
   ├── Pagamento B1
   └── Pagamento B2
```

O usuário A não deverá conseguir consultar ou modificar os pagamentos do usuário B.

A estratégia específica de autenticação será definida no documento de tecnologia.

---

# 7. Componente de comprovantes

O componente de comprovantes será responsável pelo ciclo de vida do arquivo enviado pelo usuário.

Suas responsabilidades incluem:

* receber o arquivo;
* validar o arquivo;
* armazenar o arquivo original;
* iniciar o processamento;
* acompanhar o estado do processamento;
* disponibilizar o resultado da extração.

O comprovante deverá existir independentemente do pagamento até que o usuário confirme o registro.

---

# 8. Pipeline de processamento

O processamento será organizado em etapas.

```text
Arquivo
   │
   ▼
Validação
   │
   ▼
Leitura
   │
   ▼
Extração de texto
   │
   ▼
Interpretação
   │
   ▼
Dados estruturados
   │
   ▼
Revisão pelo usuário
```

Cada etapa deverá possuir responsabilidade específica.

---

## 8.1. Validação

A primeira etapa deverá verificar se o arquivo recebido pode ser processado.

Exemplos:

* formato;
* tamanho;
* integridade;
* conteúdo mínimo esperado.

Arquivos inválidos deverão ser rejeitados antes do processamento.

---

## 8.2. Leitura do arquivo

O sistema deverá determinar como obter o conteúdo do comprovante.

Para documentos que já possuem texto, o sistema deverá priorizar a extração direta.

Para documentos que não possuem texto utilizável, poderá ser utilizado OCR.

Conceitualmente:

```text
PDF com texto ──────────────► Extração direta
                                  │
                                  ▼
                              Texto

PDF sem texto ─► OCR ───────────► Texto

Imagem ────────► OCR ───────────► Texto
```

O mecanismo específico utilizado em cada etapa será definido posteriormente.

---

# 9. Interpretação

A interpretação será responsável por transformar o conteúdo extraído em informações estruturadas do pagamento.

A entrada será o conteúdo obtido do comprovante.

A saída deverá conter, quando identificáveis:

```text
Data
Favorecido
Valor
Instituição de origem
Instituição de destino
```

A interpretação deverá ser desacoplada da interface e da persistência.

---

## 9.1. Resultado intermediário

O resultado da interpretação deverá ser tratado como informação provisória.

Conceitualmente:

```text
Comprovante
     │
     ▼
Processamento
     │
     ▼
Dados identificados
     │
     ▼
Revisão do usuário
     │
     ▼
Dados confirmados
```

O sistema não deverá considerar o resultado da interpretação como um pagamento definitivo.

---

# 10. Revisão

A revisão será realizada pelo usuário antes da persistência definitiva.

O backend deverá disponibilizar ao cliente os dados identificados.

O cliente deverá permitir que o usuário altere esses dados.

Após a edição, o cliente enviará os dados confirmados para a API.

O backend deverá validar novamente os dados antes do registro.

---

# 11. Registro do pagamento

O registro definitivo será responsabilidade do backend.

O fluxo será:

```text
Dados extraídos
      │
      ▼
Usuário revisa
      │
      ▼
Usuário confirma
      │
      ▼
API recebe dados confirmados
      │
      ▼
Validação
      │
      ▼
Persistência
      │
      ▼
Pagamento registrado
```

O cliente não deverá possuir autoridade para considerar um pagamento registrado sem confirmação do backend.

---

# 12. Banco de dados

O banco de dados será responsável pelo armazenamento dos dados estruturados da aplicação.

Deverá armazenar, no mínimo:

* usuários;
* pagamentos;
* favorecidos, quando aplicável;
* instituições, quando aplicável;
* metadados dos comprovantes;
* informações necessárias ao processamento;
* datas de criação e atualização.

O banco não deverá ser utilizado para armazenar diretamente arquivos grandes de comprovantes caso exista uma solução apropriada de armazenamento de arquivos.

---

# 13. Armazenamento de arquivos

Os comprovantes originais deverão ser armazenados em uma solução própria para arquivos.

O banco de dados deverá manter apenas a referência necessária para localizar o arquivo.

Conceitualmente:

```text
Banco de dados
      │
      │ receipt.file_reference
      ▼
Armazenamento de arquivos
      │
      └── comprovante.pdf
```

O acesso aos arquivos deverá ser protegido.

Os arquivos não deverão ser públicos por padrão.

---

# 14. Relação entre pagamento e comprovante

O pagamento deverá possuir uma referência para o comprovante utilizado no registro.

Conceitualmente:

```text
Payment
   │
   └── Receipt
           │
           └── Original File
```

O comprovante deverá permanecer associado ao pagamento após sua confirmação.

---

# 15. Estados do processamento

O processamento de um comprovante deverá possuir estados identificáveis.

Uma representação inicial poderá ser:

```text
RECEIVED
    │
    ▼
PROCESSING
    │
    ├──────────────► FAILED
    │
    ▼
PROCESSED
    │
    ▼
REVIEW
    │
    ▼
CONFIRMED
```

### Estados

**RECEIVED**

Arquivo recebido e validado.

**PROCESSING**

Arquivo sendo processado.

**FAILED**

O processamento não conseguiu ser concluído.

**PROCESSED**

As informações foram extraídas.

**REVIEW**

Resultado disponível para revisão do usuário.

**CONFIRMED**

Dados confirmados pelo usuário.

O estado definitivo de um pagamento deverá ser separado do estado de processamento do comprovante.

---

# 16. Processamento síncrono e assíncrono

A arquitetura deverá permitir que o processamento seja executado de forma assíncrona quando necessário.

Para operações rápidas, poderá existir processamento síncrono.

Para operações potencialmente demoradas, como:

* OCR;
* processamento de documentos;
* chamadas para serviços externos;
* interpretação por modelos de IA;

poderá ser utilizado processamento assíncrono.

A adoção de filas e workers será definida após a escolha das tecnologias e avaliação do volume esperado do MVP.

---

# 17. Consultas

As consultas deverão ser realizadas pelo backend.

O cliente enviará filtros e parâmetros para a API.

Exemplo conceitual:

```text
Cliente
   │
   │ período = setembro/2026
   ▼
API
   │
   ▼
Consulta
   │
   ▼
Banco de dados
   │
   ▼
Resultado
   │
   ▼
Cliente
```

As agregações deverão ser realizadas preferencialmente no backend/banco de dados, evitando carregar dados desnecessários para o cliente.

---

# 18. Resumos financeiros

As consultas deverão permitir gerar informações agregadas como:

```text
Quantidade de pagamentos
Valor total
Maior pagamento
Total por favorecido
Quantidade por favorecido
```

Essas informações deverão ser derivadas dos pagamentos confirmados.

Pagamentos que ainda estejam em processamento ou revisão não deverão ser considerados como pagamentos registrados.

---

# 19. Segurança

A arquitetura deverá considerar segurança desde as primeiras camadas.

O fluxo deverá ser:

```text
Cliente
   │
   ▼
Autenticação
   │
   ▼
Identidade do usuário
   │
   ▼
Autorização
   │
   ▼
Regra de negócio
   │
   ▼
Persistência
```

Nenhuma operação deverá confiar exclusivamente em informações fornecidas pelo cliente para determinar o usuário responsável pelo registro.

---

# 20. Tratamento de falhas

As falhas deverão ser isoladas sempre que possível.

Uma falha no processamento de um comprovante não deverá afetar os pagamentos já registrados.

Exemplo:

```text
Comprovante A ─► Processado ─► Confirmado

Comprovante B ─► Falha

Comprovante C ─► Processando
```

Cada comprovante deverá possuir seu próprio estado.

---

# 21. Observabilidade

Os componentes deverão gerar informações suficientes para acompanhar:

* requisições;
* autenticação;
* upload;
* processamento;
* falhas;
* persistência;
* consultas.

O sistema deverá permitir identificar em qual etapa um comprovante apresentou falha.

Exemplo:

```text
Receipt #123
   │
   ├── Upload       ✓
   ├── Validation   ✓
   ├── Extraction   ✓
   ├── OCR          ✗
   └── Processing   FAILED
```

Informações sensíveis não deverão ser registradas desnecessariamente nos logs.

---

# 22. Organização lógica do backend

Independentemente da tecnologia escolhida, o backend deverá possuir separação de responsabilidades.

Uma organização conceitual:

```text
backend/
│
├── authentication/
│
├── receipts/
│   ├── upload/
│   ├── processing/
│   └── extraction/
│
├── payments/
│
├── beneficiaries/
│
├── institutions/
│
└── queries/
```

A organização física dos arquivos poderá ser diferente, desde que preserve a separação das responsabilidades.

---

# 23. Fluxo completo

O fluxo completo do sistema será:

```text
                    ┌─────────────┐
                    │    Usuário  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Cliente  │
                    └──────┬──────┘
                           │
                           │ Upload
                           ▼
                    ┌─────────────┐
                    │     API     │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
             ┌────────────┐ ┌──────────────┐
             │  Arquivo   │ │ Processamento│
             │  Original  │ │              │
             └────────────┘ └──────┬───────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │  Extração /  │
                             │ Interpretação│
                             └──────┬───────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │    Cliente   │
                             │   Revisão    │
                             └──────┬───────┘
                                    │
                              Confirmação
                                    │
                                    ▼
                             ┌──────────────┐
                             │     API      │
                             └──────┬───────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │ Banco dados  │
                             └──────────────┘
```

---

# 24. Princípios arquiteturais

A arquitetura deverá seguir os seguintes princípios:

### 24.1. Separação de responsabilidades

Cada componente deverá possuir uma responsabilidade clara.

### 24.2. Backend como autoridade

Regras de negócio, autorização e persistência deverão ser controladas pelo backend.

### 24.3. Arquivo separado dos dados estruturados

O comprovante original deverá possuir armazenamento apropriado e ser referenciado pelo registro estruturado.

### 24.4. Processamento desacoplado

O mecanismo de extração/interpretação deverá poder evoluir sem exigir mudanças significativas no restante da aplicação.

### 24.5. Confirmação explícita

Nenhum resultado automático deverá ser considerado um pagamento confirmado sem ação explícita do usuário.

### 24.6. Evolução incremental

A arquitetura deverá ser simples para o MVP, evitando complexidade distribuída desnecessária, mas permitindo evolução futura.

---

# 25. Decisões deixadas para a etapa de tecnologia

A arquitetura não define neste momento:

* linguagem do backend;
* framework do backend;
* framework do frontend;
* banco de dados específico;
* armazenamento de arquivos específico;
* provedor de OCR;
* provedor de IA;
* mecanismo de autenticação específico;
* provedor de infraestrutura;
* provedor de cloud;
* sistema de filas;
* ferramenta de observabilidade.

Essas decisões serão documentadas no próximo estágio.

---

# 26. Critérios de conclusão da arquitetura

A arquitetura será considerada definida quando:

* [ ] Os principais componentes estiverem identificados.
* [ ] As responsabilidades dos componentes estiverem definidas.
* [ ] O fluxo de upload estiver definido.
* [ ] O fluxo de processamento estiver definido.
* [ ] O fluxo de revisão estiver definido.
* [ ] O fluxo de confirmação estiver definido.
* [ ] A relação entre pagamento e comprovante estiver definida.
* [ ] A estratégia de persistência estiver definida conceitualmente.
* [ ] A estratégia de armazenamento de arquivos estiver definida conceitualmente.
* [ ] O isolamento dos dados dos usuários estiver definido.
* [ ] O tratamento de estados estiver definido.
* [ ] O processamento assíncrono estiver previsto quando necessário.
* [ ] As consultas estiverem separadas da apresentação.
* [ ] Os princípios arquiteturais estiverem documentados.
* [ ] As decisões que dependem da escolha de tecnologia estiverem explicitamente identificadas.

Após a conclusão deste documento, o projeto estará preparado para a definição das tecnologias que serão utilizadas na implementação.
