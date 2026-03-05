# Guia de Contribuição 🤝

Obrigado por se interessar em contribuir para o SaveMoney! Siga estas diretrizes para manter a qualidade do projeto.

## 🌿 Fluxo de Branches

- `main`: Versão estável em produção.
- `develop`: Integração de novas funcionalidades.
- `feature/*`: Novas funcionalidades ou melhorias.
- `bugfix/*`: Correções de bugs.

## 📝 Padrões de Código

1. **Linting & Formatação**: Rode `ruff check .` e `black .` antes de subir suas mudanças.
2. **Tipagem**: Sempre que possível, utilize *type hints* para novos parâmetros e funções.
3. **Async/Await**: O Flet é assíncrono por natureza. Certifique-se de usar `page.run_task` ou `await` corretamente em eventos de UI.

## 🧪 Como Testar

Atualmente estamos implementando testes unitários com `pytest`. Para rodar os testes disponíveis:

```bash
pytest
```

## 📬 Abrindo um Pull Request

1. Garanta que sua branch está atualizada com a `develop`.
2. Forneça uma descrição clara das mudanças.
3. Inclua screenshots caso tenha alterado a interface visual.

---
SaveMoney Team 💰
