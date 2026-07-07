import streamlit as st
import requests

# 1. Configuração da página do Streamlit
st.set_page_config(page_title="Agente de Triagem Hospitalar", layout="wide")

# 2. Injeção de CSS customizado de forma correta (corrigindo o erro de sintaxe)
st.markdown("""
<style>
    .reportview-container {
        background: #f1f5f9;
    }
    .stTextArea textarea {
        height: 150px !important;
    }
    .css-11z5f9z {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Construção da Barra Lateral (Sidebar)
st.sidebar.title("🤖 Painel do Desenvolvedor")
st.sidebar.markdown("---")

# Inputs de configuração
api_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
modelo = st.sidebar.selectbox("Modelo Groq", ["llama-3.3-70b-versatile", "llama3-8b-8192"])

system_prompt = st.sidebar.text_area(
    "Prompt do Sistema (Persona)",
    value="""Você é o "Dr. Localiza", um assistente virtual de triagem do Hospital Central. Seu objetivo é coletar sintomas dos pacientes de forma empática, sugerir a especialidade médica recomendada e classificar o risco do paciente. 

Diretrizes Críticas:
1. Nunca dê diagnósticos fechados. Use termos como "pode estar associado a".
2. Se o usuário relatar dor no peito, falta de ar severa ou desmaio, instrua-o IMEDIATAMENTE a ir ao pronto-socorro ou ligar para o SAMU (192)."""
)

# 4. Área Principal do Chat
st.title("🏥 Agente de Atendimento Hospitalar")
st.subheader("Suporte e Triagem Preliminar")

# Inicializa o histórico de mensagens na sessão do Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual do hospital. Como posso te ajudar hoje? Por favor, me informe o que está sentindo."}
    ]

# Exibe as mensagens anteriores do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Lógica de envio da mensagem e integração com o Groq
if user_input := st.chat_input("Digite sua mensagem aqui..."):
    
    # Exibe a mensagem do usuário no chat
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Validação da API Key antes de chamar o servidor
    if not api_key:
        st.error("Por favor, insira sua Groq API Key no painel lateral para continuar.")
    else:
        # Chamada de API usando requests (para evitar dependências pesadas adicionais)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*Pensando...*")
            
            # Prepara o payload para o Groq
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Junta o prompt de sistema com o histórico da conversa
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
                bot_reply = response_data["choices"][0]["message"]["content"]
                
                # Atualiza a tela e o histórico com a resposta do bot
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ **Erro na comunicação com o Groq:** {str(e)}")