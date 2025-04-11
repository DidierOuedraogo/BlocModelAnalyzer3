import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import base64
import ezdxf
import tempfile
import os
import pyvista as pv
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Block Model Analyzer",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS simplifié mais efficace
st.markdown("""
<style>
    /* Couleurs principales */
    :root {
        --primary: #2C3E50;
        --secondary: #E67E22;
        --accent: #3498DB;
        --success: #2ECC71;
        --warning: #F39C12;
    }
    
    /* En-tête */
    .header {
        background: linear-gradient(135deg, var(--primary) 0%, #34495e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    }
    
    .header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .header p, .header .author {
        margin: 0.4rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Cartes */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid var(--secondary);
    }
    
    .card-title {
        color: var(--primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
    }
    
    /* Badge */
    .badge {
        background-color: var(--accent);
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .badge-success { background-color: var(--success); }
    .badge-warning { background-color: var(--warning); }
    
    /* Info box */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid var(--accent);
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #E8F5E9;
        border-left: 4px solid var(--success);
    }
    
    .warning-box {
        background-color: #FFF3E0;
        border-left: 4px solid var(--warning);
    }
    
    /* Métriques */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        flex: 1;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0.3rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #777;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        font-size: 0.9rem;
        color: #777;
    }
    
    /* Bouton téléchargement */
    .download-button {
        display: inline-block;
        background-color: var(--accent);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Version badge */
    .version-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 30px;
        font-size: 0.8rem;
    }
    
    /* Sidebar */
    .sidebar-heading {
        font-weight: 600;
        margin: 1rem 0;
        color: var(--primary);
    }
    
    /* Feature explanation */
    .feature-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .feature-title span {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    .feature-description {
        color: #555;
        font-size: 0.95rem;
        margin-left: 1.7rem;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="header">
    <div class="version-badge">v1.0.0</div>
    <h1>Block Model Analyzer</h1>
    <p>Application d'analyse de modèles de blocs miniers</p>
    <div class="author">Développé par Didier Ouedraogo, P.Geo</div>
</div>
""", unsafe_allow_html=True)

# Explication des fonctionnalités
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">✨ Fonctionnalités de l\'application</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feature-box">
    <div class="feature-title"><span>📊</span> Analyse de modèles de blocs</div>
    <p class="feature-description">
        Importez et analysez vos fichiers de modèles de blocs miniers aux formats CSV ou Excel. L'application détecte automatiquement les colonnes de coordonnées, teneurs et autres attributs pour faciliter l'analyse.
    </p>
</div>

<div class="feature-box">
    <div class="feature-title"><span>📐</span> Contraintes spatiales DXF</div>
    <p class="feature-description">
        Appliquez des contraintes spatiales à votre analyse en important des fichiers DXF d'enveloppes minéralisées ou de surfaces (topographie, fonds de fosse). Seuls les blocs respectant ces contraintes seront inclus dans l'analyse.
    </p>
</div>

<div class="feature-box">
    <div class="feature-title"><span>🔍</span> Filtrage avancé</div>
    <p class="feature-description">
        Filtrez vos données selon les coordonnées X, Y, Z, les teneurs, ou tout attribut catégoriel. Créez des sous-ensembles précis du modèle pour des analyses ciblées et des évaluations de ressources adaptées à différents scénarios.
    </p>
</div>

<div class="feature-box">
    <div class="feature-title"><span>📈</span> Statistiques descriptives</div>
    <p class="feature-description">
        Obtenez des statistiques complètes sur vos données filtrées : nombre de blocs, tonnage total, teneurs minimales/maximales/moyennes, écart-type, coefficient de variation et distribution des teneurs sous forme d'histogramme.
    </p>
</div>

<div class="feature-box">
    <div class="feature-title"><span>📉</span> Courbes tonnage-teneur</div>
    <p class="feature-description">
        Générez des courbes tonnage-teneur interactives pour déterminer l'impact des teneurs de coupure sur le tonnage, la teneur moyenne et le contenu métallique. Évaluez rapidement différents scénarios d'exploitation.
    </p>
</div>

<div class="feature-box">
    <div class="feature-title"><span>💾</span> Export des résultats</div>
    <p class="feature-description">
        Exportez vos résultats d'analyse (statistiques, courbes tonnage-teneur) aux formats CSV ou Excel pour les intégrer dans des rapports ou les analyser avec d'autres outils.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Fonctions principales
def is_point_in_mesh(point, mesh):
    """Vérifie si un point est à l'intérieur d'un maillage fermé."""
    try:
        points = pv.PolyData([point])
        selection = points.select_enclosed_points(mesh)
        return bool(selection["SelectedPoints"][0])
    except Exception as e:
        st.error(f"Erreur lors de la vérification spatiale: {e}")
        return False

def is_point_above_surface(point, surface):
    """Détermine si un point est au-dessus d'une surface."""
    try:
        x, y, z = point
        closest_point, _ = surface.find_closest_point([x, y, z])
        return z > closest_point[2]
    except Exception as e:
        st.error(f"Erreur lors de la vérification de position: {e}")
        return False

def load_dxf_as_mesh(dxf_file, is_surface=False):
    """Charge un fichier DXF et le convertit en maillage pyvista."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
        temp_file.write(dxf_file.getvalue())
        temp_file.close()
        
        doc = ezdxf.readfile(temp_file.name)
        msp = doc.modelspace()
        
        vertices = []
        faces = []
        
        if is_surface:
            for entity in msp:
                if entity.dxftype() == '3DFACE':
                    verts = [entity.dxf.vtx0, entity.dxf.vtx1, entity.dxf.vtx2, entity.dxf.vtx3]
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
        else:
            for entity in msp:
                if entity.dxftype() in ('3DFACE', 'POLYLINE', 'LWPOLYLINE'):
                    if entity.dxftype() == '3DFACE':
                        verts = [entity.dxf.vtx0, entity.dxf.vtx1, entity.dxf.vtx2, entity.dxf.vtx3]
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
        
        os.unlink(temp_file.name)
        
        if len(vertices) > 0 and len(faces) > 0:
            mesh = pv.PolyData(np.array(vertices), np.array(faces))
            return mesh
        else:
            st.warning("Aucune géométrie valide trouvée dans le fichier DXF.")
            return None
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier DXF: {e}")
        return None

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
            metal_content = tonnage_above * avg_grade_above / 100
        
        results.append({
            "Teneur de coupure": cutoff,
            "Tonnage > coupure": tonnage_above,
            "% du tonnage total": 100 * tonnage_above / total_tonnage if total_tonnage > 0 else 0,
            "Teneur moyenne > coupure": avg_grade_above,
            "Contenu métallique": metal_content
        })
    
    return pd.DataFrame(results)

# Barre latérale
with st.sidebar:
    st.markdown('<h2 class="sidebar-heading">📂 Chargement des données</h2>', unsafe_allow_html=True)
    
    block_model_file = st.file_uploader("Fichier de modèle de blocs", 
                                       type=["csv", "xlsx", "xls"],
                                       help="Formats supportés: CSV, Excel")
    
    if block_model_file is not None:
        file_type = block_model_file.name.split('.')[-1].lower()
        if file_type == 'csv':
            delimiter = st.selectbox("Délimiteur", options=[",", ";", "\t"], index=0)
            decimal = st.selectbox("Séparateur décimal", options=[".", ","], index=0)
        else:
            sheet_name = st.text_input("Nom de la feuille Excel (vide = première feuille)", "")
    
    st.markdown('<h3 class="sidebar-heading">📐 Fichiers DXF (optionnels)</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        envelopes_file = st.file_uploader("Enveloppe DXF", type=["dxf"])
    with col2:
        surface_file = st.file_uploader("Surface DXF", type=["dxf"])
    
    st.markdown('<div style="margin-top:2rem;"><hr></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0.8rem; background-color: #f8f9fa; border-radius: 8px; margin-top: 1rem;">
        <div style="font-weight: 600; font-size: 1.1rem;">Block Model Analyzer</div>
        <div style="font-size: 0.85rem; opacity: 0.8;">v1.0.0</div>
        <div style="font-size: 0.9rem; margin: 0.5rem 0;">
            Application pour l'analyse statistique et l'évaluation de ressources minières.
        </div>
        <div style="font-size: 0.85rem; color: #777; font-style: italic;">
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
            
            st.markdown("""
            <div class="success-box">
                <b>Données chargées avec succès!</b>
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
            st.success("Enveloppe DXF chargée avec succès")
        else:
            st.warning("Impossible de charger l'enveloppe DXF comme maillage fermé")

surface_mesh = None
if surface_file is not None:
    with st.spinner("Chargement de la surface DXF..."):
        surface_mesh = load_dxf_as_mesh(surface_file, is_surface=True)
        if surface_mesh:
            st.success("Surface DXF chargée avec succès")
        else:
            st.warning("Impossible de charger la surface DXF")

# Traitement et analyse des données
if df is not None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔍 Configuration de l\'analyse</div>', unsafe_allow_html=True)
    
    # Afficher l'aperçu des données
    st.subheader("Aperçu des données")
    st.dataframe(df.head(), use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection des colonnes pour l'analyse
        st.subheader("Sélection des colonnes")
        
        # Détecter automatiquement les colonnes de coordonnées
        x_col_guess = next((col for col in df.columns if col.lower() in ['x', 'east', 'easting', 'x_centre']), df.columns[0])
        y_col_guess = next((col for col in df.columns if col.lower() in ['y', 'north', 'northing', 'y_centre']), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        z_col_guess = next((col for col in df.columns if col.lower() in ['z', 'elev', 'elevation', 'z_centre']), df.columns[2] if len(df.columns) > 2 else df.columns[0])
        
        x_column = st.selectbox("Colonne coordonnée X", options=df.columns, index=df.columns.get_loc(x_col_guess) if x_col_guess in df.columns else 0)
        y_column = st.selectbox("Colonne coordonnée Y", options=df.columns, index=df.columns.get_loc(y_col_guess) if y_col_guess in df.columns else 0)
        z_column = st.selectbox("Colonne coordonnée Z", options=df.columns, index=df.columns.get_loc(z_col_guess) if z_col_guess in df.columns else 0)
        
        # Deviner les colonnes de teneur et tonnage
        grade_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['grade', 'teneur', 'au', 'cu', 'ag', 'zn', 'pb'])), df.columns[3] if len(df.columns) > 3 else df.columns[0])
        tonnage_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['ton', 'mass', 'weight'])), None)
        
        grade_column = st.selectbox("Colonne teneur", options=df.columns, index=df.columns.get_loc(grade_col_guess) if grade_col_guess in df.columns else 0)
        
        if tonnage_col_guess in df.columns:
            tonnage_column = st.selectbox("Colonne tonnage", options=df.columns, index=df.columns.get_loc(tonnage_col_guess))
        else:
            # Si pas de colonne tonnage, proposer de la calculer
            tonnage_column = st.selectbox("Colonne tonnage (ou à calculer)", options=df.columns, index=0)
            calculate_tonnage = st.checkbox("Calculer le tonnage")
            
            if calculate_tonnage:
                density_col_guess = next((col for col in df.columns if any(k in col.lower() for k in ['dens', 'sg', 'specific'])), None)
                
                if density_col_guess in df.columns:
                    density_column = st.selectbox("Colonne densité", options=df.columns, index=df.columns.get_loc(density_col_guess))
                else:
                    density_column = st.selectbox("Colonne densité", options=df.columns, index=0)
                
                default_density = st.number_input("Densité par défaut", min_value=0.1, max_value=10.0, value=2.7, step=0.1)
                block_size_x = st.number_input("Taille X (m)", min_value=0.1, value=5.0, step=0.5)
                block_size_y = st.number_input("Taille Y (m)", min_value=0.1, value=5.0, step=0.5)
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
                    st.success("Tonnage calculé avec succès!")
    
    with col2:
        # Filtres
        st.subheader("Filtres")
        
        # Filtres numériques pour les coordonnées
        x_min, x_max = float(df[x_column].min()), float(df[x_column].max())
        y_min, y_max = float(df[y_column].min()), float(df[y_column].max())
        z_min, z_max = float(df[z_column].min()), float(df[z_column].max())
        
        filter_x = st.slider("Filtre X", min_value=x_min, max_value=x_max, value=(x_min, x_max))
        filter_y = st.slider("Filtre Y", min_value=y_min, max_value=y_max, value=(y_min, y_max))
        filter_z = st.slider("Filtre Z", min_value=z_min, max_value=z_max, value=(z_min, z_max))
        
        # Filtres pour les attributs catégoriels
        categorical_columns = [col for col in df.columns if df[col].dtype == 'object' or df[col].nunique() < 20]
        
        if categorical_columns:
            categorical_filter_column = st.selectbox("Filtre catégoriel", options=["Aucun"] + categorical_columns)
            
            if categorical_filter_column != "Aucun":
                categories = sorted(df[categorical_filter_column].unique())
                selected_categories = st.multiselect("Valeurs à inclure", options=categories, default=categories)
        
        # Filtres sur la teneur
        grade_min, grade_max = float(df[grade_column].min()), float(df[grade_column].max())
        filter_grade = st.slider(f"Filtre teneur ({grade_column})", 
                              min_value=grade_min, 
                              max_value=grade_max, 
                              value=(grade_min, grade_max))
        
        # Filtres spatiaux
        st.subheader("Filtres spatiaux")
        
        spatial_filters = []
        
        if envelope_mesh:
            use_envelope = st.checkbox("Filtrer par enveloppe DXF")
            if use_envelope:
                spatial_filters.append("envelope")
        
        if surface_mesh:
            use_surface = st.checkbox("Filtrer par surface DXF")
            if use_surface:
                surface_relation = st.radio("Relation à la surface", ["Au-dessus", "En-dessous"])
                spatial_filters.append("surface_" + ("above" if surface_relation == "Au-dessus" else "below"))
    
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
                    for idx, row in filtered_df.iterrows():
                        point = [row[x_column], row[y_column], row[z_column]]
                        filtered_df.at[idx, 'in_envelope'] = is_point_in_mesh(point, envelope_mesh)
                    filtered_df = filtered_df[filtered_df['in_envelope']]
            
            elif filter_type.startswith("surface_") and surface_mesh:
                relation = filter_type.split('_')[1]  # "above" ou "below"
                
                with st.spinner(f"Application du filtre de surface DXF ({relation})..."):
                    for idx, row in filtered_df.iterrows():
                        point = [row[x_column], row[y_column], row[z_column]]
                        is_above = is_point_above_surface(point, surface_mesh)
                        filtered_df.at[idx, 'above_surface'] = is_above
                    
                    if relation == "above":
                        filtered_df = filtered_df[filtered_df['above_surface']]
                    else:
                        filtered_df = filtered_df[~filtered_df['above_surface']]
        
        blocks_filtered = original_count - len(filtered_df)
        st.info(f"{blocks_filtered} blocs supprimés par les filtres spatiaux")
    
    # Afficher le nombre de blocs après filtrage
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Résultats des filtres</div>', unsafe_allow_html=True)
    
    percentage = len(filtered_df)/len(df)*100
    
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
            <div class="metric-value">{percentage:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour différentes analyses
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Analyses</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📈 Statistiques", "📉 Courbe Tonnage-Teneur"])
    
    with tabs[0]:
        st.header("Statistiques descriptives")
        
        if not filtered_df.empty:
            stats_df = calculate_statistics(filtered_df, grade_column)
            
            # Afficher les statistiques en format de carte moderne
            col1, col2 = st.columns(2)
            
            with col1:
                # Statistiques de base
                st.subheader("Statistiques de base")
                st.dataframe(stats_df, use_container_width=True)
                
                # Export des statistiques
                if st.button("Exporter les statistiques (CSV)"):
                    csv = stats_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="stats_{grade_column}.csv" class="download-button">Télécharger CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                # Histogramme de la teneur
                st.subheader("Distribution des teneurs")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(filtered_df[grade_column], bins=30, alpha=0.7, color='#3498DB')
                ax.set_xlabel(grade_column)
                ax.set_ylabel('Fréquence')
                ax.set_title(f'Distribution de {grade_column}')
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)
                
        else:
            st.warning("Aucune donnée disponible après application des filtres.")
    
    with tabs[1]:
        st.header("Analyse Tonnage-Teneur")
        
        if tonnage_column in filtered_df.columns and not filtered_df.empty:
            # Configuration des teneurs de coupure
            cutoff_min = float(filtered_df[grade_column].min())
            cutoff_max = float(filtered_df[grade_column].max())
            
            st.subheader("Configuration des teneurs de coupure")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cutoff_range = st.slider("Plage de teneurs de coupure", 
                                       min_value=cutoff_min, 
                                       max_value=cutoff_max,
                                       value=(cutoff_min, cutoff_max))
            
            with col2:
                num_steps = st.slider("Nombre de points sur la courbe", min_value=5, max_value=50, value=20)
            
            # Générer les teneurs de coupure
            cutoffs = np.linspace(cutoff_range[0], cutoff_range[1], num_steps)
            
            # Calculer la courbe tonnage-teneur
            gtc_df = calculate_grade_tonnage_curve(filtered_df, grade_column, tonnage_column, cutoffs)
            
            # Afficher le tableau
            st.subheader("Tableau Tonnage-Teneur")
            st.dataframe(gtc_df, use_container_width=True)
            
            # Créer la courbe
            st.subheader("Courbe Tonnage-Teneur")
            
            fig = go.Figure()
            
            # Courbe de tonnage
            fig.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Tonnage > coupure"],
                name="Tonnage",
                line=dict(color='#3498DB', width=3),
                yaxis="y"
            ))
            
            # Courbe de teneur moyenne
            fig.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Teneur moyenne > coupure"],
                name="Teneur moyenne",
                line=dict(color='#E67E22', width=3),
                yaxis="y2"
            ))
            
            # Mise en page
            fig.update_layout(
                title="Courbe Tonnage-Teneur",
                xaxis=dict(title="Teneur de coupure"),
                yaxis=dict(title="Tonnage", side="left"),
                yaxis2=dict(title="Teneur moyenne", side="right", overlaying="y"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Courbe de contenu métallique
            st.subheader("Courbe de Contenu Métallique")
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=gtc_df["Teneur de coupure"],
                y=gtc_df["Contenu métallique"],
                name="Contenu métallique",
                line=dict(color='#2ECC71', width=3),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.2)'
            ))
            
            fig2.update_layout(
                title="Contenu Métallique vs Teneur de Coupure",
                xaxis=dict(title="Teneur de coupure"),
                yaxis=dict(title="Contenu métallique"),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Export des résultats
            st.subheader("Export des résultats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exporter en CSV"):
                    csv = gtc_df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="tonnage_teneur.csv" class="download-button">Télécharger CSV</a>'
                    st.markdown(href, unsafe_allow_html=True)
            
            with col2:
                if st.button("Exporter en Excel"):
                    # Excel export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        gtc_df.to_excel(writer, sheet_name='Tonnage_Teneur', index=False)
                    
                    b64 = base64.b64encode(output.getvalue()).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="tonnage_teneur.xlsx" class="download-button">Télécharger Excel</a>'
                    st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning(f"Colonne de tonnage '{tonnage_column}' non trouvée ou aucune donnée disponible après filtrage.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer avec copyright
st.markdown("""
<div class="footer">
    <p>
        Block Model Analyzer v1.0.0<br>
        © 2025 Didier Ouedraogo, P.Geo. Tous droits réservés.
    </p>
</div>
""", unsafe_allow_html=True)