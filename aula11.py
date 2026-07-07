import streamlit as st
import requests

# 1. Configuração da página do Streamlit
st.set_page_config(page_title="Agente de Triagem Hospitalar", layout="wide")

# 2. Estilização básica
st.markdown("""
<style>
    .reportview-container { background: #f1f5f9; }
    .stTextArea textarea { height: 150px !important; }
</style>
""", unsafe_allow_html=True)

# 3. Barra Lateral (Sidebar) com configurações do OpenRouter
st.sidebar.title("🤖 Configuração OpenRouter")
st.sidebar.markdown("---")

# Inputs de configuração
api_key = st.sidebar.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")

# Seleção de modelos populares do OpenRouter
modelo = st.sidebar.selectbox(
    "Escolha o Modelo", 
    [
        "meta-llama/llama-3-8b-instruct:free", 
        "meta-llama/llama-3.3-70b-instruct",
        "mistralai/mistral-7b-instruct:free"
    ]
)

system_prompt = st.sidebar.text_area(
    "Prompt do Sistema (Persona)",
    value="""Você é o "Dr. Localiza", um assistente virtual de triagem do Hospital Central. Seu objetivo é coletar sintomas dos pacientes de forma empática, sugerir a especialidade médica recomendada e classificar o risco do paciente. 

Diretrizes Críticas:
1. Nunca dê diagnósticos fechados. Use termos como "pode estar associado a".
2. Se o usuário relatar dor no peito, falta de ar severa ou desmaio, instrua-o IMEDIATAMENTE a ir ao pronto-socorro ou ligar para o SAMU (192)."""
)

# 4. Interface do Chat
st.title("🏥 Agente de Atendimento Hospitalar")
st.subheader("Suporte e Triagem Preliminar (via OpenRouter)")

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual do hospital. Como posso te ajudar hoje? Por favor, me informe o que está sentindo."}
    ]

# Exibe o histórico na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Envio de mensagens e Integração API
if user_input := st.chat_input("Digite sua mensagem aqui..."):
    
    # Mostra a mensagem do usuário
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Validação da chave
    if not api_key:
        st.error("Por favor, insira sua OpenRouter API Key na barra lateral.")
    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Analisando sintomas...*")
            
            # Endpoint oficial do OpenRouter
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            # Headers obrigatórios do OpenRouter
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501", # Necessário para o OpenRouter saber a origem
                "X-Title": "Agente Hospitalar Streamlit"
            }
            
            # Montagem do Payload
            payload = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt}
                ] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ],
                "temperature": 0.3
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                response_data = response.json()
                
                # Extrai a resposta do modelo
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    bot_reply = response_data["choices"][0]["message"]["content"]
                    message_placeholder.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    message_placeholder.markdown("⚠️ Resposta inesperada da API. Verifique os logs.")
                    
            except Exception as e:
                # Exibe detalhes do erro caso a chave seja inválida ou o modelo falhe
                message_placeholder.markdown(f"❌ **Erro no OpenRouter:** {str(e)}")
