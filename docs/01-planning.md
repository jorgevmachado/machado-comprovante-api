# Comprovante

## 1. Visão do produto

O Comprovante é uma aplicação pessoal para registrar pagamentos a partir dos comprovantes gerados por instituições bancárias.

A aplicação deve ser simples e rápida, permitindo que o usuário envie um comprovante, confira as informações identificadas e registre o pagamento sem precisar preencher manualmente todos os dados.

A aplicação deverá funcionar tanto em computadores quanto em smartphones.

### 1.1. Desktop

No computador, o usuário deverá conseguir enviar um comprovante utilizando arrastar e soltar (drag and drop), além da seleção tradicional de arquivos.

### 1.2. Smartphone

No smartphone, o usuário deverá conseguir compartilhar um comprovante diretamente pelo menu de compartilhamento do sistema operacional.

O fluxo esperado é:

**WhatsApp → Compartilhar → Comprovante → Processamento → Confirmação**

A aplicação deverá funcionar como uma etapa intermediária entre o recebimento do comprovante e seu registro, reduzindo ao mínimo o trabalho manual.

### 1.3. Princípios

O produto deverá seguir três princípios principais:

1. **Simplicidade** — o usuário deve conseguir registrar um pagamento sem precisar aprender a utilizar a aplicação.
2. **Rapidez** — o caminho entre enviar um comprovante e registrar o pagamento deve ser curto.
3. **Mobile e desktop** — o mesmo fluxo principal deve funcionar adequadamente no computador e no smartphone.

---

## 2. Problema

Atualmente, após realizar o pagamento de uma conta, o usuário precisa localizar o comprovante e compartilhá-lo manualmente em um grupo do WhatsApp.

Esse processo se repete diversas vezes durante o mês e não gera um histórico estruturado dos pagamentos realizados.

Os comprovantes ficam distribuídos entre conversas, arquivos e aplicativos bancários, dificultando a consulta posterior.

O Comprovante deverá reduzir esse trabalho ao permitir que o próprio comprovante seja utilizado como entrada para o registro do pagamento.

---

## 3. Objetivo

Permitir que o usuário envie um comprovante de pagamento, tenha suas principais informações identificadas automaticamente, revise e corrija essas informações e confirme o registro do pagamento.

Após a confirmação, o pagamento deverá ficar disponível em um histórico consultável.

O sistema deverá permitir consultas que ajudem o usuário a entender seus pagamentos sem se transformar em um sistema financeiro completo.

---

## 4. Informações do pagamento

Cada pagamento deverá possuir, no mínimo, as seguintes informações:

* data do pagamento;
* favorecido;
* valor;
* instituição de origem;
* instituição de destino;
* comprovante original;
* data de criação do registro.

### 4.1. Favorecido

Representa a pessoa ou instituição que recebeu o pagamento.

O nome extraído do comprovante poderá ser alterado pelo usuário antes da confirmação.

Exemplo:

```text
Nome extraído:
Neoenergia Distribuição Brasília

Nome confirmado:
Neoenergia
```

### 4.2. Instituição de origem

Representa a instituição bancária de onde o dinheiro foi enviado.

O nome extraído do comprovante poderá ser alterado pelo usuário antes da confirmação.

Exemplo:

```text
Nome extraído:
Itaú Unibank Ltda

Nome confirmado:
Itaú
```

### 4.3. Instituição de destino

Representa a instituição bancária para a qual o valor foi enviado.

---

## 5. Fluxo de registro do pagamento

O registro de um pagamento será realizado em duas etapas principais:

1. extração das informações;
2. confirmação pelo usuário.

### 5.1. Envio do comprovante

O usuário deverá conseguir enviar um comprovante através de:

* arrastar e soltar no computador;
* seleção de arquivo no computador;
* seleção de arquivo ou imagem no smartphone;
* compartilhamento de um arquivo ou imagem pelo sistema operacional do smartphone.

Após o envio, o sistema deverá processar o comprovante e identificar as informações disponíveis.

### 5.2. Extração

O sistema deverá tentar identificar automaticamente as informações relevantes do comprovante, incluindo:

* data do pagamento;
* favorecido;
* valor;
* instituição de origem;
* instituição de destino.

A extração automática não será considerada definitiva.

### 5.3. Revisão

Após o processamento, o sistema deverá apresentar ao usuário as informações identificadas.

Os dados deverão ser apresentados em campos editáveis.

O usuário poderá corrigir qualquer informação antes de confirmar o pagamento.

A forma de apresentação, como modal ou página dedicada, será definida durante a implementação da interface.

### 5.4. Confirmação

Somente após o usuário confirmar os dados o pagamento deverá ser registrado definitivamente.

O fluxo principal será:

**Enviar comprovante → Extrair informações → Revisar → Corrigir → Confirmar → Registrar**

O sistema não deverá considerar um pagamento como registrado apenas porque o comprovante foi enviado.

---

## 6. Consultas

Após os pagamentos serem registrados, o usuário deverá conseguir consultar:

1. quantidade de contas pagas em determinado mês;
2. valor total gasto em determinado mês;
3. qual foi a conta mais cara paga em determinado período;
4. pesquisar pelo nome do favorecido para verificar se ele já foi pago;
5. consultar quanto foi pago para determinado favorecido em determinado mês;
6. consultar quanto foi pago para determinado favorecido durante determinado ano.

### 6.1. Exemplos de consultas

O sistema deverá permitir obter respostas para perguntas como:

> Quantas contas paguei em setembro?

> Quanto gastei em setembro?

> Qual foi a conta mais cara que paguei em setembro?

> Já paguei a conta da Neoenergia este mês?

> Quanto paguei para a Neoenergia em setembro?

> Quanto paguei para a Neoenergia em 2026?

---

## 7. Escopo do MVP

O MVP deverá permitir:

* autenticação do usuário;
* envio de comprovantes;
* processamento dos comprovantes;
* extração automática das informações;
* revisão das informações extraídas;
* edição dos dados pelo usuário;
* confirmação do pagamento;
* armazenamento do pagamento;
* consulta do histórico;
* pesquisa por favorecido;
* filtros por período;
* consulta de valores por período;
* consulta de valores por favorecido.

O MVP deverá funcionar em computadores e smartphones.

---

## 8. Fora do escopo

Não fazem parte do MVP:

* integração direta com bancos;
* Open Finance;
* realização de pagamentos;
* conciliação bancária;
* controle de saldo;
* orçamento;
* categorias financeiras;
* cartão de crédito;
* investimentos;
* notificações;
* aplicativo mobile nativo;
* múltiplos usuários;
* integração com a API do WhatsApp;
* processamento automático de pagamentos;
* processamento em lote de vários comprovantes;
* funcionalidades avançadas de gestão financeira.

Qualquer funcionalidade que não esteja explicitamente definida no escopo do MVP será considerada fora do escopo.

---

## 9. Critérios de conclusão

O MVP será considerado concluído quando:

* [ ] O usuário conseguir autenticar.
* [ ] O usuário conseguir enviar um comprovante pelo computador.
* [ ] O usuário conseguir enviar um comprovante pelo smartphone.
* [ ] O sistema conseguir processar um comprovante.
* [ ] O sistema conseguir apresentar os dados extraídos.
* [ ] O usuário conseguir corrigir os dados extraídos.
* [ ] O usuário conseguir confirmar o pagamento.
* [ ] O pagamento confirmado for persistido.
* [ ] O usuário conseguir consultar os pagamentos.
* [ ] O usuário conseguir pesquisar por favorecido.
* [ ] O usuário conseguir consultar pagamentos por período.
* [ ] O usuário conseguir consultar valores por favorecido.
* [ ] O sistema funcionar adequadamente em desktop e smartphone.
* [ ] Os testes automatizados estiverem implementados.
* [ ] O CI estiver configurado.
* [ ] A aplicação estiver publicada.
* [ ] A documentação final estiver atualizada.

Quando todos os itens acima estiverem concluídos, o MVP estará encerrado.
