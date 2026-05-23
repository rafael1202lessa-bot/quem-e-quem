import streamlit as st
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="Quem é Quem?", page_icon="🕵️‍♂️", layout="centered")

# CONEXÃO DIRETA CORRETA
SUPABASE_URL = "https://tuymyyxguujeuxwgrssm.supabase.co"
SUPABASE_KEY = "sb_publishable_mE_GPQgHRnkF1bp241SkyA_Ijynueb5"

# Criando o cliente diretamente
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro de conexão inicial: {e}")

# Controle de telas
if "tela" not in st.session_state:
    st.session_state.tela = "login"
if "meu_nick" not in st.session_state:
    st.session_state.meu_nick = ""

# --- TELA 1: LOGIN ---
if st.session_state.tela == "login":
    st.title("🕵️‍♂️ Jogo: Quem é Quem?")
    st.markdown("Bem-vindo ao sistema anônimo de investigação. Escolha seu codinome para entrar na sala.")
    
    nick = st.text_input("Escolha seu Nick Secreto:", placeholder="Ex: GalaticoAnonimo")
    
    if st.button("Entrar na Sala"):
        if nick.strip() != "":
            st.session_state.meu_nick = nick.strip()
            st.session_state.tela = "jogo"
            st.rerun()
        else:
            st.error("Digite um nick válido!")

# --- TELA 2: SALA DO JOGO ---
elif st.session_state.tela == "jogo":
    st.title("🎮 Painel do Jogo")
    st.write(f"Logado como: **{st.session_state.meu_nick}**")
    
    # Abas do jogo
    aba_pistas, aba_palpites, aba_regras = st.tabs(["💬 Pistas e Chat", "🚨 Dar Palpite / Acusar", "📜 Regras do Jogo"])
    
    # --- ABA 1: CHAT DE PISTAS ---
    with aba_pistas:
        st.subheader("Enviar uma pista anônima")
        pergunta = st.text_input("Sua Pista:", placeholder="Escreva sua pista aqui...", key="input_pista")
        
        if st.button("Enviar Pista"):
            if pergunta.strip() != "":
                try:
                    dados_pista = {
                        "jogador": st.session_state.meu_nick,
                        "texto": pergunta.strip()
                    }
                    supabase.table("mensagens").insert(dados_pista).execute()
                    st.toast("Pista enviada com sucesso! 🚀")
                    st.success("Pista salva no banco de dados!")
                    st.rerun()
                except Exception as erro:
                    st.error(f"Erro ao enviar pista: {erro}")
            else:
                st.warning("Escreva algo antes de enviar!")
                
        st.markdown("---")
        st.subheader("📋 Histórico de Pistas")
        try:
            historico = supabase.table("mensagens").select("*").order("created_at", desc=True).execute()
            if historico.data:
                for msg in historico.data:
                    st.info(f"🕵️‍♂️ Pista recebida: \"{msg['texto']}\"")
            else:
                st.write("Nenhuma pista enviada ainda.")
        except Exception:
            st.write("Aguardando novas pistas...")

    # --- ABA 2: SISTEMA DE PALPITES ---
    with aba_palpites:
        st.subheader("Quem você acha que é?")
        
        suspeito = st.text_input("Nome do jogador suspeito (Nome Real):", placeholder="Ex: João")
        palpite_identidade = st.text_input("Qual você acha que é o Nick Secreto dele?", placeholder="Ex: NinjaAnonimo")
        
        if st.button("Lançar Palpite Oficial 🚨"):
            if suspeito.strip() != "" and palpite_identidade.strip() != "":
                try:
                    dados_palpite = {
                        "acusador": st.session_state.meu_nick,
                        "suspeito": suspeito.strip(),
                        "palpite": palpite_identidade.strip()
                    }
                    supabase.table("palpites").insert(dados_palpite).execute()
                    st.toast("Palpite registrado! 🚨")
                    st.success(f"Palpite contra {suspeito} registrado!")
                    st.rerun()
                except Exception as erro:
                    st.error(f"Erro ao enviar palpite: {erro}")
            else:
                st.warning("Preencha o nome do suspeito e o palpite!")
                
        st.markdown("---")
        st.subheader("📢 Palpites Feitos")
        try:
            lista_palpites = supabase.table("palpites").select("*").order("created_at", desc=True).execute()
            if lista_palpites.data:
                for pal in lista_palpites.data:
                    st.warning(f"💥 **{pal['acusador']}** acha que **{pal['suspeito']}** é o **{pal['palpite']}**!")
            else:
                st.write("Nenhum palpite feito ainda nesta rodada.")
        except Exception:
            st.write("Aguardando palpites...")

    # --- ABA 3: REGRAS DO JOGO ---
    with aba_regras:
        st.subheader("📜 Como Jogar 'Quem é Quem?'")
        st.markdown("""
        1. **Configuração Inicial:** Cada jogador entra na sala usando um **Nick Secreto** (sem contar para ninguém qual escolheu).
        2. **Fase de Pistas:** Na aba **Pistas e Chat**, envie características, fatos ou piadas internas anonimamente para que o grupo tente adivinhar quem é você.
        3. **A Acusação:** Se você tiver certeza da identidade de alguém, vá na aba **Dar Palpite** e coloque o Nome Real da pessoa junto com o Nick Secreto que você acha que pertence a ela.
        4. **Vitória:** Ganha quem desmascarar mais integrantes até o fim da rodada!
        """)

    # --- MENU LATERAL: ADMIN, ASSINATURA & LOGOUT ---
    st.sidebar.title("⚙️ Opções")
    
    # Sistema de Admin Oculto
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔑 Painel do Administrador"):
        senha_admin = st.text_input("Senha Master:", type="password")
        if senha_admin == "admin123":
            st.success("Acesso Liberado")
            
            if st.button("🗑️ Limpar Todas as Pistas"):
                try:
                    supabase.table("mensagens").delete().neq("id", 0).execute()
                    st.toast("Histórico de pistas deletado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao limpar: {e}")
                    
            if st.button("🗑️ Limpar Todos os Palpites"):
                try:
                    supabase.table("palpites").delete().neq("id", 0).execute()
                    st.toast("Histórico de palpites deletado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao limpar: {e}")
        elif senha_admin != "":
            st.error("Senha Incorreta")

    st.sidebar.markdown("---")
    if st.sidebar.button("Sair da Sala"):
        st.session_state.tela = "login"
        st.session_state.meu_nick = ""
        st.rerun()

    # CRÉDITOS E ASSINATURA NO RODAPÉ DA BARRA LATERAL
    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("💻 **Desenvolvido por Rafael Lessa**")
        
