# Detector de Mensagens Suspeitas — Anti-golpe com IA

Aplicacao que analisa mensagens (SMS, e-mail, WhatsApp) e avalia o risco de golpe / phishing, combinando verificacoes de seguranca deterministicas com o raciocinio de um LLM (Groq + Llama).

Projeto do cruzamento IA Generativa + Ciberseguranca: as regras detectam sinais objetivos (links encurtados, urgencia, pedido de dados sensiveis) e o LLM explica o risco em linguagem simples.

## Como funciona

1. Verificacoes deterministicas (Python): extrai URLs, detecta encurtadores, linguagem de urgencia e pedidos de dados sensiveis (CPF, senha, PIX...).
2. O LLM recebe a mensagem + os sinais tecnicos e devolve um JSON estruturado: nivel de risco, sinais, explicacao para leigos e recomendacao.

Essa combinacao "regras + IA" evita depender so do modelo: os sinais objetivos sao confiaveis, e o LLM agrega raciocinio e clareza.

## Estrutura

    detector-golpes/
    ├── src/
    │   ├── detector.py   # regras deterministicas + chamada ao LLM (modulo reutilizavel)
    │   └── app.py        # interface web (Streamlit)
    └── requirements.txt

## Pré-requisitos

Uma chave de API gratuita do Groq (console.groq.com, sem cartao de credito).

## Como rodar

    git clone https://github.com/adaltonvieira/detector-golpes.git
    cd detector-golpes
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Crie um arquivo `.env` na raiz com sua chave:

    GROQ_API_KEY=sua_chave_aqui

Suba o app:

    streamlit run src/app.py

## Tecnologias

Python, Groq (Llama 3.1), Streamlit, python-dotenv
