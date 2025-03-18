# Webscrapping python

## Descrição

Este é um projeto de avaliação da disciplina de programação python com banco de dados. O desafio era fazer um webscrapping onde fosse possível pegar os dados, armazenar em um banco de dados e consulta - los posteriormente.

O fórum de coleta de dados escolhito foi o Adrenaline para esse projeto.

## Pré-requisitos

- Python
- Docker

## Instalação

### 1. Clonar o repositório

Primeiro, clone o repositório para sua máquina local:

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Instalar as dependências

Instale as dependências do projeto com o seguinte comando:

```bash
pip install -r requirements.txt
```

### 3. Executar o contêiner do MongoDB

Para armazenar os dados coletados, vamos usar um banco de dados MongoDB. 
Execute o contêiner Docker do MongoDB:

```bash
docker run --name forum_mongo -d -p 27017:27017 mongo
```

Lembrando que esse projeto é para fins didáticos, nunca deixe as credencias do seu banco de dados exposta.

## Uso

### Coletar e Armazenar Dados

O script `forum_persistence.py` é responsável por coletar dados do Fórum Adrenaline e armazená-los no MongoDB.

#### Passo a Passo:

1. **Abra o arquivo `forum_persistence.py`**

2. **Execute o script `forum_persistence.py`**:
    ```bash
    python forum_persistence.py
    ```

### 4. Escolha do banco de dados e do Selenium


O MongoDB foi a escolha pois é um banco de dados NoSQL que permite a flexibilidade de armazenar dados e de manuseá-los depois e se caso o projeto for escalonavél, o mongo tem esse suporte melhor que os outros bancos.
O Selenium foi uma escolha para identificar o conteúdo da página. Assim conseguimos fazer a coleta das informações e salvá-las no MongoDB.
