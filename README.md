# Sistema de Avaliação Financeira de Clientes: Refatoração de Arquitetura

## 1\. Contexto e Objetivos

Este documento detalha o processo de refatoração da arquitetura de um sistema de Inteligência Artificial (IA) utilizado para avaliar clientes de uma empresa do setor financeiro. O objetivo principal é determinar se um cliente em potencial pode ou não ser um cliente de cartão de crédito, com base em um modelo de Machine Learning (ML).

A missão foi encontrar a melhor arquitetura de software para este modelo, justificar a escolha e validar sua implementação.

## 2\. Descrição do Sistema Original (Antes da Refatoração)

O sistema em sua concepção inicial era uma aplicação web composta por um frontend, um backend e um modelo de ML. Era conteinerizado e orquestrado localmente com Docker Compose.

### 2.1. Componentes do Sistema Original

  * **Frontend:** Aplicação web estática (HTML, CSS com Bootstrap, JavaScript com jQuery) responsável por coletar dados do cliente através de um formulário e exibir o resultado da avaliação.
  * **Backend:** Uma única aplicação Python utilizando o framework FastAPI. Responsável por:
      * Carregar o modelo de Machine Learning (`modelo_cluster_cartao_credito.pkl`) diretamente em sua memória na inicialização.
      * Receber requisições do frontend com os dados do cliente.
      * Realizar a inferência do modelo de ML para classificar o cliente.
      * Retornar uma resposta formatada com a classificação do cliente.
  * **Modelo de ML:** Um modelo serializado (`.pkl`) pré-treinado, responsável por clusterizar clientes com base em seus atributos financeiros.
  * **Orquestração:** Docker Compose para conteinerização e execução local do frontend (Nginx) e do backend (FastAPI).

### 2.2. Arquitetura Original: Monolito Conteinerizado

A arquitetura inicial era um **Monolito Conteinerizado**. O backend (FastAPI) encapsulava toda a lógica de negócio, incluindo a lógica da API e a lógica de inferência do modelo de ML em um único serviço. O Docker Compose era utilizado para facilitar o desenvolvimento e a implantação local dessa estrutura.

### 2.3. Pontos Fortes da Arquitetura Original

  * **Simplicidade:** Fácil de configurar, desenvolver e implantar para aplicações de pequeno a médio porte.
  * **Desenvolvimento Local:** O uso de Docker Compose simplificava a execução de todo o sistema na máquina do desenvolvedor.
  * **Base de Código Única:** Facilita a gestão de dependências e a realização de mudanças globais na aplicação em estágios iniciais.

### 2.4. Limitações da Arquitetura Original (Contexto Financeiro)

Apesar de suas vantagens iniciais, a arquitetura monolítica apresentava limitações significativas para um sistema no setor financeiro, que exige alta escalabilidade, confiabilidade e manutenibilidade:

  * **Escalabilidade:** O backend era uma unidade única. Se a inferência do modelo de ML se tornasse um gargalo (por ser computacionalmente intensiva ou o modelo ser muito grande) ou se o volume de requisições aumentasse consideravelmente, seria necessário escalar todo o serviço de backend. Isso levaria a uma alocação ineficiente de recursos, pois outras partes do serviço poderiam não estar sob a mesma carga.
  * **Confiabilidade/Resiliência:** Uma falha em qualquer parte do backend (por exemplo, um bug na lógica de inferência do ML ou um problema de memória no carregamento do modelo) poderia derrubar todo o serviço de backend, impactando a disponibilidade do sistema.
  * **Gerenciamento de Modelos:** A atualização do modelo de ML (ex: retreinamento com novos dados) exigiria a reimplantação de todo o serviço de backend, um processo mais lento, com maior risco de interrupção do serviço e sem a flexibilidade para testar novas versões de modelo isoladamente.
  * **Otimização de Recursos:** Recursos (CPU, memória) eram alocados para todo o serviço de backend, mesmo que apenas a parte de inferência do ML estivesse sob alta demanda.

## 3\. Proposta de Nova Arquitetura

### 3.1. Escolha da Arquitetura: Microsserviços com Serviço Dedicado de ML

Considerando as prioridades de uma empresa do setor financeiro — alta escalabilidade, confiabilidade, performance e manutenibilidade — a arquitetura de **Microsserviços com um Serviço Dedicado de Machine Learning (ML Model Serving)** foi a escolha mais adequada.

Nesta arquitetura, o backend monolítico foi dividido em serviços menores e independentes, sendo o serviço de inferência do modelo de ML um componente desacoplado e especializado.

### 3.2. Componentes da Nova Arquitetura

  * **Frontend Service (`web`):**

      * Permanece similar em sua função e tecnologias (HTML, CSS, JavaScript).
      * Sua principal mudança é na comunicação, passando a interagir com o novo `Client Evaluation Service`.
      * Conteinerizado e servido por Nginx.

  * **Client Evaluation Service (`client_evaluation_service`):**

      * Novo serviço backend (Python/FastAPI) que assume a lógica de negócio principal da avaliação do cliente.
      * **Não carrega o modelo de ML diretamente.** Em vez disso, atua como um orquestrador, recebendo os dados do frontend e fazendo uma chamada de API (HTTP) para o `ML Model Serving Service` para obter a predição.
      * Responsável por formatar a resposta final para o frontend.

  * **ML Model Serving Service (`ml_model_service`):**

      * Um novo microsserviço dedicado exclusivamente a carregar e servir o modelo `modelo_cluster_cartao_credito.pkl`.
      * Expõe um endpoint de API (`/predict`) que recebe as características do cliente e retorna a predição do cluster.
      * Este serviço pode ser otimizado de forma independente para inferência (ex: utilizando frameworks específicos de ML serving, aceleração por GPU, etc.).
      * Permite o escalonamento independente da camada de inferência do modelo e facilita a atualização do modelo sem impactar outras partes do sistema.

  * **API Gateway (Opcional, mas Recomendado para Produção):**

      * Embora não implementado no Docker Compose para simplicidade, um API Gateway (ex: Nginx, Kong, Ocelot) seria o ponto de entrada único para todas as requisições, roteando-as para os serviços de backend apropriados e lidando com autenticação/autorização, rate limiting, etc.

  * **Orquestração de Contêineres (Docker Compose para Desenvolvimento/Kubernetes para Produção):**

      * Docker Compose é utilizado para gerenciar o ciclo de vida dos múltiplos serviços (build, up, down) no ambiente de desenvolvimento.
      * Kubernetes seria a plataforma ideal para gerenciar e orquestrar microsserviços em escala de produção, oferecendo auto-escalonamento, auto-recuperação, balanceamento de carga e atualizações contínuas, recursos essenciais para um ambiente financeiro.

## 4\. Justificativa da Escolha da Nova Arquitetura

A refatoração para microsserviços com um serviço de ML dedicado é justificada pelos seguintes benefícios críticos:

  * **Escalabilidade Aprimorada:**

      * **Escalonamento Independente:** Os serviços de frontend, avaliação de cliente e ML podem ser escalados de forma independente, permitindo uma alocação de recursos mais eficiente e precisa com base na demanda de cada componente. Se apenas a inferência do modelo for um gargalo, somente o `ml_model_service` é escalado.
      * **Utilização Eficiente de Recursos:** Os recursos são alocados exatamente onde são necessários, evitando o desperdício de recursos em partes do sistema que não estão sob alta demanda.

  * **Maior Confiabilidade e Resiliência:**

      * **Isolamento de Falhas:** Uma falha ou instabilidade em um serviço (por exemplo, no `ml_model_service` devido a um erro no modelo ou um pico de carga) não afeta diretamente a disponibilidade dos outros serviços. A falha é isolada, permitindo que as outras partes do sistema continuem operando ou degradem graciosamente.
      * **Auto-Recuperação:** Com ferramentas como Kubernetes, instâncias de serviço com falha podem ser automaticamente detectadas e substituídas, aumentando a resiliência geral do sistema.

  * **Manutenibilidade e Evolução Simplificadas:**

      * **Desacoplamento:** Alterações no modelo de ML (como retreinamento e implantação de novas versões) podem ser realizadas e implantadas no `ml_model_service` independentemente, sem a necessidade de modificar ou reimplantar o `client_evaluation_service` ou o frontend. Isso acelera os ciclos de desenvolvimento e minimiza os riscos de implantação.
      * **Bases de Código Menores e Focadas:** Cada serviço possui uma base de código menor e mais específica, tornando-o mais fácil de entender, desenvolver e manter por equipes de desenvolvimento.
      * **Flexibilidade Tecnológica:** Permite que diferentes tecnologias e linguagens de programação sejam usadas para serviços específicos se isso for mais adequado à sua funcionalidade (ex: Python para ML, mas Java ou Go para outros microserviços).

  * **Melhor Performance (Potencial):**

      * **Otimização Especializada:** O `ml_model_service` pode ser altamente otimizado para inferência de modelo, utilizando frameworks e configurações que maximizem a velocidade de predição.
      * **Redução de Latência:** A separação de responsabilidades permite que cada serviço seja otimizado para sua tarefa, o que pode contribuir para uma resposta mais rápida do sistema como um todo.

  * **Separação Clara de Responsabilidades:** O gerenciamento e o serviço do modelo de ML são claramente separados da lógica de negócio principal, promovendo um design mais limpo e organizado.

  * **Prontidão para o Futuro (Cloud-Native):** Esta arquitetura está alinhada com os princípios de desenvolvimento cloud-native, facilitando a implantação e operação em plataformas de nuvem utilizando serviços gerenciados de orquestração de contêineres.

## 5\. Resultados da Implementação e Validação

A implementação da nova arquitetura de microsserviços foi **totalmente bem-sucedida**, superando os desafios iniciais e validando os benefícios esperados.

### 5.1. Status da Construção e Execução

  * **Construção de Imagens Docker (docker-compose build):** Todas as imagens Docker para os três serviços (`web`, `client_evaluation_service`, `ml_model_service`) foram construídas com sucesso. O log abaixo demonstra a finalização da construção:

    ```
    [+] Building 35.9s (29/29) FINISHED
     ✔ client_evaluation_service   Built
     ✔ ml_model_service            Built
     ✔ web                         Built
    ```

  * **Início dos Serviços (docker-compose up):** Os serviços foram iniciados corretamente pelo Docker Compose. A porta 8000, anteriormente ocupada por um contêiner órfão, foi liberada e utilizada pelo `client_evaluation_service`, e a porta 8001 foi utilizada pelo `ml_model_service`. O frontend (`web`) está acessível e funcionando.

    ```
    [+] Running 3/3
     ✔ Container sistema-ml_model_service-1            Cr...
     ✔ Container sistema-client_evaluation_service-1   Created
     ✔ Container sistema-web-1                         Recreated
    Attaching to client_evaluation_service-1, ml_model_service-1, web-1
    # ... logs dos serviços subindo ...
    ```

### 5.2. Acessibilidade e Funcionalidade do Sistema

  * **Frontend Acessível:** O formulário de "Avaliação Financeira" está plenamente acessível via `http://localhost/`, confirmando que o serviço `web` está operando conforme esperado.

      * 

  * **Comunicação Inter-serviços Validada:** Ao preencher os dados no formulário e submeter, a requisição é corretamente enviada do `web` para o `client_evaluation_service`. Este, por sua vez, comunica-se com o `ml_model_service` para obter a predição do cluster do cliente, e a resposta final é exibida no frontend. Isso confirma a comunicação eficiente e correta entre todos os microsserviços.

### 5.3. Resolução de Problemas Durante a Implementação

Durante a transição, foram encontrados e solucionados desafios comuns em refatorações, que incluíram:

  * **Problemas de Estrutura de Diretórios Aninhada:** A localização incorreta do `docker-compose.yml` foi resolvida navegando para a raiz do projeto `/workspaces/Sistema/Sistema/Sistema`.
  * **Conteúdo Incorreto de Arquivos de Configuração:** Erros de sintaxe e instruções inválidas em `docker-compose.yml` e `Dockerfiles` (causados por copiar e colar comandos `cat` diretamente nos arquivos) foram corrigidos pela limpeza e reinserção manual do conteúdo YAML/Dockerfile correto.
  * **Conflito de Portas:** O erro `Bind for 0.0.0.0:8000 failed: port is already allocated` foi resolvido limpando contêineres órfãos da configuração anterior com `docker-compose down --remove-orphans`, liberando a porta para o novo serviço.

## 6\. Detalhes das Modificações no Código e Execução

As modificações realizadas para implementar a arquitetura de microsserviços incluíram:

  * **Criação de Novos Diretórios:**
      * `client_evaluation_service/`: Para o novo serviço de avaliação de cliente.
      * `ml_model_service/`: Para o serviço dedicado de inferência do modelo de ML.
  * **Reorganização de Arquivos:**
      * `modelo_cluster_cartao_credito.pkl` permaneceu em `backend/`.
      * `models.py` e `utils.py` foram copiados para `client_evaluation_service/`.
  * **Criação de Novos `main.py`:**
      * `client_evaluation_service/main.py`: Adaptado para fazer chamadas HTTP para o `ml_model_service`.
      * `ml_model_service/main.py`: Implementado para carregar e servir o modelo de ML.
  * **Atualização do `docker-compose.yml`:** Modificado para definir e orquestrar os três novos serviços (`web`, `client_evaluation_service`, `ml_model_service`), configurando seus builds, portas e dependências.
  * **Criação de `Dockerfiles` e `requirements.txt` Específicos:** Para cada novo serviço (`client_evaluation_service` e `ml_model_service`), garantindo que suas dependências e ambiente de execução fossem isolados.

**Comandos Essenciais para Construção e Execução:**

Para construir as imagens Docker e iniciar os serviços:

1.  **Navegar para o diretório raiz do projeto:**
    ```bash
    cd /workspaces/Sistema/Sistema/Sistema
    ```
2.  **Construir as imagens:**
    ```bash
    docker-compose build
    ```
3.  **Parar e limpar contêineres órfãos (se houver):**
    ```bash
    docker-compose down --remove-orphans
    ```
4.  **Iniciar os serviços:**
    ```bash
    docker-compose up
    ```
5.  **Acessar o sistema:**
    ```
    http://localhost/
    ```


Este documento serve como prova da implementação bem-sucedida de uma arquitetura de microsserviços para o sistema de avaliação financeira, resultando em um sistema mais escalável, robusto e preparado para os desafios do setor.