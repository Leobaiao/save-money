# SaveMoney 💰

Um aplicativo Android-first elegante e funcional para gestão financeira pessoal, desenvolvido com **Flet** (Python).

![Dashboard Preview](https://via.placeholder.com/800x400.png?text=SaveMoney+Dashboard)

## ✨ Funcionalidades

- **Dashboard Hero**: Visão geral do saldo, receitas e despesas com saudação personalizada.
- **Burn Rate Widget**: Acompanhamento em tempo real do seu limite diário de gastos baseado em metas.
- **Registro Rápido**: Adicione transações em segundos com o Bottom Sheet inteligente.
- **Gestão de Contas**: Controle de contas fixas, agendadas e recorrentes (mensais).
- **Análise Detalhada**: Gráficos de evolução anual e despesas por categoria.
- **Perfil Personalizável**: Nome e foto de perfil customizáveis.
- **SQLite Database**: Persistência de dados robusta e rápida.

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11 ou superior
- Pip (gerenciador de pacotes do Python)

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/app-save-money.git
   cd app-save-money
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o aplicativo:**
   ```bash
   flet run --android  # Para simular no Android
   flet run            # Para rodar no desktop/web
   ```

## 🏗️ Arquitetura

O projeto segue uma estrutura modular para facilitar a manutenção:

- `main.py`: Ponto de entrada e gerenciamento de navegação.
- `models/`: Definições de dados (Transaction, Category).
- `pages/`: Módulos de cada tela do aplicativo.
- `repositories/`: Camada de acesso ao banco de dados SQLite.
- `components/`: Componentes UI reutilizáveis (Header, EmptyState, etc).
- `theme/`: Configurações globais de cores e estilos.

## 🛠️ Qualidade de Código

Utilizamos **Ruff** para linting e **Black** para formatação. Para garantir os padrões antes de cada commit:

```bash
pip install pre-commit
pre-commit install
```

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
