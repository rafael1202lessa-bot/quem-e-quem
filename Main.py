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
if "meu_nome_real" not in st.session_state:
    st.session_state.meu_nome_real = ""
if "sala" not in st.session_state:
    st.session_state.sala = ""

# --- TELA 1: LOGIN SEGURO COM TELEPORTE ---
if st.session_state.tela == "login":
    st.title("🕵️‍♂️ Jogo: Quem é Quem?")
    st.markdown("Insira seus dados para o sistema te teleportar para uma sala disponível!")
    
    nome_real = st.text_input("Seu Nome Verdadeiro (Ficará oculto e protegido):", placeholder="Ex: Rafael").strip()
    nick = st.text_input("Seu Nick Secreto (Apenas este aparecerá no chat):", placeholder="Ex: GalaticoAnonimo").strip()
    
    if st.button("Entrar no Jogo (Teleportar) 🌀"):
        if nome_real == "" or nick == "":
            st.error("Preencha o Nome Verdadeiro e o Nick Secreto!")
        else:
            try:
                sala_encontrada = ""
                numero_da_sala = 1
                
                # Procura uma sala disponível (máximo 2 pessoas)
                while sala_encontrada == "":
                    nome_sala_teste = f"SALA {numero_da_sala}"
                    resposta_sala = supabase.table("jogadores").select("*").eq("sala", nome_sala_teste).execute()
                    qtd_jogadores = len(resposta_sala.data) if resposta_sala.data else 0
                    
                    if qtd_jogadores < 2:
                        sala_encontrada = nome_sala_teste
                    else:
                        numero_da_sala += 1
                
                # Salva no banco vinculando Nome Real, Nick e Sala
                supabase.table("jogadores").insert({
                    "nick": nick, 
                    "sala": sala_encontrada,
                    "nome_real": nome_real
                }).execute()
                
                st.session_state.sala = sala_encontrada
                st.session_state.meu_nick = nick
                st.session_state.meu_nome_real = nome_real
                st.session_state.tela = "jogo"
                st.rerun()
                
            except Exception as erro:
                st.error(f"Erro no teleporte. Certifique-se de rodar o comando SQL no Supabase! Erro: {erro}")

# --- TELA 2: SALA DO JOGO ---
elif st.session_state.tela == "jogo":
    st.title("🎮 Painel do Jogo")
    st.write(f"Sala Atual: **{st.session_state.sala}** | Logado como Nick: **{st.session_state.meu_nick}**")
    
    # Mostra quem está na sala usando APENAS o nick secreto para manter o mistério
    try:
        parceiros = supabase.table("jogadores").select("nick").eq("sala", st.session_state.sala).execute()
        lista_nicks = [p['nick'] for p in parceiros.data] if parceiros.data else []
        if lista_nicks:
            st.caption(f"🕵️‍♂️ Nicks conectados nesta sala: {', '.join(lista_nicks)}")
    except:
        pass

    aba_pistas, aba_palpites, aba_regras = st.tabs(["💬 Pistas e Chat", "🚨 Dar Palpite / Acusar", "📜 Regras do Jogo"])
    
    # --- ABA 1: CHAT DE PISTAS ANÔNIMAS ---
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

    # --- ABA 2: SISTEMA DE PALPITES COM VALIDAÇÃO AUTOMÁTICA ---
    with aba_palpites:
        st.subheader("Quem você acha que é?")
        
        # O jogador seleciona ou digita o Nick Secreto que ele suspeita
        nick_suspeito = st.text_input("Nick Secreto do Suspeito:", placeholder="Ex: NinjaAnonimo").strip()
        palpite_nome_real = st.text_input("Qual o Nome Verdadeiro dele?", placeholder="Ex: João").strip()
        
        if st.button("Lançar Palpite Oficial 🚨"):
            if nick_suspeito != "" and palpite_nome_real != "":
                try:
                    # Busca no banco secreto quem é o dono real daquele nick nesta sala
                    busca = supabase.table("jogadores").select("nome_real").eq("sala", st.session_state.sala).eq("nick", nick_suspeito).execute()
                    
                    resultado_status = "❌ ERROU"
                    if busca.data:
                        nome_verdadeiro_banco = busca.data[0]['nome_real']
                        # Compara ignorando maiúsculas/minúsculas
                        if nome_verdadeiro_banco.lower() == palpite_nome_real.lower():
                            resultado_status = "💥 ACERTOU EM CHEIO! DESMASCARADO!"
                    
                    # Salva o histórico do palpite para todos verem o resultado
                    dados_palpite = {
                        "acusador": st.session_state.meu_nick,
                        "suspeito": f"{nick_suspeito} (Chutou: {palpite_nome_real})",
                        "palpite": resultado_status,
                        "sala": st.session_state.sala
                    }
                    supabase.table("palpites").insert(dados_palpite).execute()
                    
                    if "💥" in resultado_status:
                        st.balloons()
                        st.success(f"{resultado_status}")
                    else:
                        st.error(f"{resultado_status}")
                    st.rerun()
                    
                except Exception as erro:
                    st.error(f"Erro ao processar palpite: {erro}")
            else:
                st.warning("Preencha todos os campos!")
                
        st.markdown("---")
        st.subheader("📢 Histórico de Acusações")
        try:
            lista_palpites = supabase.table("palpites").select("*").eq("sala", st.session_state.sala).order("created_at", desc=True).execute()
            if lista_palpites.data:
                for pal in lista_palpites.data:
                    # Mostra quem acusou e o veredito automático gerado pelo sistema
                    if "💥" in pal['palpite']:
                        st.success(f"💥 **{pal['acusador']}** desmascarou o suspeito! {pal['palpite']}")
                    else:
                        st.warning(f"🕵️‍♂️ **{pal['acusador']}** acusou **{pal['suspeito']}** ➔ Resposta: {pal['palpite']}")
            else:
                st.write("Nenhum palpite feito nesta sala ainda.")
        except Exception:
            st.write("Aguardando palpites...")

    # --- ABA 3: REGRAS DO JOGO ---
    with aba_regras:
        st.subheader("📜 Como Jogar")
        st.markdown("""
        1. **Cadastro Seguro:** Digite seu nome real e seu apelido secreto. Seu nome real fica trancado em segredo no servidor.
        2. **O Teleporte:** O sistema junta os jogadores em duplas por salas automaticamente.
        3. **Investigação:** Mande pistas na aba de chat. Tente descobrir quem está na sala com você.
        4. **Acusação Final:** Na aba de palpites, coloque o Nick do suspeito e o Nome Real dele. O sistema vai validar na hora se você acertou ou errou!
        """)

    # --- MENU LATERAL: ADMIN & LOGOUT ---
    st.sidebar.title("⚙️ Opções")
    
    with st.sidebar.expander("🔑 Painel do Administrador"):
        senha_admin = st.text_input("Senha Master:", type="password")
        if senha_admin == "admin123":
            st.success("Acesso Liberado")
            
            if st.button("🗑️ Resetar Servidor Inteiro (Geral)"):
                try:
                    supabase.table("mensagens").delete().neq("id", 0).execute()
                    supabase.table("palpites").delete().neq("id", 0).execute()
                    supabase.table("jogadores").delete().neq("id", 0).execute()
                    st.toast("Todo o servidor foi limpo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao resetar: {e}")
        elif senha_admin != "":
            st.error("Senha Incorreta")

    st.sidebar.markdown("---")
    if st.sidebar.button("Sair do Jogo"):
        try:
            supabase.table("jogadores").delete().eq("nick", st.session_state.meu_nick).eq("sala", st.session_state.sala).execute()
        except:
            pass
        st.session_state.tela = "login"
        st.session_state.meu_nick = ""
        st.session_state.meu_nome_real = ""
        st.session_state.sala = ""
        st.rerun()

    st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("💻 **Desenvolvido por Rafael Lessa**")
            
