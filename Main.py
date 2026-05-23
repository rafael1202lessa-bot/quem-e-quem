import streamlit as st
from supabase import create_client, Client

# Configuração da página
st.set_page_config(page_title="Quem é Quem?", page_icon="🕵️‍♂️", layout="centered")

# CONEXÃO DIRETA CORRETA
SUPABASE_URL = "https://tuymyyxguujeuxwgrssm.supabase.co"
SUPABASE_KEY = "sb_publishable_mE_GPQgHRnkF1bp241SkyA_Ijynueb5"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erro de conexão inicial: {e}")

# Controle de telas e estado do jogo
if "tela" not in st.session_state:
    st.session_state.tela = "login"
if "meu_nick" not in st.session_state:
    st.session_state.meu_nick = ""
if "sala" not in st.session_state:
    st.session_state.sala = ""

# --- TELA 1: LOGIN E TELEPORTE ---
if st.session_state.tela == "login":
    st.title("🕵️‍♂️ Jogo: Quem é Quem?")
    st.markdown("Insira seu codinome. O sistema irá te teleportar para uma sala disponível automaticamente!")
    
    nick = st.text_input("Escolha seu Nick Secreto:", placeholder="Ex: GalaticoAnonimo").strip()
    
    if st.button("Entrar no Jogo (Teleportar) 🌀"):
        if nick == "":
            st.error("Digite un nick válido!")
        else:
            try:
                # SISTEMA DE TELEPORTE AUTOMÁTICO (MATCHMAKING)
                sala_encontrada = ""
                numero_da_sala = 1
                
                while sala_encontrada == "":
                    nome_sala_teste = f"SALA {numero_da_sala}"
                    
                    # Conta quantos jogadores já estão nessa sala específica
                    resposta_sala = supabase.table("jogadores").select("*").eq("sala", nome_sala_teste).execute()
                    qtd_jogadores = len(resposta_sala.data) if resposta_sala.data else 0
                    
                    # Limite de 2 pessoas por sala. Se tiver espaço, entra!
                    if qtd_jogadores < 2:
                        sala_encontrada = nome_sala_teste
                    else:
                        # Se estiver cheia, testa a próxima sala (SALA 2, SALA 3...)
                        numero_da_sala += 1
                
                # Registra o jogador na sala encontrada
                dados_jogador = {"nick": nick, "sala": sala_encontrada}
                supabase.table("jogadores").insert(dados_jogador).execute()
                
                # Salva o estado na sessão do navegador
                st.session_state.sala = sala_encontrada
                st.session_state.meu_nick = nick
                st.session_state.tela = "jogo"
                st.rerun()
                
            except Exception as erro:
                st.error(f"Erro no teleporte: {erro}. Verifique se a tabela 'jogadores' foi criada no Supabase.")

# --- TELA 2: SALA DO JOGO ---
elif st.session_state.tela == "jogo":
    st.title("🎮 Painel do Jogo")
    st.write(f"Você foi teleportado para a: **{st.session_state.sala}**")
    
    # Mostra quem está na mesma sala que você
    try:
        parceiros = supabase.table("jogadores").select("nick").eq("sala", st.session_state.sala).execute()
        lista_nomes = [p['nick'] for p in parceiros.data] if parceiros.data else []
        st.caption(f"🕵️‍♂️ Jogadores conectados nesta sala: {', '.join(lista_nomes)}")
    except:
        pass

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
                        "texto": pergunta.strip(),
                        "sala": st.session_state.sala
                    }
                    supabase.table("mensagens").insert(dados_pista).execute()
                    st.toast("Pista enviada! 🚀")
                    st.rerun()
                except Exception as erro:
                    st.error(f"Erro ao enviar pista: {erro}")
            else:
                st.warning("Escreva algo antes de enviar!")
                
        st.markdown("---")
        st.subheader("📋 Histórico de Pistas")
        try:
            historico = supabase.table("mensagens").select("*").eq("sala", st.session_state.sala).order("created_at", desc=True).execute()
            if historico.data:
                for msg in historico.data:
                    st.info(f"🕵️‍♂️ Pista recebida: \"{msg['texto']}\"")
            else:
                st.write("Nenhuma pista enviada nesta sala ainda.")
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
                        "palpite": palpite_identidade.strip(),
                        "sala": st.session_state.sala
                    }
                    supabase.table("palpites").insert(dados_palpite).execute()
                    st.toast("Palpite registrado! 🚨")
                    st.rerun()
                except Exception as erro:
                    st.error(f"Erro ao enviar palpite: {erro}")
            else:
                st.warning("Preencha todos os campos!")
                
        st.markdown("---")
        st.subheader("📢 Palpites Feitos")
        try:
            lista_palpites = supabase.table("palpites").select("*").eq("sala", st.session_state.sala).order("created_at", desc=True).execute()
            if lista_palpites.data:
                for pal in lista_palpites.data:
                    st.warning(f"💥 **{pal['acusador']}** acha que **{pal['suspeito']}** é o **{pal['palpite']}**!")
            else:
                st.write("Nenhum palpite feito nesta sala ainda.")
        except Exception:
            st.write("Aguardando palpites...")

    # --- ABA 3: REGRAS DO JOGO ---
    with aba_regras:
        st.subheader("📜 Como Jogar")
        st.markdown("""
        1. **Teleporte:** Você não precisa digitar sala. O servidor te aloca em dupla com o próximo jogador disponível.
        2. **Pistas:** Envie fatos anônimos para seu parceiro de sala tentar descobrir quem é você.
        3. **Palpites:** Desmascare a identidade secreta dele antes que ele te desmascare!
        """)

    # --- MENU LATERAL: ADMIN & LOGOUT ---
    st.sidebar.title("⚙️ Opções")
    
    with st.sidebar.expander("🔑 Painel do Administrador"):
        senha_admin = st.text_input("Senha Master:", type="password")
        if senha_admin == "admin123":
            st.success("Acesso Liberado")
            
            if st.button("🗑️ Resetar Servidor Inteiro (Geral)"):
                try:
                    # Limpa absolutamente tudo para começar do zero na segunda feira
                    supabase.table("mensagens").delete().neq("id", 0).execute()
                    st.table("palpites").delete().neq("id", 0).execute()
                    st.table("jogadores").delete().neq("id", 0).execute()
                    st.toast("Todo o servidor foi resetado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao resetar: {e}")
        elif senha_admin != "":
            st.error("Senha Incorreta")

    st.sidebar.markdown("---")
    if st.sidebar.button("Sair do Jogo"):
        try:
            # Remove o registro do jogador ao sair para liberar espaço na sala
            supabase.table("jogadores").delete().eq("nick", st.session_state.meu_nick).eq("sala", st.session_state.sala).execute()
        except:
            pass
        st.session_state.tela = "login"
        st.session_state.meu_nick = ""
        st.session_state.sala = ""
        st.rerun()

    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("💻 **Desenvolvido por Rafael Lessa**")
            
