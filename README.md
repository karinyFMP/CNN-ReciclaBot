# ♻️ ReciclaBot

O **ReciclaBot** é uma aplicação web interativa e moderna focada na classificação automática de resíduos. Utilizando conceitos de Visão Computacional e Deep Learning, o projeto simula a inferência de uma **Rede Neural Convolucional (CNN)** treinada no famoso dataset *TrashNet* para identificar qual é o tipo de lixo em uma imagem, auxiliando na triagem correta para a reciclagem.

## ✨ Funcionalidades

- **Classificação em Tempo Real:** Simulação de inferência de IA que classifica resíduos em 6 categorias.
- **Interface Moderna (Dark Mode):** Construída com Streamlit mas completamente customizada com CSS avançado para uma aparência "Cyber/Eco-tech".
- **Upload Simplificado:** Suporte para arrastar e soltar (Drag and Drop) imagens nos formatos JPG, PNG e WEBP.
- **Animações Fluidas:** Efeitos de carregamento, scan de imagem e elementos visuais flutuantes ("emojis" de lixo) em plano de fundo.
- **Dicas de Sustentabilidade:** O sistema fornece dicas práticas de descarte correto dependendo da categoria classificada.

## 🧠 Categorias Reconhecidas (TrashNet)

O modelo foi desenhado para reconhecer as seguintes categorias baseadas no dataset TrashNet:
1. **♻️ Plástico:** Lave antes de reciclar.
2. **🫙 Vidro:** Separe por cor e tenha cuidado para não quebrar.
3. **🔩 Metal:** Latas de alumínio e afins.
4. **📄 Papel:** Mantenha seco e limpo.
5. **📦 Papelão:** Caixas e embalagens (desmonte-as).
6. **🗑️ Geral:** Resíduos não recicláveis.

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
Certifique-se de ter o **Python 3.10+** instalado em sua máquina.

### Passo a passo

1. **Clone o repositório** (ou baixe os arquivos fonte):
   ```bash
   git clone https://github.com/seu-usuario/waste-classifier.git
   cd waste-classifier
   ```

2. **Crie e ative um ambiente virtual (recomendado):**
   No Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   No Linux/Mac:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   O projeto requer principalmente o Streamlit e a biblioteca Pillow.
   ```bash
   pip install -r requirements.txt
   ```
   *(Caso não exista o `requirements.txt`, você pode rodar: `pip install streamlit pillow`)*

4. **Execute a aplicação:**
   ```bash
   streamlit run app.py
   ```

5. **Acesse no navegador:**
   O Streamlit abrirá a página automaticamente no endereço `http://localhost:8501`.

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/)** - Linguagem base do projeto.
- **[Streamlit](https://streamlit.io/)** - Framework para construção da interface e servidor web.
- **HTML/CSS Nativo** - Injetado dinamicamente para sobrepor o design padrão do Streamlit, permitindo layouts em grade, ícones SVG vetoriais customizados e animações CSS (`@keyframes`).
- **[Pillow (PIL)](https://python-pillow.org/)** - Para processamento e manipulação das imagens carregadas.

## 💡 Como Funciona (UX/UI)

A experiência do usuário foi desenhada para ser o mais simples possível, seguindo 3 etapas:
1. **Envie uma foto:** Faça o upload ou arraste uma imagem do resíduo para a área de envio.
2. **A IA processa:** Uma animação de *scan* é ativada enquanto a (simulação da) CNN analisa os padrões visuais em milissegundos.
3. **Veja o resultado:** Um painel colorido ("Result Card") surge mostrando a categoria vencedora, a porcentagem de confiança e uma barra de progresso detalhada de todas as outras classes.

---
*Feito com 💚 para um futuro mais sustentável.*
