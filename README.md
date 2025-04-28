# Sistema de Cadastro de Produtos para Manutenção

Um sistema completo em Python para cadastro e gerenciamento de solicitações de manutenção de produtos, implementado com interface gráfica PyQt5 e banco de dados SQL Server.

## Recursos

- **Autenticação e controle de acesso**
  - Sistema de login com diferentes níveis de permissões
  - Limite de 2 administradores
  - Registro de ações dos usuários (logs)
  - Visualização de usuários online

- **Gestão de Solicitações**
  - Cadastro de clientes e produtos
  - Numeração automática de Ordens de Serviço (formato mmAA-n)
  - Anexo de imagens para cada solicitação
  - Controle de status e prioridade
  - Diagnóstico e histórico de manutenção

- **Interface Amigável**
  - Organização por abas
  - Coloração visual por status e prioridade
  - Visualização e manipulação de imagens
  - Sistema de busca integrado

## Estrutura de Diretórios

```
sistema_manutencao/
│
├── main.py                  # Ponto de entrada do aplicativo
├── requirements.txt         # Dependências do projeto
│
├── database/                # Camada de acesso a dados
│   ├── __init__.py
│   ├── database.py          # Classe principal do banco de dados
│   └── schema.py            # Definição do esquema do banco
│
├── models/                  # Classes de modelo/entidades
│   └── __init__.py
│
├── ui/                      # Interface do usuário
│   ├── __init__.py
│   ├── login_window.py      # Tela de login
│   ├── main_window.py       # Janela principal e navegação
│   ├── usuarios_window.py   # Gerenciamento de usuários
│   ├── recepcao_window.py   # Tela de recepção
│   ├── manutencao_window.py # Tela de manutenção
│   └── logs_widget.py       # Widget para exibição de logs
│
└── utils/                   # Utilitários e ferramentas auxiliares
    ├── __init__.py
    └── helpers.py           # Funções auxiliares
```

## Requisitos

- Python 3.6+
- PyQt5

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/sistema-manutencao.git
   cd sistema-manutencao
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute o sistema:
   ```
   python main.py
   ```
4. Sempre verifique a conexão do banco de dados antes de iniciar o sistema:
   ```
              # Configuração de conexão com SQL Server
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=(PEDIR CONEXAO DO BANCO PARA ADM);'
                'DATABASE=manutencao;'
                'Trusted_Connection=yes;'
                'TrustServerCertificate=yes;'
            )
   ```


## Usuário Padrão

O sistema vem com um usuário administrador padrão:
- **Usuário**: admin
- **Senha**: admin

Recomendamos criar novos usuários após o primeiro acesso.

## Telas Principais

### Login
Gerencia a autenticação dos usuários.

### Recepção
Responsável pelo cadastro inicial das solicitações, incluindo dados do cliente, descrição do problema e gerenciamento de imagens.

### Manutenção
Permite acompanhar e atualizar o status das solicitações, registrar diagnósticos e finalizar os processos.

### Logs e Usuários Online
Exibe um registro das ações realizadas no sistema e os usuários atualmente conectados.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está sob a licença MIT.
