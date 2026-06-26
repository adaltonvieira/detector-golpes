# Detector de Mensagens Suspeitas — Anti-golpe com IA

Aplicacao que analisa mensagens (SMS, e-mail, WhatsApp) e avalia o risco de golpe / phishing, combinando verificacoes de seguranca deterministicas com o raciocinio de um LLM (Groq + Llama).

Projeto do cruzamento IA Generativa + Ciberseguranca + Prompt Engineering.

## Como funciona

1. Verificacoes deterministicas (Python): extrai links (inclusive dominios sem http://), detecta encurtadores, linguagem de urgencia e pedidos de dados sensiveis (CPF, senha, PIX...).
2. Analise de dominio: detecta IP no lugar de nome, excesso de hifens, terminacoes (TLDs) suspeitas e marcas conhecidas usadas em subdominios falsos (ex: bradesco.com.golpe.xyz).
3. O LLM, guiado por exemplos (few-shot), recebe a mensagem + os sinais tecnicos e devolve um JSON estruturado: nivel de risco, sinais, explicacao para leigos e recomendacao.

Essa combinacao "regras + IA" e o diferencial: os sinais objetivos sao confiaveis, e o LLM agrega raciocinio e clareza.

## Tecnicas aplicadas

- Prompt Engineering: few-shot com exemplos rotulados de golpes brasileiros para calibrar o nivel de risco.
- Ciberseguranca: deteccao de padroes classicos de phishing (subdominio falso, TLD abusado, link encurtado).
- Saida estruturada: response_format JSON para resultado sempre parseavel.

## Estrutura

    detector-golpes/
    ├── src/
    │   ├── detector.py   # regras + analise de dominio + LLM (modulo reutilizavel)
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
