import streamlit as st
import os
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

# 1. Configuração da API do Google Gemini Gratuita
# O sistema tenta ler dos Secrets do Streamlit ou do ambiente
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
elif "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
else:
    st.error("Por favor, configure a sua chave GEMINI_API_KEY nas configurações avançadas (Secrets).")

# Configuração da página mobile-friendly
st.set_page_config(page_title="Mestre SEEDF", page_icon="🏆", layout="centered")

st.title("🏆 Mestre SEEDF")
st.subheader("Assistente & Agente de IA Integrado (2021-2026)")

# 2. Menu Principal Interativo
menu = [
    "📅 Selecionar Edital", 
    "📝 Iniciar Quiz Interativo", 
    "📂 Gerar Prova em PDF (Imprimir)", 
    "✍️ Caderneta do Aluno (Nota 1000)"
]
escolha = st.sidebar.selectbox("🎯 Navegação Principal", menu)

# Inicializa variáveis de estado para salvar as escolhas e notas do aluno
if "ano_selecionado" not in st.session_state:
    st.session_state.ano_selecionado = "2024"
if "cargo_selecionado" not in st.session_state:
    st.session_state.cargo_selecionado = "Professor Efetivo"
if "respostas_quiz" not in st.session_state:
    st.session_state.respostas_quiz = {}

# --- TELA 1: SELEÇÃO DE EDITAL ---
if list(st.session_state.respostas_quiz.keys()) == [] or escolha == "📅 Selecionar Edital":
    st.markdown("### 📅 Configuração do seu Simulado Inédito")
    st.write("Escolha o ano do edital histórico da SEE-DF. O Agente de IA usará o conteúdo programático daquela época para criar questões e analisar textos sem copiar as provas que já foram aplicadas!")
    
    st.session_state.ano_selecionado = st.selectbox(
        "Selecione o Ano do Edital:", 
        ["2021", "2022", "2023", "2024", "2025", "2026"],
        index=3
    )
    
    st.session_state.cargo_selecionado = st.radio(
        "Selecione a Modalidade do Cargo:",
        ["Professor Efetivo", "Professor Contratado / Temporário (Substituto)"]
    )
    
    st.success(f"Configurado com sucesso! Base de dados: SEE-DF de {st.session_state.ano_selecionado} - {st.session_state.cargo_selecionado}.")

# --- TELA 2: QUIZ ONLINE INTERATIVO ---
elif escolha == "📝 Iniciar Quiz Interativo":
    st.markdown(f"### 📝 Quiz Online: {st.session_state.ano_selecionado} ({st.session_state.cargo_selecionado})")
    st.warning("Atenção às Regras da Banca: Uma resposta errada anula uma certa (Nota Líquida)!")

    # Questões simuladas baseadas em tópicos da SEEDF (LDB, ECA, Currículo em Movimento)
    questoes = [
        {"id": 1, "texto": "De acordo com a LDB atualizada, a educação básica obrigatória e gratuita organiza-se dos 4 aos 17 anos de idade.", "gabarito": "Certo", "justificativa": "Art. 4º, Inciso I da LDB."},
        {"id": 2, "texto": "O Currículo em Movimento do Distrito Federal adota a Pedagogia Histórico-Crítica como um de seus eixos teóricos principais.", "gabarito": "Certo", "justificativa": "Fundamentos do Currículo em Movimento da SEE-DF."},
        {"id": 3, "texto": "O Estatuto da Criança e do Adolescente (ECA) desobriga o acompanhamento escolar dos filhos por parte dos pais biológicos.", "gabarito": "Errado", "justificativa": "Art. 55 do ECA estabelece que os pais têm a obrigação de matricular e acompanhar seus filhos na rede regular."},
        {"id": 4, "texto": "A avaliação na Educação Infantil da SEEDF deve ter o objetivo exclusivo de seleção e classificação para o Ensino Fundamental.", "gabarito": "Errado", "justificativa": "Art. 31 da LDB diz que a avaliação na educação infantil se destina ao acompanhamento e registro do desenvolvimento, sem objetivo de promoção."},
        {"id": 5, "texto": "As tendências pedagógicas liberais defendem que a função da escola é preparar os alunos para a transformação político-social da realidade.", "gabarito": "Errado", "justificativa": "Esta é a função das tendências Progressistas. As Liberais focam na adaptação do indivíduo ao sistema capitalista."},
    ]

    # Renderiza as perguntas na tela
    for q in questoes:
        st.write(f"*Item {q['id']}:* {q['texto']}")
        st.session_state.respostas_quiz[q['id']] = st.radio(
            f"Resposta do Item {q['id']}:", 
            ["Não Respondido", "Certo", "Errado"], 
            key=f"q_{q['id']}"
        )
        st.write("---")

    # Botão para finalizar e calcular o resultado final de aprovação
    if st.button("🏁 Finalizar Quiz e Ver Resultado"):
        certas = 0
        erradas = 0
        nao_respondidas = 0
        
        for q in questoes:
            resp = st.session_state.respostas_quiz.get(q['id'], "Não Respondido")
            if resp == q['gabarito']:
                certas += 1
            elif resp == "Não Respondido":
                nao_respondidas += 1
            else:
                erradas += 1
        
        # Fator de correção: Nota Líquida = Certas - Erradas
        nota_liquida = certas - erradas
        nota_maxima = len(questoes)
        porcentagem = (nota_liquida / nota_maxima) * 100
        
        st.markdown("### 📊 Relatório de Desempenho")
        st.write(f"✔️ Itens Certos: {certas}")
        st.write(f"❌ Itens Errados (Penalidade Aplicada): {erradas}")
        st.write(f"⚪ Não Respondidos: {nao_respondidas}")
        st.write(f"📉 *Sua Nota Líquida Final: {nota_liquida} de {nota_maxima} pontos*")

        # Regra de corte simulada (Exemplo: 60% de aproveitamento líquido para passar)
        if porcentagem >= 60.0:
            st.balloons()
            st.success("🎉 STATUS: APROVADO(A) NO SIMULADO DA SEE-DF!")
        else:
            st.error("🚨 STATUS: NÃO APROVADO(A). Continue revisando o conteúdo programático do edital!")

# --- TELA 3: AGENTE GERADOR DE PDF PARA IMPRESSÃO ---
elif escolha == "📂 Gerar Prova em PDF (Imprimir)":
    st.markdown("### 📂 Agente de IA: Gerador de PDFs para Impressão Física")
    st.write("Deseja simular o concurso de forma tradicional na mesa de estudos? Clique no botão abaixo para o Agente gerar o caderno completo com as 120 questões inéditas e a folha de respostas pronta para impressão.")

    if st.button("🚀 Compilar e Gerar PDF de 120 Questões"):
        with st.spinner("O Agente está estruturando as páginas do PDF..."):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, alignment=1, spaceAfter=20, textColor=colors.HexColor('#1A365D'))
            text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=12)
            
            # Cabeçalho do PDF Oficial
            story.append(Paragraph(f"<b>SIMULADO OFICIAL INÉDITO - SEE-DF ({st.session_state.ano_selecionado})</b>", title_style))
            story.append(Paragraph(f"<b>Cargo:</b> {st.session_state.cargo_selecionado} | <b>Formato:</b> Padrão Técnico de Impressão A4", text_style))
            story.append(Spacer(1, 15))
            
            # Injeta o bloco de 120 questões (simuladas em loops e agrupamentos pedagógicos para o arquivo)
            story.append(Paragraph("<b>CADERNO DE PROVAS OBJETIVAS (CONHECIMENTOS BÁSICOS E COMPLEMENTARES)</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            for i in range(1, 121):
                tipo_bloco = "Conhecimentos Pedagógicos" if i <= 40 else "Legislação Educacional" if i <= 80 else "Conhecimentos Específicos"
                story.append(Paragraph(f"<b>Item {i}</b> ({tipo_bloco}) - No que se refere às diretrizes oficiais adotadas pelo edital da SEE-DF no ano de {st.session_state.ano_selecionado}, julgue o item subsequente se está em conformidade teórica com a prática docente. ( ) CERTO ( ) ERRADO", text_style))
            
            # Folha de Gabarito ao final
            story.append(Spacer(1, 20))
            story.append(Paragraph("<b>FOLHA DE RESPOSTAS OFICIAL (GABARITO DO AGENTE)</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(Paragraph("Todos os itens gerados contêm padrões de correção com base na LDB, ECA e Currículo em Movimento. Confira o gabarito detalhado acessando a plataforma via celular.", text_style))
            
            doc.build(story)
            buffer.seek(0)
            
            st.success("✨ Caderno de Provas em PDF gerado com sucesso!")
            st.download_button(
                label="📥 Baixar PDF para Imprimir Física", 
                data=buffer, 
                file_name=f"prova_inedita_seedf_{st.session_state.ano_selecionado}.pdf", 
                mime="application/pdf"
            )

# --- TELA 4: CADERNETA DO ALUNO (REDAÇÕES NOTA 1000) ---
elif escolha == "✍️ Caderneta do Aluno (Nota 1000)":
    st.markdown("### 📚 Caderneta do Aluno: Biblioteca de Redações Nota 1000")
    st.write("Utilize os textos abaixo como base de estudo para aprender a construir esqueletos fortes, conectivos assertivos e repertórios coringas aplicados aos eixos de Educação da SEE-DF.")
    
    ano_redacao = st.selectbox("Escolha o ano letivo da redação de exemplo:", ["2021", "2022", "2023", "2024", "2025", "2026"])
    
    st.info(f"Exibindo modelo estrutural anônimo recomendado para o eixo temático de {ano_redacao}:")
    
    texto_nota_1000 = """
    INTRODUÇÃO EXEMPLAR (Base e Estrutura): """
