# ♻️ ReciclaBot — CNN Waste Classifier

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/karinyFMP/CNN-ReciclaBot/blob/main/treinamento/treinamento_ReciclaBot.ipynb)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-blue?logo=github)](https://karinyFMP.github.io/CNN-ReciclaBot/)

> **Demo ao vivo** — sem instalar nada, basta abrir o link:
> **[karinyFMP.github.io/CNN-ReciclaBot](https://karinyFMP.github.io/CNN-ReciclaBot/)**

---

## O que é este projeto?

O **ReciclaBot** utiliza **Transfer Learning com MobileNetV2** treinado em um *super dataset* (TrashNet + Garbage Real World) para classificar imagens de resíduos em 6 categorias. O modelo roda **100% no navegador** via **TensorFlow.js** — sem servidor, sem dependências Python.

---

## 🌐 Como usar (sem instalar nada)

1. Acesse o link do GitHub Pages acima.
2. Na página inicial (hub), escolha:
   - **🎬 Ver Apresentação** — slides sobre o projeto, arquitetura MobileNetV2, pipeline, métricas e tecnologias.
   - **🤖 Testar o Modelo** — demo ao vivo com câmera ou upload de imagem.
3. Na demo, clique em **Ativar câmera** ou faça upload de uma imagem de resíduo.

---

## 🏷️ Categorias Reconhecidas

| Categoria | Classe | Dica de descarte |
|---|---|---|
| 📦 Papelão | `cardboard` | Desmonte as caixas. Remova fitas e plásticos. |
| 🫙 Vidro | `glass` | Separe por cor. Nunca misture com cerâmica. |
| 🥫 Metal | `metal` | Amasse latas. O alumínio é infinitamente reciclável! |
| 📄 Papel | `paper` | Mantenha seco e limpo. |
| ♻️ Plástico | `plastic` | Lave antes de reciclar. Remova tampas. |
| 🗑️ Lixo Geral | `trash` | Não reciclável. Tente reduzir o uso. |

---

## 🧠 Arquitetura — Transfer Learning com MobileNetV2

```
Input (224×224×3)
    ↓
Rescaling(1/127.5, offset=-1)   ← normaliza para [-1, 1], padrão MobileNet
    ↓
MobileNetV2 (ImageNet, congelada) ← ~2.2M parâmetros NÃO treináveis
    ↓
GlobalAveragePooling2D
    ↓
Dropout(0.2)
    ↓
Dense(6, softmax)               ← saída: probabilidade das 6 classes
```

### Por que MobileNetV2 + Transfer Learning?

| CNN do Zero | Transfer Learning |
|---|---|
| Treina todos os pesos do zero | Reutiliza pesos aprendidos no ImageNet |
| Requer muito dado e muitas épocas | Converge em poucas épocas (aqui: 10) |
| ~59% de acurácia no TrashNet | Significativamente melhor com menos tempo |

---

## 🗂️ Super Dataset

O notebook mescla automaticamente dois datasets via **KaggleHub**:

| Dataset | Descrição | Prefixo |
|---|---|---|
| **TrashNet** | Imagens de estúdio com fundo branco — limpas, controladas | `tn_` |
| **Garbage Real World** | Fotos com fundos reais (mãos, rua, grama) | `rw_` |

Split: 80% treino / 20% validação · Shuffle seed=123 · Batch=32

---

## 📊 Configuração de Treinamento

| Parâmetro | Valor |
|---|---|
| Épocas | 10 |
| Batch Size | 32 |
| Input Shape | 224 × 224 × 3 |
| Optimizer | Adam (lr=0.001) |
| Loss | Sparse Categorical Crossentropy |
| Augmentation | Flip H+V · Rotate 20% · Zoom 20% |
| Ambiente | Google Colab (GPU) |

---

## 🧠 Como Treinar (Google Colab)

O notebook está em [`treinamento/treinamento_ReciclaBot.ipynb`](treinamento/treinamento_ReciclaBot.ipynb).

Clique no badge **Open in Colab** no topo deste README.

### Célula 1 — Instalação
```bash
pip install tf-keras tensorflowjs==4.22.0 kagglehub "numpy<2.0"
```
> ⚠️ Reinicie a sessão após a Célula 1 antes de executar a Célula 2.

### Célula 2 — Treinamento
Baixa automaticamente os dois datasets do Kaggle, mescla em super dataset, aplica augmentation e treina o MobileNetV2 por 10 épocas. Salva `modelo_trashnet.h5`.

### Célula 3 — Conversão para TF.js
Carrega o `.h5` e converte para `modelo_tfjs/` com `tensorflowjs_converter`. Baixe a pasta e substitua a do repositório.

---

## 📁 Estrutura do Projeto

```
CNN-ReciclaBot/
├── index.html              ← Hub / página inicial (GitHub Pages entry point)
├── style.css               ← Design system compartilhado (Cyber/Eco-tech)
│
├── apresentacao/           ← Apresentação animada (HTML/CSS/JS puro)
│   ├── index.html          ← Pipeline, arquitetura, métricas, tecnologias
│   ├── app.js
│   └── style.css
│
├── webapp/                 ← Demo interativa (câmera + upload + TF.js)
│   ├── index.html
│   ├── app.js              ← MobileNetV2 via TF.js, rescaling [-1, 1] interno
│   └── style.css
│
├── modelo_tfjs/            ← Modelo convertido para TensorFlow.js
│   ├── model.json
│   └── group1-shard*.bin
│
└── treinamento/            ← Notebook de treinamento (Google Colab)
    └── treinamento_ReciclaBot.ipynb
```

---

## 🛠️ Tecnologias

| Tecnologia | Papel |
|---|---|
| **TF-Keras + MobileNetV2** | Transfer Learning com base ImageNet |
| **KaggleHub** | Download e mesclagem automática dos datasets |
| **TensorFlow.js 4.20** | Inferência no browser via WebGL |
| **Google Colab** | Ambiente de treino com GPU gratuita |
| **HTML / CSS / JS** | Site estático 100%, sem frameworks |
| **GitHub Pages** | Hospedagem gratuita |

---

## ⚙️ Configurar GitHub Pages

1. Vá em **Settings → Pages** no repositório.
2. Em *Source*, selecione branch `main`, pasta `/ (root)`.
3. Salve — o link público será gerado automaticamente.

---

*Feito com 💚 para um futuro mais sustentável.*
