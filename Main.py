import streamlit as st
from supabase import create_client, Client

# Configuração da página do Streamlit
st.set_page_config(page_title="Quem é Quem? - Jogo", page_icon="🕵️‍♂️", layout="centered")

# 1. CONEXÃO COM O SUPABASE
# Buscando as credenciais direto dos Secrets do Streamlit por segurança
if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
else:
    # Caso você ainda não tenha colocado nos Secrets, coloque suas strings aqui temporariamente:
    SUPABASE_URL = "https://tuymyyxguujeuxwgrssm.supabase.co/rest/v1/"
    SUPABASE_KEY = "sb_publishable_mE_GPQgHRnkF1bp241SkyA_Ijynueb5"

# Inicializa o cliente do Supabase
@st.cache_resource
def conectar_banco():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = conectar_banco()
except Exception as e:
    st.error("Erro ao conectar ao banco de dados. Verifique suas credenciais.")

# 2. CONTROLE DE TELA (ESTADO DO JOGO)
if "tela" not in st.session_state:
    st.session_state.tela = "login"
if "meu_nick" not in st.session_state:
    st.session_state.meu_nick = ""

# --- TELA 1: LOGIN / ENTRAR NA SALA ---
if st.session_state.tela == "login":
    st.title("🕵️‍♂️ Jogo: Quem é Quem?")
    st.subheader("Entre na sala para começar")
    
    nick = st.text_input("Escolha seu Nick Secreto:", placeholder="Ex: NinjaAnonimo")
    
    if st.button("Entrar no Jogo"):
        if nick.strip() != "":
            st.session_state.meu_nick = nick.strip()
            st.session_state.tela = "jogo"
            st.rerun()
        else:
            st.error("Por favor, digite um nick válido!")

# --- TELA 2: SALA DO JOGO ---
elif st.session_state.tela == "jogo":
    st.title("🎮 Sala do Jogo")
    st.write(f"Jogador atual: **{st.session_state.meu_nick}**")
    
    st.markdown("---")
    
    # Interface de envio de mensagens
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pergunta = st.text_input("💬 Enviar Pergunta/Pista:", placeholder="Escreva sua pista aqui...")
        if st.button("Enviar Mensagem"):
            if pergunta.strip() != "":
                try:
                    # Monta os dados com as colunas EXATAMENTE iguais ao Supabase (minúsculas)
                    dados = {
                        "jogador": st.session_state.meu_nick,
                        "texto": pergunta.strip()
                    }
                    
                    # Envia para a tabela "Mensagens" (com M maiúsculo) no esquema public
                    supabase.table("Mensagens").insert(dados).execute()
                    
                    st.success("Mensagem enviada com sucesso!")
                except Exception as erro:
                    st.error(f"Erro ao enviar: {erro}")
            else:
                st.warning("Digite alguma mensagem antes de clicar em enviar!")
                
    with col2:
        st.write("") # Espaçador
        st.write("") 
        if st.button("Sair da Sala", type="secondary"):
            st.session_state.tela = "login"
            st.session_state.meu_nick = ""
            st.rerun()
            
