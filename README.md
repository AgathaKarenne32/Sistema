# Sistema
Arquitetura de Software
Instruções
O sistema em anexo, é um sistema de IA que faz a avaliação se clientes de uma empresa do setor financeiro podem ou não ser clientes de cartão de crédito.

O sistema tem implementado o modelo de ML, o back-end e o front-end.

Sua missão (Atividade em Grupo) é encontrar a melhor arquitetura para esse modelo. Justifique sua escolha e teste se deu certo.

Entrega:

Um documento contendo:
a explicação do sistema,
escolha da arquitetura,
justificativa da escolha, e
resultados encontrados.
Código-fonte com a modificação realizada (zip).


# Explicação do sistema atual:
O sistema atual é uma aplicação web projetada para avaliar clientes de uma empresa do setor financeiro, determinando se eles podem ou não ser clientes de cartão de crédito, com base em um modelo de Machine Learning. Ele é composto por dois serviços principais: um backend construído com Python e FastAPI, e um frontend estático desenvolvido com HTML, CSS e JavaScript (jQuery). Ambos os serviços são conteinerizados usando Docker e orquestrados para execução local com Docker Compose.

# Arquitetura Atual: 
A arquitetura atual é um Monolito Conteinerizado com Docker Compose. É "monolítica" no sentido de que toda a lógica de negócio do backend, incluindo o carregamento e inferência do modelo de ML, reside em um único serviço. O Docker Compose é usado para facilitar o desenvolvimento e a implantação local.

# Pontos Fortes da Arquitetura Atual:
Simplicidade: Fácil de configurar, desenvolver e implantar para aplicações de pequeno a médio porte.

Desenvolvimento Local: O Docker Compose simplifica a execução de todo o sistema na máquina do desenvolvedor.

Base de Código Única: Mais fácil de gerenciar dependências e realizar mudanças globais na aplicação.
Limitações da Arquitetura Atual (para uma empresa financeira):

Escalabilidade: O backend é uma unidade única. Se a inferência do modelo de ML se tornar um gargalo ou o volume de requisições aumentar, é necessário escalar todo o serviço de backend, mesmo que outras partes não estejam sobrecarregadas. Modelos maiores consomem mais memória ao serem carregados na inicialização.

Confiabilidade/Resiliência: Uma falha em qualquer parte do backend (ex: um bug na lógica de inferência do ML) pode derrubar todo o serviço.

Gerenciamento de Modelos: A atualização do modelo de ML requer a reimplantação de todo o serviço de backend, o que pode ser mais lento e arriscado.

Otimização de Recursos: Recursos (CPU, memória) são alocados para todo o serviço de backend, mesmo que apenas uma parte esteja ativamente em uso.

Escolha da Melhor Arquitetura: Microsserviços com Serviço Dedicado de ML.Considerando que o sistema é para uma empresa do setor financeiro, as prioridades são alta escalabilidade, confiabilidade, performance e manutenibilidade. A arquitetura de Microsserviços com um Serviço Dedicado de Machine Learning (ML Model Serving) é a mais adequada.

Nesta arquitetura, o backend monolítico é dividido em serviços menores e independentes. A inferência do modelo de ML, em particular, é desacoplada em seu próprio serviço.

## Escolha da Nova Arquitetura

# Componentes da Nova Arquitetura:

Frontend Service: Permanece similar, servido por Nginx.
API Gateway (Opcional, mas Recomendado): Atua como um ponto de entrada único para todas as requisições do cliente, roteando-as para os serviços de backend apropriados, além de lidar com autenticação/autorização e balanceamento de carga.

Client Evaluation Service (FastAPI):
Responsável pela lógica de negócio principal da avaliação do cliente.
Não carrega o modelo de ML diretamente. Em vez disso, faz uma chamada de API para o Serviço de ML Model Serving.

ML Model Serving Service (FastAPI/TensorFlow Serving/etc.):
Um serviço dedicado exclusivamente a carregar e servir o modelo modelo_cluster_cartao_credito.pkl.
Expõe um endpoint de API (ex: /predict) que recebe as características do cliente e retorna a predição do cluster.
Pode ser otimizado para inferência de modelo (ex: uso de GPUs, frameworks específicos para serving de ML).
Permite o escalonamento independente da camada de inferência do modelo.
Facilita a atualização do modelo sem impactar outras partes do sistema.

Orquestração de Contêineres: Kubernetes é a plataforma ideal para gerenciar e orquestrar microsserviços em escala de produção, oferecendo auto-escalonamento, auto-recuperação, balanceamento de carga e atualizações contínuas.

## Justificativa da Escolha

# Escalabilidade Aprimorada:

Escalonamento Independente: O frontend, o serviço de avaliação de cliente e o serviço de ML podem ser escalados de forma independente com base em suas cargas específicas. Se a inferência do modelo se tornar um gargalo, apenas o serviço de ML precisa ser escalado, otimizando o uso de recursos.
Utilização Eficiente de Recursos: Os recursos (CPU, memória) são alocados precisamente onde são necessários, evitando o desperdício de recursos em partes do sistema que não estão sob alta demanda.

# Maior Confiabilidade e Resiliência:

Isolamento de Falhas: Uma falha no serviço de ML (ex: devido a um modelo corrompido) não derrubaria o serviço de avaliação de cliente ou o frontend. As outras partes do sistema poderiam continuar funcionando ou degradar graciosamente.
Auto-Recuperação (com Kubernetes): O Kubernetes pode detectar e substituir automaticamente instâncias de serviço com falha.
Manutenibilidade e Evolução Simplificadas:

Desacoplamento: Alterações no modelo de ML (ex: retreinamento, novas versões) podem ser implantadas no serviço de ML Model Serving sem afetar o serviço de avaliação de cliente.
Heterogeneidade Tecnológica: Diferentes serviços podem usar diferentes tecnologias ou linguagens de programação, se isso for benéfico para uma tarefa específica.

Bases de Código Menores: Cada serviço possui uma base de código menor e mais focada, facilitando o entendimento, desenvolvimento e manutenção por equipes de desenvolvimento.

Melhor Performance (Potencial):
Otimização Especializada: O serviço de ML Model Serving pode ser altamente otimizado para inferência, potencialmente usando frameworks específicos ou aceleração por hardware (GPU).
Redução de Latência: Ao separar as preocupações, serviços específicos podem ser otimizados para suas tarefas, contribuindo para uma resposta mais rápida.
Separação Clara de Responsabilidades: O gerenciamento e o serviço do modelo de ML são claramente separados da lógica de negócio principal.

Prontidão para o Futuro (Cloud-Native): Esta arquitetura se alinha bem com os princípios de cloud-native e é ideal para implantação em plataformas de nuvem usando serviços gerenciados de Kubernetes (GKE, EKS, AKS).

## Resultados Esperados (com a implementação da nova arquitetura)

Aumento da Escalabilidade do Sistema: O sistema será capaz de lidar com um volume muito maior de requisições de avaliação de clientes, pois os serviços de API e de inferência de ML podem ser escalados independentemente.

Maior Disponibilidade e Resiliência: O impacto de falhas será localizado, e o sistema será mais robusto contra interrupções de componentes individuais.
Ciclos de Implantação de Modelos Mais Rápidos: Novas versões do modelo de ML poderão ser implantadas e testadas isoladamente, reduzindo o risco e o tempo associados às atualizações do modelo.

Melhor Eficiência de Recursos: Os recursos (CPU, memória) serão alocados de forma mais precisa com base na demanda de cada serviço, potencialmente levando a economia de custos em infraestrutura.

Manutenibilidade Aprimorada e Autonomia das Equipes: As equipes de desenvolvimento poderão trabalhar em serviços individuais de forma mais independente, acelerando o desenvolvimento e reduzindo a sobrecarga de coordenação.

Preparação para Crescimento Futuro: O design modular facilita a adição de novas funcionalidades, a integração com outros sistemas ou a introdução de novos modelos de ML no futuro.

## Modificações:

# Apresento as modificações conceituais no código para ilustrar a arquitetura de microsserviços. Isso envolve a criação de um novo serviço para o modelo de ML e a adaptação do serviço de avaliação de cliente para se comunicar com ele.

1. Backend - Serviço de Avaliação de Cliente (Novo diretório: client_evaluation_service/)
Este serviço receberá os dados do frontend e fará uma chamada HTTP para o novo serviço de ML.

2. Backend - Serviço de ML Model Serving (Novo diretório: ml_model_service/)
Este é um novo serviço dedicado apenas ao carregamento e à inferência do modelo de Machine Learning.

3. Frontend 
O frontend não precisa de modificações no código JavaScript, pois ele continuará chamando o endpoint /avaliar do serviço de avaliação de cliente. A mudança de arquitetura é transparente para o frontend, desde que o API Gateway (ou o serviço de avaliação de cliente diretamente) esteja acessível na mesma URL.

4. docker-compose.yml (Atualizado para Microsserviços)
Este arquivo será modificado para orquestrar os três serviços (frontend, serviço de avaliação de cliente e serviço de ML).

5. Novos Dockerfiles e requirements.txt para cada serviço
Criar novos diretórios e arquivos para cada serviço

após todas as modificações a saidas foram as seguintes:
os comandos das modificações foram: 
 docker-compose build e  docker-compose up
![alt text](<Captura de tela 2025-05-24 192840.png>)

como tivemos a mensagem de erro WARN[0000] Found orphan containers ([sistema-backend-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
Este aviso indica que o contêiner antigo do seu backend monolítico ainda existe (ou está rodando) e precisa ser limpo. É provável que ele esteja ocupando a porta 8000!

Parar e Limpar Contêineres Antigos/Órfãos:
O docker-compose down é o comando que para e remove os contêineres, redes e volumes criados pelo docker-compose.yml. A flag --remove-orphans é perfeita para remover aquele contêiner sistema-backend-1 que está causando o problema.

executamos e ao final fizemos o  docker-compose up novamente
![alt text](<Captura de tela 2025-05-24 192853.png>)

essa foi a saida: 
![alt text](image.png)