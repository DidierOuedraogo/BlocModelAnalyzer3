import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import base64
import ezdxf
from ezdxf.addons import r12writer
import tempfile
import os
import pyvista as pv
from shapely.geometry import Point, Polygon
import trimesh
from scipy.spatial import ConvexHull
from datetime import datetime

# Configuration de la page avec thème moderne
st.set_page_config(
    page_title="Block Model Analyzer",
    page_icon=⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour une interface plus jolie et conviviale
st.markdown("""
<style>
    /* Thème moderne avec une palette de couleurs minières */
    :root {
        --primary: #2C3E50;
        --secondary: #E67E22;
        --background: #ECF0F1;
        --text: #2C3E50;
        --accent: #3498DB;
        --success: #2ECC71;
        --warning: #F39C12;
        --error: #E74C3C;
    }
    
    /* Reset et styles de base */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text);
        background-color: var(--background);
    }
    
    /* En-tête et titre */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, #34495e 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        z-index: 0;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.4rem;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .author {
        margin-top: 0.7rem;
        font-style: italic;
        font-size: 1rem;
        opacity: 0.8;
        position: relative;
        z-index: 1;
    }
    
    /* Cartes pour les sections */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        border-left: 5px solid var(--secondary);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
    }
    
    .card-title {
        color: var(--primary);
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.7rem;
        display: flex;
        align-items: center;
    }
    
    .card-title svg {
        margin-right: 0.5rem;
    }
    
    /* Badge pour les compteurs et statistiques */
    .badge {
        background-color: var(--accent);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.6rem;
        box-shadow: 0 2px 5px rgba(52, 152, 219, 0.2);
    }
    
    .badge-success {
        background-color: var(--success);
        box-shadow: 0 2px 5px rgba(46, 204, 113, 0.2);
    }
    
    .badge-warning {
        background-color: var(--warning);
        box-shadow: 0 2px 5px rgba(243, 156, 18, 0.2);
    }
    
    .badge-error {
        background-color: var(--error);
        box-shadow: 0 2px 5px rgba(231, 76, 60, 0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #eee;
        font-size: 0.9rem;
        color: #7f8c8d;
    }
    
    /* Tabs design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 1.5rem;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        color: var(--text);
        transition: all 0.2s ease;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: rgba(52, 152, 219, 0.1);
        color: var(--accent);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--accent) !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 8px 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #eee;
    }
    
    .sidebar-heading {
        color: var(--primary);
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--secondary) 0%, #D35400 100%);
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(230, 126, 34, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #D35400 0%, var(--secondary) 100%);
        box-shadow: 0 4px 8px rgba(230, 126, 34, 0.4);
        transform: translateY(-2px);
    }
    
    /* Info box */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid var(--accent);
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1.2rem 0;
        position: relative;
    }
    
    .info-box::before {
        content: "ℹ️";
        position: absolute;
        top: 1.2rem;
        left: 1.2rem;
        font-size: 1.2rem;
    }
    
    .info-box-content {
        margin-left: 2.5rem;
    }
    
    .success-box {
        background-color: #E8F5E9;
        border-left: 4px solid var(--success);
    }
    
    .success-box::before {
        content: "✅";
    }
    
    .warning-box {
        background-color: #FFF3E0;
        border-left: 4px solid var(--warning);
    }
    
    .warning-box::before {
        content: "⚠️";
    }
    
    /* Version badge */
    .version-badge {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
        backdrop-filter: blur(5px);
        z-index: 2;
    }
    
    /* Data metrics */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.2rem;
        flex: 1;
        min-width: 180px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Range inputs styling */
    .slider-container {
        padding: 1rem 0;
    }
    
    /* Custom tooltips */
    [data-tooltip] {
        position: relative;
        cursor: help;
    }
    
    [data-tooltip]::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background-color: var(--primary);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        z-index: 10;
    }
    
    [data-tooltip]:hover::after {
        opacity: 1;
        visibility: visible;
    }
    
    /* File uploader enhancements */
    .uploadedFile {
        border-radius: 8px;
        border: 1px dashed #ccc;
        padding: 0.8rem;
        transition: all 0.2s ease;
    }
    
    .uploadedFile:hover {
        border-color: var(--accent);
        background-color: rgba(52, 152, 219, 0.05);
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    /* Plot styling */
    .plot-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        margin: 1.5rem 0;
    }
    
    /* Download button */
    .download-button {
        display: inline-block;
        background: linear-gradient(135deg, var(--accent) 0%, #2980b9 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3);
        margin-top: 1rem;
    }
    
    .download-button:hover {
        background: linear-gradient(135deg, #2980b9 0%, var(--accent) 100%);
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.4);
        transform: translateY(-2px);
    }
    
    /* Control panel */
    .control-panel {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Progress animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    /* Table enhancements */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    th {
        background-color: var(--primary);
        color: white;
        padding: 0.8rem;
        text-align: left;
    }
    
    td {
        padding: 0.8rem;
        border-bottom: 1px solid #eee;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    tr:hover {
        background-color: rgba(52, 152, 219, 0.05);
    }
    
    /* Selectbox and multiselect styling */
    .stSelectbox label, .stMultiSelect label {
        font-weight: 500;
        color: var(--primary);
    }
    
    /* Number input styling */
    [data-testid="stNumberInput"] > div > div {
        background-color: white;
        border-radius: 6px;
    }
    
    /* Conditional formatting for data values */
    .value-high {
        color: var(--success);
        font-weight: 500;
    }
    
    .value-medium {
        color: var(--warning);
        font-weight: 500;
    }
    
    .value-low {
        color: var(--error);
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# En-tête de l'application avec nom de l'auteur
st.markdown("""
<div class="main-header">
    <div class="version-badge">v1.0.0</div>
    <h1>Block Model Analyzer</h1>
    <p>Application d'analyse de modèles de blocs miniers</p>
    <div class="author">Développé par Didier Ouedraogo, P.Geo</div>
</div>
""", unsafe_allow_html=True)

# Fonctions utilitaires pour les calculs spatiaux
def is_point_in_mesh(point, mesh):
    """Vérifie si un point est à l'intérieur d'un maillage fermé."""
    try:
        # Utilisation de pyvista pour le test d'inclusion
        points = pv.PolyData([point])
        selection = points.select_enclosed_points(mesh)
        return bool(selection["SelectedPoints"][0])
    except Exception as e:
        st.error(f"Erreur lors de la vérification spatiale: {e}")
        return False

def is_point_above_surface(point, surface):
    """Détermine si un point est au-dessus d'une surface."""
    try:
        # Projection du point sur la surface
        x, y, z = point
        closest_point, _ = surface.find_closest_point([x, y, z])
        return z > closest_point[2]  # Point est au-dessus si son z est plus grand
    except Exception as e:
        st.error(f"Erreur lors de la vérification de position: {e}")
        return False

def load_dxf_as_mesh(dxf_file, is_surface=False):
    """Charge un fichier DXF et le convertit en maillage pyvista."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
        temp_file.write(dxf_file.getvalue())
        temp_file.close()
        
        # Charger le DXF avec ezdxf
        doc = ezdxf.readfile(temp_file.name)
        msp = doc.modelspace()
        
        # Extraire les informations géométriques
        vertices = []
        faces = []
        
        if is_surface:
            # Pour une surface (collection de faces)
            for entity in msp:
                if entity.dxftype() == '3DFACE':
                    verts = [entity.dxf.vtx0, entity.dxf.vtx1, entity.dxf.vtx2, entity.dxf.vtx3]
                    current_face = []
                    
                    for v in verts:
                        # Éviter les doublons
                        idx = None
                        for i, existing_v in enumerate(vertices):
                            if np.allclose(v, existing_v):
                                idx = i
                                break
                        
                        if idx is None:
                            idx = len(vertices)
                            vertices.append(v)
                        
                        current_face.append(idx)
                    
                    # Ajout de la face (triangle)
                    faces.append(current_face[:3])
                    if not np.allclose(verts[2], verts[3]):  # Si c'est un quad, ajouter un second triangle
                        faces.append([current_face[0], current_face[2], current_face[3]])
        else:
            # Pour un solide (maillage fermé)
            for entity in msp:
                if entity.dxftype() in ('3DFACE', 'POLYLINE', 'LWPOLYLINE'):
                    # Traitement adapté selon le type d'entité
                    if entity.dxftype() == '3DFACE':
                        verts = [entity.dxf.vtx0, entity.dxf.vtx1, entity.dxf.vtx2, entity.dxf.vtx3]
                        # Même logique que pour les surfaces
                        current_face = []
                        for v in verts:
                            idx = None
                            for i, existing_v in enumerate(vertices):
                                if np.allclose(v, existing_v):
                                    idx = i
                                    break
                            
                            if idx is None:
                                idx = len(vertices)
                                vertices.append(v)
                            
                            current_face.append(idx)
                        
                        faces.append(current_face[:3])
                        if not np.allclose(verts[2], verts[3]):
                            faces.append([current_face[0], current_face[2], current_face[3]])
        
        # Nettoyer le fichier temporaire
        os.unlink(temp_file.name)
        
        # Créer le maillage pyvista
        if len(vertices) > 0 and len(faces) > 0:
            mesh = pv.PolyData(np.array(vertices), np.array(faces))
            return mesh
        else:
            st.warning("Aucune géométrie valide trouvée dans le fichier DXF.")
            return None
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier DXF: {e}")
        return None

# Fonction de calcul des statistiques descriptives
def calculate_statistics(df, value_column):
    """Calcule les statistiques descriptives pour une colonne de valeurs."""
    if df.empty:
        return pd.DataFrame()
    
    stats = {
        "Nombre de blocs": len(df),
        "Minimum": df[value_column].min(),
        "Maximum": df[value_column].max(),
        "Moyenne": df[value_column].mean(),
        "Médiane": df[value_column].median(),
        "Écart-type": df[value_column].std(),
        "Coefficient de variation": df[value_column].std() / df[value_column].mean() if df[value_column].mean() != 0 else np.nan,
        "Quartile 25%": df[value_column].quantile(0.25),
        "Quartile 75%": df[value_column].quantile(0.75),
    }
    
    if 'tonnage' in df.columns:
        stats["Tonnage total"] = df['tonnage'].sum()
    
    return pd.DataFrame(list(stats.items()), columns=['Statistique', 'Valeur'])

# Fonction de calcul de la courbe tonnage-teneur
def calculate_grade_tonnage_curve(df, grade_column, tonnage_column, cutoffs):
    """Calcule la courbe tonnage-teneur pour différentes teneurs de coupure."""
    if df.empty or not cutoffs:
        return pd.DataFrame()
    
    results = []
    total_tonnage = df[tonnage_column].sum()
    
    for cutoff in cutoffs:
        above_cutoff = df[df[grade_column] >= cutoff]
        
        if above_cutoff.empty:
            tonnage_above = 0
            avg_grade_above = 0
            metal_content = 0
        else:
            tonnage_above = above_cutoff[tonnage_column].sum()
            avg_grade_above = (above_cutoff[grade_column] * above_cutoff[tonnage_column]).sum() / tonnage_above if tonnage_above > 0 else 0
            metal_content = tonnage_above * avg_grade_above / 100  # Supposant que la teneur est en %
        
        results.append({
            "Teneur de coupure": cutoff,
            "Tonnage > coupure": tonnage_above,
            "% du tonnage total": 100 * tonnage_above / total_tonnage if total_tonnage > 0 else 0,
            "Teneur moyenne > coupure": avg_grade_above,
            "Contenu métallique": metal_content
        })
    
    return pd.DataFrame(results)

# Barre latérale pour les contrôles
with st.sidebar:
    st.markdown('<h2 class="sidebar-heading">📂 Chargement des données</h2>', unsafe_allow_html=True)
    
    # Uploader de fichier de modèle de blocs
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <label style="font-weight: 500; margin-bottom: 0.5rem; display: block;">Fichier de modèle de blocs</label>
    </div>
    """, unsafe_allow_html=True)
    
    block_model_file = st.file_uploader("", 
                                     type=["csv", "xlsx", "xls"],
                                     help="Formats supportés: CSV, Excel")
    
    # Options supplémentaires pour le chargement du fichier
    if block_model_file is not None:
        st.markdown(f"""
        <div class="success-box">
            <div class="info-box-content">
                <b>Fichier sélectionné:</b><br>{block_model_file.name}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        file_type = block_model_file.name.split('.')[-1].lower()
        if file_type == 'csv':
            st.markdown('<div class="control-panel">', unsafe_allow_html=True)
            delimiter = st.selectbox("Délimiteur", options=[",", ";", "\t"], index=0)
            decimal = st.selectbox("Séparateur décimal", options=[".", ","], index=0)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="control-panel">', unsafe_allow_html=True)
            sheet_name = st.text_input("Nom de la feuille Excel (vide = première feuille)", "")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Uploader de fichiers DXF
    st.markdown('<h3 class="sidebar-heading">📐 Fichiers DXF (optionnels)</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        envelopes_file = st.file_uploader("Enveloppe DXF", type=["dxf"])
    with col2:
        surface_file = st.file_uploader("Surface DXF", type=["dxf"])
    
    # Afficher des informations sur les fichiers DXF chargés
    if envelopes_file:
        st.markdown(f"""
        <div style="margin-top: 0.5rem;">
            <span class="badge">Enveloppe: {envelopes_file.name.split('/')[-1]}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if surface_file:
        st.markdown(f"""
        <div style="margin-top: 0.5rem;">
            <span class="badge">Surface: {surface_file.name.split('/')[-1]}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Informations sur l'application
    st.markdown('<div style="margin-top:3rem;"><hr></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background: linear-gradient(135deg, #ECF0F1 0%, #D6DBDF 100%); border-radius: 8px; margin-top: 1rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
            <div style="font-size: 2rem; margin-right: 0.8rem;">⛏️</div>
            <div>
                <div style="font-weight: 600; font-size: 1.1rem;">Block Model Analyzer</div>
                <div style="font-size: 0.85rem; opacity: 0.8;">v1.0.0</div>
            </div>
        </div>
        <div style="font-size: 0.9rem; margin-bottom: 1rem;">
            Application pour l'analyse statistique et l'évaluation de ressources minières.
        </div>
        <div style="font-size: 0.85rem; color: #7f8c8d; font-style: italic;">
            © 2025 Didier Ouedraogo, P.Geo
        </div>
    </div>
    """, unsafe_allow_html=True)

# Charger les données
df = None
if block_model_file is not None:
    try:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Chargement des données</div>', unsafe_allow_html=True)
        
        with st.spinner("Chargement en cours..."):
            file_type = block_model_file.name.split('.')[-1].lower()
            
            if file_type in ['xls', 'xlsx']:
                if sheet_name and sheet_name.strip():
                    df = pd.read_excel(block_model_file, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(block_model_file)
            elif file_type == 'csv':
                df = pd.read_csv(block_model_file, sep=delimiter, decimal=decimal)
            
            # Métriques interactives pour l'aperçu des données
            st.markdown("""
            <div class="success-box">
                <div class="info-box-content">
                    <b>Données chargées avec succès!</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Nombre de blocs</div>
                <div class="metric-value">{len(df):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Colonnes</div>
                <div class="metric-value">{len(df.columns)}</div>
            </div>
            """, unsafe_allow_html=True)
            
            num_cols = len([col for col in df.columns if np.issubdtype(df[col].dtype, np.number)])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Colonnes numériques</div>
                <div class="metric-value">{num_cols}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")

# Charger les fichiers DXF si présents
envelope_mesh = None
if envelopes_file is not None:
    with st.spinner("Chargement de l'enveloppe DXF..."):
        envelope_mesh = load_dxf_as_mesh(envelopes_file, is_surface=False)
        if envelope_mesh:
            st.markdown("""
            <div class="success-box" style="width: fit-content;">
                <div class="info-box-content">
                    <b>Enveloppe DXF chargée avec succès!</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger l'enveloppe DXF comme maillage fermé")

surface_mesh = None
if surface_file is not None:
    with st.spinner("Chargement de la surface DXF..."):
        surface_mesh = load_dxf_as_mesh(surface_file, is_surface=True)
        if surface_mesh:
            st.markdown("""
            <div class="success-box" style="width: fit-content;">
                <div class="info-box-content">
                    <b>Surface DXF chargée avec succès!</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger la surface DXF")

# Traitement et analyse des données
if df is not None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔍 Configuration de l\'analyse</div>', unsafe_allow_html=True)
    
    # Afficher l'aperçu des données
    st.subheader("Aperçu des données")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Onglets pour la configuration
    config_tabs = st.tabs(["📋 Colonnes", "⚙️ Filtres"])
    
    with config_tabs[0]:
        # Sélection des colonnes pour l'analyse
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        
        # Détecter automatiquement les colonnes de coordonnées
        x_col_guess = next((col for col in df.columns if col.lower() in ['x', 'east', 'easting', 'x_centre']), df.columns[0])
        y_col_guess = next((col for col in df.columns if col.lower() in ['y', 'north', 'northing', 'y_centre']), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        z_col_guess = next((col for col in df.columns if col.lower() in ['z', 'elev', 'elevation', 'z_centre']), df.columns[2] if len(df.columns) > 2 else df.columns[0])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<p style="font-weight: 600; color: #2C3E50;">Coordonnées</p>', unsafe_allow_html=True)
            x_column = st.selectbox("Colonne X", options=df.columns, index=df.columns.get_loc(x_col_guess) if x_col_guess in df.columns else 0)
            y_column = st.selectbox("Colonne Y", options=df.columns, index=df.columns.get_loc(y_col_guess) if y_col_guess in df.columns else 0)
            z_column = st.selectbox("Colonne Z", options=df.columns, index=df.columns.get_loc(z_col_guess) if z_col_guess in df.columns else 0)
        
        with col2:
            # Deviner les colonnes de teneur et tonnage
            grade_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['grade', 'teneur', 'au', 'cu', 'ag', 'zn', 'pb'])), df.columns[3] if len(df.columns) > 3 else df.columns[0])
            tonnage_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['ton', 'mass', 'weight'])), None)
            
            st.markdown('<p style="font-weight: 600; color: #2C3E50;">Données d\'analyse</p>', unsafe_allow_html=True)
            grade_column = st.selectbox("Colonne teneur", options=df.columns, index=df.columns.get_loc(grade_col_guess) if grade_col_guess in df.columns else 0)
            
            if tonnage_col_guess in df.columns:
                tonnage_column = st.selectbox("Colonne tonnage", options=df.columns, index=df.columns.get_loc(tonnage_col_guess))
            else:
                # Si pas de colonne tonnage, proposer de la calculer
                tonnage_column = st.selectbox("Colonne tonnage (ou à calculer)", options=df.columns, index=0)
                calculate_tonnage = st.checkbox("Calculer le tonnage", value=True)
                
                if calculate_tonnage:
                    with col3:
                        st.markdown('<p style="font-weight: 600; color: #2C3E50;">Calcul du tonnage</p>', unsafe_allow_html=True)
                        
                        density_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['dens', 'sg', 'specific'])), None)
                        
                        if density_col_guess in df.columns:
                            density_column = st.selectbox("Colonne densité", options=df.columns, index=df.columns.get_loc(density_col_guess))
                        else:
                            density_column = st.selectbox("Colonne densité", options=df.columns, index=0)
                        
                        default_density = st.number_input("Densité par défaut", min_value=0.1, max_value=10.0, value=2.7, step=0.1)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            block_size_x = st.number_input("Taille X (m)", min_value=0.1, value=5.0, step=0.5)
                        with col2:
                            block_size_y = st.number_input("Taille Y (m)", min_value=0.1, value=5.0, step=0.5)
                        with col3:
                            block_size_z = st.number_input("Taille Z (m)", min_value=0.1, value=5.0, step=0.5)
                        
                        # Calculer le tonnage si demandé
                        if calculate_tonnage and st.button("Calculer le tonnage"):
                            if density_column in df.columns:
                                df['densité'] = df[density_column].fillna(default_density)
                            else:
                                df['densité'] = default_density
                            
                            # Calcul du volume et du tonnage
                            df['volume'] = block_size_x * block_size_y * block_size_z
                            df['tonnage'] = df['volume'] * df['densité']
                            tonnage_column = 'tonnage'
                            
                            st.markdown("""
                            <div class="success-box">
                                <div class="info-box-content">
                                    <b>Tonnage calculé avec succès!</b>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with config_tabs[1]:
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        
        # Filtres numériques pour les coordonnées
        st.markdown('<p style="font-weight: 600; color: #2C3E50;">Filtres de coordonnées</p>', unsafe_allow_html=True)
        
        x_min, x_max = float(df[x_column].min()), float(df[x_column].max())
        y_min, y_max = float(df[y_column].min()), float(df[y_column].max())
        z_min, z_max = float(df[z_column].min()), float(df[z_column].max())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'<p style="margin-bottom:0.5rem;">Plage X: [{x_min:.2f}, {x_max:.2f}]</p>', unsafe_allow_html=True)
            filter_x = st.slider("Filtre X", min_value=x_min, max_value=x_max, value=(x_min, x_max), key="x_filter")
            
            st.markdown(f'<p style="margin-bottom:0.5rem; margin-top:1rem;">Plage Y: [{y_min:.2f}, {y_max:.2f}]</p>', unsafe_allow_html=True)
            filter_y = st.slider("Filtre Y", min_value=y_min, max_value=y_max, value=(y_min, y_max), key="y_filter")
        
        with col2:
            st.markdown(f'<p style="margin-bottom:0.5rem;">Plage Z: [{z_min:.2f}, {z_max:.2f}]</p>', unsafe_allow_html=True)
            filter_z = st.slider("Filtre Z", min_value=z_min, max_value=z_max, value=(z_min, z_max), key="z_filter")
            
            # Filtres sur la teneur
            grade_min, grade_max = float(df[grade_column].min()), float(df[grade_column].max())
            st.markdown(f'<p style="margin-bottom:0.5rem; margin-top:1rem;">Plage {grade_column}: [{grade_min:.2f}, {grade_max:.2f}]</p>', unsafe_allow_html=True)
            filter_grade = st.slider(f"Filtre {grade_column}", 
                                min_value=grade_min, 
                                max_value=grade_max, 
                                value=(grade_min, grade_max),
                                key="grade_filter")
        
        # Filtres pour les attributs catégoriels
        categorical_columns = [col for col in df.columns if df[col].dtype == 'object' or df[col].nunique() < 20]
        
        if categorical_columns:
            st.markdown('<p style="font-weight: 600; color: #2C3E50; margin-top:1.5rem;">Filtres catégoriels</p>', unsafe_allow_html=True)
            
            categorical_filter_column = st.selectbox("Attribut", options=["Aucun"] + categorical_columns, key="cat_filter_select")
            
            if categorical_filter_column != "Aucun":
                categories = sorted(df[categorical_filter_column].unique())
                selected_categories = st.multiselect("Valeurs à inclure", options=categories, default=categories, key="cat_values")
        
        # Filtres spatiaux
        if envelope_mesh or surface_mesh:
            st.markdown('<p style="font-weight: 600; color: #2C3E50; margin-top:1.5rem;">Filtres spatiaux</p>', unsafe_allow_html=True)
        
        spatial_filters = []
        
        col1, col2 = st.columns(2)
        
        with col1:
            if envelope_mesh:
                use_envelope = st.checkbox("Filtrer par enveloppe DXF", key="use_envelope")
                if use_envelope:
                    spatial_filters.append("envelope")
        
        with col2:
            if surface_mesh:
                use_surface = st.checkbox("Filtrer par surface DXF", key="use_surface")
                if use_surface:
                    surface_relation = st.radio("Relation à la surface", ["Au-dessus", "En-dessous"], key="surface_relation")
                    spatial_filters.append("surface_" + ("above" if surface_relation == "Au-dessus" else "below"))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Appliquer les filtres sélectionnés
    filtered_df = df.copy()
    
    # Filtres de coordonnées
    filtered_df = filtered_df[(filtered_df[x_column] >= filter_x[0]) & 
                             (filtered_df[x_column] <= filter_x[1]) &
                             (filtered_df[y_column] >= filter_y[0]) & 
                             (filtered_df[y_column] <= filter_y[1]) &
                             (filtered_df[z_column] >= filter_z[0]) & 
                             (filtered_df[z_column] <= filter_z[1])]
    
    # Filtre de teneur
    filtered_df = filtered_df[(filtered_df[grade_column] >= filter_grade[0]) & 
                             (filtered_df[grade_column] <= filter_grade[1])]
    
    # Filtre catégoriel
    if 'categorical_filter_column' in locals() and categorical_filter_column != "Aucun" and selected_categories:
        filtered_df = filtered_df[filtered_df[categorical_filter_column].isin(selected_categories)]
    
    # Filtres spatiaux
    if spatial_filters:
        original_count = len(filtered_df)
        
        # Créer une colonne pour le résultat des filtres spatiaux
        filtered_df['in_spatial_filter'] = True
        
        # Appliquer chaque filtre spatial
        for filter_type in spatial_filters:
            if filter_type == "envelope" and envelope_mesh:
                # Pour chaque point, vérifier s'il est dans l'enveloppe
                with st.spinner("Application du filtre d'enveloppe DXF..."):
                    progress_bar = st.progress(0)
                    total_rows = len(filtered_df)
                    
                    for idx, (i, row) in enumerate(filtered_df.iterrows()):
                        point = [row[x_column], row[y_column], row[z_column]]
                        filtered_df.at[i, 'in_envelope'] = is_point_in_mesh(point, envelope_mesh)
                        
                        # Mettre à jour la barre de progression
                        if idx % max(1, total_rows // 100) == 0:
                            progress_bar.progress(idx / total_rows)
                    
                    progress_bar.progress(1.0)
                    filtered_df = filtered_df[filtered_df['in_envelope']]
            
            elif filter_type.startswith("surface_") and surface_mesh:
                relation = filter_type.split('_')[1]  # "above" ou "below"
                
                with st.spinner(f"Application du filtre de surface DXF ({relation})..."):
                    progress_bar = st.progress(0)
                    total_rows = len(filtered_df)
                    
                    for idx, (i, row) in enumerate(filtered_df.iterrows()):
                        point = [row[x_column], row[y_column], row[z_column]]
                        is_above = is_point_above_surface(point, surface_mesh)
                        filtered_df.at[i, 'above_surface'] = is_above
                        
                        # Mettre à jour la barre de progression
                        if idx % max(1, total_rows // 100) == 0:
                            progress_bar.progress(idx / total_rows)
                    
                    progress_bar.progress(1.0)
                    
                    if relation == "above":
                        filtered_df = filtered_df[filtered_df['above_surface']]
                    else:
                        filtered_df = filtered_df[~filtered_df['above_surface']]
        
        blocks_filtered = original_count - len(filtered_df)
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-content">
                <b>Filtres spatiaux appliqués</b><br>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <span class="badge badge-warning">{blocks_filtered:,} blocs supprimés</span>
                    <span class="badge badge-success">{len(filtered_df):,} blocs restants</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Afficher le nombre de blocs après filtrage
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Résultats des filtres</div>', unsafe_allow_html=True)
    
    percentage = len(filtered_df)/len(df)*100
    color_class = "success" if percentage > 50 else "warning" if percentage > 20 else "error"
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">Blocs totaux</div>
            <div class="metric-value">{len(df):,}</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Blocs filtrés</div>
            <div class="metric-value">{len(filtered_df):,}</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Pourcentage</div>
            <div class="metric-value value-{color_class}">{percentage:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour différentes analyses
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Analyses</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📈 Statistiques", "📉 Courbe Tonnage-Teneur", "🔍 Visualisation 3D"])
    
    with tabs[0]:
        st.markdown('<h3 style="margin-bottom: 1.5rem;">Statistiques descriptives</h3>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            stats_df = calculate_statistics(filtered_df, grade_column)
            
            # Afficher les statistiques en format de carte moderne
            col1, col2 = st.columns(2)
            
            with col1:
                # Statistiques de base
                st.markdown('<h4 style="margin-bottom: 1rem;">Statistiques de base</h4>', unsafe_allow_html=True)
                st.dataframe(stats_df, use_container_width=True)
                
                # Export des statistiques
                if st.button("Exporter les statistiques (CSV)", key="export_stats"):
                    csv = stats_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="stats_{grade_column}.csv" class="download-button">Télécharger CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                # Histogramme de la teneur
                st.markdown('<h4 style="margin-bottom: 1rem;">Distribution des teneurs</h4>', unsafe_allow_html=True)
                
                # Créer une figure Plotly pour un histogramme plus interactif
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=filtered_df[grade_column],
                    nbinsx=30,
                    marker_color='#3498DB',
                    opacity=0.8,
                    hovertemplate=
                    f"{grade_column}: %{{x}}<br>" +
                    "Nombre: %{y}<extra></extra>"
                ))
                
                fig.update_layout(
                    title=f'Distribution de {grade_column}',
                    xaxis_title=grade_column,
                    yaxis_title='Fréquence',
                    plot_bgcolor='rgba(245, 245, 245, 0.8)',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=50, b=20),
                    bargap=0.05,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        else:
            st.markdown("""
            <div class="warning-box">
                <div class="info-box-content">
                    <b>Aucune donnée disponible après application des filtres.</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown('<h3 style="margin-bottom: 1.5rem;">Analyse Tonnage-Teneur</h3>', unsafe_allow_html=True)
        
        if tonnage_column in filtered_df.columns and not filtered_df.empty:
            # Configuration des teneurs de coupure dans une carte élégante
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-top: 0; margin-bottom: 1rem;">Configuration des teneurs de coupure</h4>
            """, unsafe_allow_html=True)
            
            # Configuration des teneurs de coupure
            cutoff_min = float(filtered_df[grade_column].min())
            cutoff_max = float(filtered_df[grade_column].max())
            
            col1, col2 = st.columns(2)
            
            with col1:
                cutoff_range = st.slider("Plage de teneurs de coupure", 
                                       min_value=cutoff_min, 
                                       max_value=cutoff_max,
                                       value=(cutoff_min, cutoff_max),
                                       key="cutoff_range")
            
            with col2:
                num_steps = st.slider("Nombre de points sur la courbe", min_value=5, max_value=50, value=20, key="num_steps")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Générer les teneurs de coupure
            cutoffs = np.linspace(cutoff_range[0], cutoff_range[1], num_steps)
            
            # Calculer la courbe tonnage-teneur
            gtc_df = calculate_grade_tonnage_curve(filtered_df, grade_column, tonnage_column, cutoffs)
            
            # Afficher le tableau
            st.markdown('<h4 style="margin-bottom: 1rem;">Tableau Tonnage-Teneur</h4>', unsafe_allow_html=True)
            st.dataframe(gtc_df, use_container_width=True)
            
            # Créer la courbe
            st.markdown('<h4 style="margin-bottom: 1rem; margin-top: 1.5rem;">Courbe Tonnage-Teneur</h4>', unsafe_allow_html=True)
            
            fig = go.Figure()
            
            # Courbe de tonnage
            fig.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Tonnage > coupure"],
                name="Tonnage",
                line=dict(color='#3498DB', width=3),
                yaxis="y",
                hovertemplate=
                "Teneur de coupure: %{x:.2f}<br>" +
                "Tonnage: %{y:,.0f}<extra></extra>"
            ))
            
            # Courbe de teneur moyenne
            fig.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Teneur moyenne > coupure"],
                name="Teneur moyenne",
                line=dict(color='#E67E22', width=3),
                yaxis="y2",
                hovertemplate=
                "Teneur de coupure: %{x:.2f}<br>" +
                "Teneur moyenne: %{y:.2f}<extra></extra>"
            ))
            
            # Mise en page moderne
            fig.update_layout(
                title=f"Courbe Tonnage-Teneur pour {grade_column}",
                xaxis=dict(
                    title="Teneur de coupure",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)',
                    tickformat=".2f"
                ),
                yaxis=dict(
                    title="Tonnage",
                    side="left",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)',
                    tickformat=",d"
                ),
                yaxis2=dict(
                    title="Teneur moyenne",
                    side="right",
                    overlaying="y",
                    showgrid=False,
                    tickformat=".2f"
                ),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255, 255, 255, 0.8)'
                ),
                margin=dict(l=20, r=20, t=60, b=20),
                paper_bgcolor='white',
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
            )
            
            # Amélioration visuelle
            fig.update_xaxes(showspikes=True, spikecolor="#999", spikesnap="cursor", spikemode="across")
            fig.update_yaxes(showspikes=True, spikecolor="#999", spikethickness=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Courbe de contenu métallique
            st.markdown('<h4 style="margin-bottom: 1rem; margin-top: 1.5rem;">Courbe de Contenu Métallique</h4>', unsafe_allow_html=True)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Contenu métallique"],
                name="Contenu métallique",
                line=dict(color='#2ECC71', width=3),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.2)',
                hovertemplate=
                "Teneur de coupure: %{x:.2f}<br>" +
                "Contenu métallique: %{y:,.0f}<extra></extra>"
            ))
            
            fig2.update_layout(
                title="Contenu Métallique vs Teneur de Coupure",
                xaxis=dict(
                    title="Teneur de coupure",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)',
                    tickformat=".2f"
                ),
                yaxis=dict(
                    title="Contenu métallique",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)',
                    tickformat=",d"
                ),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=60, b=20),
                paper_bgcolor='white',
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
            )
            
            # Amélioration visuelle
            fig2.update_xaxes(showspikes=True, spikecolor="#999", spikesnap="cursor", spikemode="across")
            fig2.update_yaxes(showspikes=True, spikecolor="#999", spikethickness=1)
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Export des résultats
            st.markdown('<h4 style="margin-bottom: 1rem; margin-top: 1.5rem;">Export des résultats</h4>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exporter en CSV", key="export_csv"):
                    csv = gtc_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="tonnage_teneur.csv" class="download-button">Télécharger CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                if st.button("Exporter en Excel", key="export_excel"):
                    # Excel export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        gtc_df.to_excel(writer, sheet_name='Tonnage_Teneur', index=False)
                    
                    b64 = base64.b64encode(output.getvalue()).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="tonnage_teneur.xlsx" class="download-button">Télécharger Excel</a>'
                    st.markdown(href, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-box">
                <div class="info-box-content">
                    <b>Analyse impossible :</b> Colonne de tonnage '{tonnage_column}' non trouvée ou aucune donnée disponible après filtrage.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[2]:
        st.markdown('<h3 style="margin-bottom: 1.5rem;">Visualisation 3D</h3>', unsafe_allow_html=True)
        
        if not filtered_df.empty:
            # Limiter à 3000 points pour la performance
            sample_size = min(3000, len(filtered_df))
            sample_df = filtered_df.sample(sample_size) if len(filtered_df) > sample_size else filtered_df
            
            st.markdown("""
            <div class="info-box">
                <div class="info-box-content">
                    <b>Mode de visualisation 3D simplifié</b><br>
                    Cette vue présente un échantillon représentatif du modèle. Pour une visualisation plus complète, exportez les données et utilisez un logiciel de visualisation 3D spécialisé.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Configuration de la visualisation
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-top: 0; margin-bottom: 1rem;">Options de visualisation</h4>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                marker_size = st.slider("Taille des points", min_value=2, max_value=10, value=3, key="marker_size")
            
            with col2:
                color_scale = st.selectbox("Palette de couleurs", 
                                        options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Turbo"],
                                        index=0,
                                        key="color_scale")
            
            with col3:
                opacity = st.slider("Opacité", min_value=0.1, max_value=1.0, value=0.8, step=0.1, key="opacity")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Créer le nuage de points 3D avec Plotly
            fig = go.Figure(data=[go.Scatter3d(
                x=sample_df[x_column],
                y=sample_df[y_column],
                z=sample_df[z_column],
                mode='markers',
                marker=dict(
                    size=marker_size,
                    color=sample_df[grade_column],
                    colorscale=color_scale.lower(),
                    colorbar=dict(title=grade_column),
                    opacity=opacity,
                    showscale=True
                ),
                hovertemplate=
                f'X: %{{x:.2f}}<br>'+
                f'Y: %{{y:.2f}}<br>'+
                f'Z: %{{z:.2f}}<br>'+
                f'{grade_column}: %{{marker.color:.2f}}<extra></extra>'
            )])
            
            # Amélioration de l'apparence
            fig.update_layout(
                title=f"Visualisation 3D du modèle de blocs ({sample_size:,} points)",
                scene=dict(
                    xaxis=dict(
                        title=x_column,
                        backgroundcolor='rgb(245, 245, 245)',
                        gridcolor='white',
                        showbackground=True,
                    ),
                    yaxis=dict(
                        title=y_column,
                        backgroundcolor='rgb(245, 245, 245)',
                        gridcolor='white',
                        showbackground=True,
                    ),
                    zaxis=dict(
                        title=z_column,
                        backgroundcolor='rgb(245, 245, 245)',
                        gridcolor='white',
                        showbackground=True,
                    ),
                    aspectmode='data'
                ),
                margin=dict(l=0, r=0, b=0, t=50),
                paper_bgcolor='white',
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Légende explicative
            st.markdown("""
            <div style="background-color:#f8f9fa; padding:1.2rem; border-radius:8px; margin-top:1.5rem; font-size:0.95rem;">
                <h4 style="margin-top:0; margin-bottom:0.8rem;">Comment utiliser la visualisation 3D</h4>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1rem;">
                    <div>
                        <b>Rotation :</b> Cliquez et faites glisser avec la souris
                    </div>
                    <div>
                        <b>Zoom :</b> Molette de la souris ou pincement sur écran tactile
                    </div>
                    <div>
                        <b>Déplacement :</b> Clic droit + glisser
                    </div>
                    <div>
                        <b>Réinitialiser :</b> Double-clic sur le graphique
                    </div>
                </div>
                <p style="margin-top:0.8rem; opacity:0.8;">
                    Les couleurs représentent les valeurs de teneur de <b>{grade_column}</b>. L'échelle de couleur est indiquée à droite du graphique.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <div class="info-box-content">
                    <b>Aucune donnée disponible pour la visualisation après filtrage.</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer avec copyright
st.markdown("""
<div class="footer">
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
        <div style="font-size: 1.5rem; margin-right: 0.5rem;">⛏️</div>
        <div style="font-weight: 600; font-size: 1.1rem;">Block Model Analyzer</div>
    </div>
    <p>
        Version 1.0.0<br>
        © 2025 Didier Ouedraogo, P.Geo. Tous droits réservés.
    </p>
</div>
""", unsafe_allow_html=True)