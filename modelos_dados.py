# Saída estruturada sempre com um schema(pydantic) sempre que você precisar de números, recomendável usar saída estruturada

# pyrefly: ignore [missing-import]
from asyncio import coroutines
from pydantic import BaseModel, Field
from google import genai
from PIL import Image
import streamlit as st

MODEL= 'gemini-3.1-flash-lite' #JAMAIS ALTERAR ESSE MODELO, PODE CAUSAR ERROS

class Refeicao(BaseModel):
    nome: str = Field(description="Nome do prato identificado na foto.")
    calorias: int = Field(description="Estimativa de calorias totais para a porção mostrada.")
    proteinas: float = Field(description="Quantidade estimada de proteínas em gramas.")
    carboidratos: float = Field(description="Quantidade estimada de carboidratos em gramas.")
    gorduras: float = Field(description="Quantidade estimada de gorduras em gramas.")
    vegetariano: bool = Field(description="Se o prato é adequado para vegetarianos.")
    vegano: bool = Field(description="Se o prato é adequado para veganos.")
    gluten_free: bool = Field(description="Se o prato é livre de glúten.")
    alergicos: list[str] = Field(description="Lista de alérgenos comuns no prato.")
    tipo_cozinha: str = Field(description="Tipo de culinária do prato.")
    score_saude: int = Field(description="Score de saúde do prato de 1 a 10.")
    nota_confianca: int = Field(description="Nota de confiança de 1 até 5 sobre a certeza na identificação do prato.")

# --- Configurações da Página Streamlit ---
st.set_page_config(
    page_title="NutriVision AI",
    page_icon="🥗",
    layout="wide"
)

# --- Estilo CSS Customizado (Premium) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Container styling */
    .header-container {
        text-align: center;
        background: linear-gradient(135deg, #1e3d2f 0%, #111b15 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        color: white;
    }
    
    .header-container h1 {
        font-weight: 800;
        font-size: 2.8rem;
        margin: 0 0 0.5rem 0;
        color: #4CAF50;
        background: linear-gradient(90deg, #81C784, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-container p {
        font-weight: 300;
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Premium Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1e3d2f;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E8F5E9;
        padding-bottom: 0.4rem;
    }
    
    /* Styled Metric Card */
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #E9ECEF;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2E7D32;
        margin: 0.2rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6C757D;
        text-transform: uppercase;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* Badges styling */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 0.5rem;
    }

    .badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-flex;
        align-items: center;
    }

    .badge-success {
        background-color: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #C8E6C9;
    }

    .badge-danger {
        background-color: #FFEBEE;
        color: #C62828;
        border: 1px solid #FFCDD2;
    }

    .badge-warning {
        background-color: #FFF3E0;
        color: #EF6C00;
        border: 1px solid #FFE0B2;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header-container">
    <h1>🥗 NutriVision AI</h1>
    <p>Envie a foto do seu prato e obtenha instantaneamente a análise nutricional completa.</p>
</div>
""", unsafe_allow_html=True)

# --- Cliente Gemini ---
import os
api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Chave de API do Google não configurada! Adicione 'GOOGLE_API_KEY' aos secrets do Streamlit ou nas variáveis de ambiente.")
else:
    client = genai.Client(api_key=api_key)

    def exibir_resultados(imagem):
        # Cria colunas para exibir Imagem + Resultados
        col_img, col_res = st.columns([5, 7], gap="large")
        
        with col_img:
            st.image(imagem, caption="Imagem Analisada", use_container_width=True)
            
        with col_res:
            with st.spinner("Analisando prato com Gemini AI... 🧠"):
                try:
                    resposta = client.models.generate_content(
                        model=MODEL,
                        contents=[
                            imagem,
                            "Analise esta imagem de refeição e extraia os dados nutricionais solicitados.",
                        ],
                        config=genai.types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=Refeicao.model_json_schema(),
                        ),
                    )
                    
                    # Converte a resposta JSON em objeto Pydantic
                    dados_refeicao = Refeicao.model_validate_json(resposta.text)
                    
                    # Exibe Nome do Prato e Tipo de Cozinha
                    st.markdown(f'<h2 style="color: #1e3d2f; margin-top: 0;">🍽️ {dados_refeicao.nome}</h2>', unsafe_allow_html=True)
                    st.markdown(f'**Tipo de Culinária:** {dados_refeicao.tipo_cozinha}')
                    
                    # Score de Saúde
                    st.markdown('<div class="section-header">⭐ Score de Saúde</div>', unsafe_allow_html=True)
                    st.markdown(f'Nota: **{dados_refeicao.score_saude}/10**')
                    st.progress(dados_refeicao.score_saude / 10.0)
                    
                    # Informações Nutricionais (Macro Nutrientes)
                    st.markdown('<div class="section-header">📊 Informações Nutricionais</div>', unsafe_allow_html=True)
                    
                    # Exibe como cards customizados
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">🔥 Calorias</div>
                            <div class="metric-value">{dados_refeicao.calorias}</div>
                            <div style="font-size: 0.8rem; color: #6c757d;">kcal</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💪 Proteínas</div>
                            <div class="metric-value">{dados_refeicao.proteinas}g</div>
                            <div style="font-size: 0.8rem; color: #6c757d;">Grama(s)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">🍞 Carboidratos</div>
                            <div class="metric-value">{dados_refeicao.carboidratos}g</div>
                            <div style="font-size: 0.8rem; color: #6c757d;">Grama(s)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with m4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">🥑 Gorduras</div>
                            <div class="metric-value">{dados_refeicao.gorduras}g</div>
                            <div style="font-size: 0.8rem; color: #6c757d;">Grama(s)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Preferências e Características Alimentares
                    st.markdown('<div class="section-header">🥗 Características Alimentares</div>', unsafe_allow_html=True)
                    
                    badge_veg = '<div class="badge badge-success">🥗 Vegetariano</div>' if dados_refeicao.vegetariano else '<div class="badge badge-danger">🥩 Não Vegetariano</div>'
                    badge_vegan = '<div class="badge badge-success">🌱 Vegano</div>' if dados_refeicao.vegano else '<div class="badge badge-danger">🥛 Não Vegano</div>'
                    badge_gf = '<div class="badge badge-success">🌾 Sem Glúten</div>' if dados_refeicao.gluten_free else '<div class="badge badge-warning">🍞 Contém Glúten</div>'
                    
                    st.markdown(f"""
                    <div class="badge-container">
                        {badge_veg}
                        {badge_vegan}
                        {badge_gf}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Alérgenos
                    st.markdown('<div class="section-header">⚠️ Alérgenos</div>', unsafe_allow_html=True)
                    if dados_refeicao.alergicos:
                        allergens_badges = "".join([f'<div class="badge badge-warning">{a}</div>' for a in dados_refeicao.alergicos])
                        st.markdown(f'<div class="badge-container">{allergens_badges}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color: #2E7D32; font-weight: 600;">✅ Nenhum alérgeno comum detectado.</span>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Erro ao processar imagem: {e}")

    # --- Abas de Entrada ---
    tab1, tab2 = st.tabs(["📸 Captura de Foto", "📤 Upload de Foto"])

    with tab1:
        st.markdown('<p style="font-size: 1.1rem; color: #6C757D; margin-top: 1rem;">Use a câmera do seu dispositivo para tirar uma foto do prato:</p>', unsafe_allow_html=True)
        camera_image = st.camera_input("Tire uma foto da sua refeição")
        if camera_image is not None:
            # Carrega a imagem capturada
            imagem = Image.open(camera_image)
            exibir_resultados(imagem)

    with tab2:
        st.markdown('<p style="font-size: 1.1rem; color: #6C757D; margin-top: 1rem;">Selecione um arquivo de imagem salvo no seu dispositivo:</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Selecione uma imagem de refeição (.jpg, .png, .webp)", 
            type=["jpg", "png", "webp"],
            key="file_uploader"
        )
        if uploaded_file is not None:
            # Carrega a imagem enviada
            imagem = Image.open(uploaded_file)
            exibir_resultados(imagem)



