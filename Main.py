import streamlit as st
from supabase import create_client, Client

# ==========================================
# COLQUE SUAS CHAVES DO SUPABASE AQUI DENTRO:
# ==========================================
SUPABASE_URL = "https://tuymyyxguujeuxwgrssm.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_mE_GPQgHRnkF1bp241SkyA_Ijynueb5"
# ==========================================

# Conecta o jogo ao banco de dados do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração da página
st.set_page_config(page_title="Quem é Quem? - Chat Secreto", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Jogo do Chat Secreto")
st.write("Tente descobrir com quem você está falando sem revelar sua identidade!")

# Criar uma memória para saber se o jogador já entrou na sala
if "entrou_na_sala" not in st.session_state:
    st.session_state.entrou_na_sala = False

# --- TELA 1: ENTRADA (Se o jogador ainda não entrou) ---
if not st.session_state.entrou_na_sala:
    st.subheader("🤖 Passo 1: Crie seu disfarce")
    
    # Campo para digitar o Nick Secreto
    nick = st.text_input("Digite seu Nick Secreto (Ex: NinjaAnônimo):", placeholder="Não use seu nome real!")
    
    # Botão para entrar
    if st.button("Procurar Sala 🚀"):
        if nick.strip() != "":
            # Salva o nick na memória e muda de tela
            st.session_state.meu_nick = nick
            st.session_state.entrou_na_sala = True
            st.rerun() # Atualiza a tela
        else:
            st.error("Por favor, digite um Nick antes de entrar!")
            
    # --- SUA ASSINATURA NO FINAL DA TELA ---
    st.divider() # Cria uma linha fininha para separar
    st.caption("⚡ Desenvolvido por Rafael Lessa")

# --- TELA 2: O JOGO (Depois que ele clica no botão) ---
else:
    st.success(f"Conectado como: **{st.session_state.meu_nick}**")
    st.info("🕵️‍♂️ Sistema: Conectado ao banco de dados! Enviando mensagens reais agora.")
    
    st.divider()
    
    # Aqui é onde vai ficar o visual dos dois campos que você inventou!
    col1, col2 = st.columns(2)
    
    with col1:
        pergunta = st.text_input("💬 Enviar Pergunta/Pista:", placeholder="Escreva algo...")
        if st.button("Enviar Mensagem"):
            if pergunta.strip() != "":
                # SALVA A MENSAGEM DIRETO NA SUA TABELA DO SUPABASE!
                dados = {
                    "Jogador": st.session_state.meu_nick,
                    "texto": pergunta
                }
                supabase.table("Mensagens").insert(dados).execute()
                st.success(f"Enviado para o banco: {pergunta}")
            else:
                st.warning("Digite algo antes de enviar!")
            
    with col2:
        palpite = st.text_input("🎯 Dar Palpite de quem é:", placeholder="Acho que você é o...")
        if st.button("Arriscar Palpite!"):
            st.write(f"Você acha que é: {palpite}")
            
    # Botão para voltar para o começo se quiser testar de novo
    if st.button("Sair da Sala 🚪"):
        st.session_state.entrou_na_sala = False
        st.rerun()
