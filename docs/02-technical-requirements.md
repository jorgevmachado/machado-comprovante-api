# Comprovante

## 1. Objetivo

Este documento define os requisitos técnicos necessários para implementar o MVP do Comprovante.

Os requisitos são derivados do planejamento funcional do produto e têm como objetivo orientar as decisões de arquitetura e tecnologia.

Este documento não define tecnologias específicas. A escolha das tecnologias será realizada posteriormente, com base nos requisitos aqui definidos.

---

## 2. Plataforma

A aplicação deverá ser disponibilizada como uma aplicação web.

Deverá funcionar em:

* computadores;
* smartphones.

O mesmo backend deverá atender aos diferentes dispositivos.

A interface deverá ser responsiva e adequada para diferentes tamanhos de tela.

### 2.1. Desktop

A aplicação deverá permitir:

* seleção tradicional de arquivos;
* arrastar e soltar arquivos para envio.

### 2.2. Smartphone

A aplicação deverá permitir:

* seleção de arquivos;
* seleção de imagens;
* recebimento de arquivos compartilhados pelo sistema operacional.

O fluxo de compartilhamento deverá ser compatível com o funcionamento padrão de compartilhamento de arquivos dos sistemas operacionais móveis.

---

## 3. Autenticação

O sistema deverá possuir autenticação de usuários.

O acesso às funcionalidades do sistema deverá ser restrito a usuários autenticados.

O sistema deverá identificar o usuário responsável por cada pagamento registrado.

Os dados de um usuário não deverão ser acessíveis por outro usuário.

O mecanismo específico de autenticação será definido posteriormente.

---

## 4. Upload de comprovantes

O sistema deverá permitir o envio de comprovantes para processamento.

### 4.1. Formatos

O sistema deverá suportar, no mínimo:

* documentos PDF;
* imagens.

Os formatos de imagem suportados deverão ser definidos durante a implementação.

### 4.2. Validação

O sistema deverá validar o arquivo recebido antes do processamento.

Deverão ser consideradas, no mínimo:

* tipo do arquivo;
* tamanho do arquivo;
* integridade do arquivo.

Arquivos inválidos não deverão ser processados.

### 4.3. Armazenamento

O comprovante original deverá ser preservado após o registro do pagamento.

O sistema deverá permitir recuperar o comprovante posteriormente.

O arquivo original não deverá ser substituído pelo resultado do processamento.

---

## 5. Processamento de comprovantes

O sistema deverá processar o comprovante enviado para identificar informações relevantes do pagamento.

O processamento deverá suportar diferentes tipos de comprovante sem depender de um único formato visual.

O sistema deverá ser capaz de trabalhar com:

* PDF contendo texto;
* PDF contendo conteúdo que necessite de reconhecimento de texto;
* imagens.

O mecanismo utilizado para extração será definido posteriormente.

---

## 6. Extração de informações

O processamento deverá tentar identificar automaticamente:

* data do pagamento;
* favorecido;
* valor;
* instituição de origem;
* instituição de destino.

A extração deverá produzir dados estruturados para serem apresentados ao usuário.

A informação extraída deverá ser considerada uma sugestão e não um dado definitivo.

O sistema deverá permitir que uma informação não identificada seja posteriormente preenchida pelo usuário.

---

## 7. Identificação de instituições

O sistema deverá tentar identificar as instituições envolvidas no pagamento a partir das informações disponíveis no comprovante.

A identificação deverá considerar que uma mesma instituição poderá aparecer de formas diferentes nos documentos.

Exemplo:

```text
Itaú Unibanco S.A.
Itaú Unibank Ltda.
Itaú
```

Essas diferentes representações poderão corresponder à mesma instituição.

O sistema deverá permitir normalizar a informação apresentada ao usuário.

A estratégia de identificação e normalização será definida durante a arquitetura e implementação.

---

## 8. Revisão dos dados

Após o processamento, o sistema deverá apresentar os dados identificados para revisão.

Os dados deverão ser editáveis.

O usuário deverá conseguir:

* corrigir informações;
* preencher informações não identificadas;
* alterar informações identificadas incorretamente.

A aplicação não deverá registrar definitivamente um pagamento apenas com base no resultado automático do processamento.

---

## 9. Registro do pagamento

O pagamento somente deverá ser persistido após a confirmação explícita do usuário.

O registro deverá possuir, no mínimo:

* usuário responsável;
* data do pagamento;
* favorecido;
* valor;
* instituição de origem;
* instituição de destino;
* comprovante original;
* data de criação do registro.

O pagamento confirmado deverá possuir um identificador único.

---

## 10. Integridade dos dados

O sistema deverá garantir que os dados confirmados pelo usuário sejam os dados utilizados no registro definitivo.

Uma alteração realizada durante a revisão deverá substituir o valor extraído antes da persistência.

O sistema não deverá alterar silenciosamente os dados confirmados pelo usuário.

Os relacionamentos entre usuário, pagamento e comprovante deverão ser preservados.

---

## 11. Consultas

O sistema deverá permitir consultar os pagamentos registrados.

As consultas deverão suportar, no mínimo:

* período;
* favorecido;
* combinação de período e favorecido.

O sistema deverá permitir obter:

* quantidade de pagamentos;
* valor total dos pagamentos;
* maior pagamento;
* pagamentos de determinado favorecido;
* total pago para determinado favorecido.

---

## 12. Datas e valores

Os valores monetários deverão ser armazenados de forma que não ocorram erros decorrentes de representação de ponto flutuante.

As datas deverão possuir uma definição consistente de timezone.

A data do pagamento deverá ser diferente da data de criação do registro quando necessário.

Exemplo:

```text
data do pagamento: 10/09/2026
data de criação:   12/09/2026
```

---

## 13. Persistência

O sistema deverá possuir armazenamento persistente para:

* usuários;
* pagamentos;
* informações relacionadas aos favorecidos;
* informações relacionadas às instituições, quando aplicável;
* referência ao comprovante;
* metadados necessários ao processamento.

Os comprovantes deverão possuir armazenamento apropriado para arquivos.

Os dados estruturados do pagamento deverão possuir armazenamento apropriado para consultas e filtros.

---

## 14. Segurança

O sistema deverá proteger:

* credenciais de autenticação;
* dados dos usuários;
* informações dos pagamentos;
* comprovantes armazenados.

O acesso aos dados deverá respeitar o usuário autenticado.

Arquivos enviados não deverão ser disponibilizados publicamente sem autorização.

O sistema deverá validar os arquivos recebidos antes de processá-los ou armazená-los.

---

## 15. Tratamento de erros

O sistema deverá tratar, no mínimo, os seguintes cenários:

* arquivo inválido;
* formato não suportado;
* arquivo excedendo o tamanho permitido;
* falha na leitura do arquivo;
* falha na extração;
* comprovante sem informações suficientes;
* falha no armazenamento;
* falha no registro do pagamento.

Erros de processamento não deverão resultar em um pagamento registrado incorretamente.

O usuário deverá receber uma indicação clara quando o processamento não puder ser concluído automaticamente.

---

## 16. Processamento assíncrono

O processamento de comprovantes poderá ser realizado de forma assíncrona quando necessário.

A arquitetura deverá permitir que operações demoradas, como OCR ou processamento por serviços externos, não bloqueiem desnecessariamente a interface do usuário.

A necessidade de fila ou processamento assíncrono será definida durante a arquitetura.

---

## 17. Observabilidade

O sistema deverá possuir mecanismos para identificar falhas durante:

* autenticação;
* upload;
* processamento;
* extração;
* persistência;
* consultas.

Deverão existir logs suficientes para diagnosticar falhas sem registrar informações sensíveis desnecessariamente.

A solução específica de observabilidade será definida posteriormente.

---

## 18. Testes

O projeto deverá possuir testes automatizados.

Deverão ser considerados, no mínimo:

* testes unitários;
* testes de integração;
* testes dos principais fluxos da aplicação.

O fluxo de registro deverá ser testado considerando:

```text
Upload
  ↓
Processamento
  ↓
Extração
  ↓
Revisão
  ↓
Confirmação
  ↓
Persistência
```

Também deverão ser testados cenários de falha.

---

## 19. CI/CD

O projeto deverá possuir integração contínua.

O pipeline deverá executar automaticamente, no mínimo:

* validação do código;
* testes automatizados;
* verificações necessárias para garantir a qualidade do projeto.

O processo de publicação da aplicação deverá ser automatizado sempre que possível.

---

## 20. Compatibilidade

A aplicação deverá funcionar adequadamente nos principais navegadores modernos utilizados em computadores e smartphones.

A interface deverá ser responsiva.

O fluxo principal de registro deverá ser utilizável tanto por mouse/teclado quanto por interação por toque.

---

## 21. Performance

O sistema deverá priorizar uma experiência rápida no fluxo principal.

Operações que possam levar tempo significativo não deverão bloquear a interface sem necessidade.

O upload e processamento deverão possuir feedback visual adequado ao usuário.

O sistema deverá evitar processamento desnecessário de arquivos.

---

## 22. Escalabilidade

O MVP deverá ser dimensionado para uso pessoal e não deverá exigir uma arquitetura distribuída complexa inicialmente.

Entretanto, as decisões arquiteturais não deverão impedir uma futura evolução do sistema.

A solução deverá permitir posteriormente aumentar a capacidade de:

* armazenamento;
* processamento;
* número de pagamentos;
* número de usuários.

Não faz parte do MVP a otimização para grandes volumes.

---

## 23. Restrições do MVP

O MVP não deverá depender de:

* integração direta com bancos;
* Open Finance;
* API do WhatsApp;
* realização automática de pagamentos;
* aplicativos móveis nativos.

O processamento deverá ocorrer a partir dos comprovantes fornecidos pelo usuário.

---

## 24. Requisitos ainda não definidos

Os seguintes pontos deverão ser definidos nas próximas etapas:

* tecnologia do frontend;
* tecnologia do backend;
* banco de dados;
* armazenamento de arquivos;
* mecanismo de OCR;
* mecanismo de extração de informações;
* eventual utilização de IA/LLM;
* mecanismo de autenticação;
* infraestrutura;
* estratégia de deploy;
* mecanismo de filas, caso necessário;
* solução de observabilidade;
* limites de tamanho dos arquivos;
* formatos de imagem suportados;
* política de retenção dos arquivos.

Essas decisões não fazem parte deste documento e serão definidas nos documentos de arquitetura e tecnologia.

---

## 25. Critérios técnicos de conclusão

O conjunto de requisitos técnicos será considerado atendido quando:

* [ ] A aplicação funcionar em desktop.
* [ ] A aplicação funcionar em smartphone.
* [ ] O usuário conseguir autenticar.
* [ ] O usuário conseguir enviar PDF.
* [ ] O usuário conseguir enviar imagem.
* [ ] O sistema validar os arquivos recebidos.
* [ ] O comprovante original for preservado.
* [ ] O sistema conseguir processar um comprovante.
* [ ] O sistema conseguir extrair as informações disponíveis.
* [ ] Os dados extraídos forem apresentados ao usuário.
* [ ] O usuário conseguir editar os dados.
* [ ] O pagamento somente for persistido após confirmação.
* [ ] Os dados do pagamento forem persistidos corretamente.
* [ ] O pagamento puder ser consultado posteriormente.
* [ ] Os pagamentos puderem ser filtrados por período.
* [ ] Os pagamentos puderem ser pesquisados por favorecido.
* [ ] Os valores puderem ser agregados por período.
* [ ] Os valores puderem ser agregados por favorecido.
* [ ] Os principais fluxos possuírem testes automatizados.
* [ ] O CI estiver configurado.
* [ ] O sistema possuir tratamento adequado de erros.
* [ ] O sistema possuir mecanismos básicos de observabilidade.
* [ ] A aplicação estiver preparada para publicação.

Quando todos os requisitos necessários ao MVP estiverem atendidos, a implementação poderá ser considerada tecnicamente compatível com o planejamento definido.
