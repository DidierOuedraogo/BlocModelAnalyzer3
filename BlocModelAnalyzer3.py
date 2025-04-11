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
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour une interface moderne avec meilleure lisibilité dans la navigation
st.markdown("""
<style>
    /* Thème moderne avec une palette de couleurs minières */
    :root {
        --primary: #2C3E50;
        --secondary: #E67E22;
        --background: #ECF0F1;
        --text: #2C3E50;
        --accent: #3498DB;
    }
    
    /* En-tête et titre */
    .main-header {
        background-color: var(--primary);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .author {
        margin-top: 0.5rem;
        font-style: italic;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Cartes pour les sections */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
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
    
    /* Badge pour les compteurs et statistiques */
    .badge {
        background-color: var(--accent);
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        font-size: 0.8rem;
        color: grey;
    }
    
    /* Tabs design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 6px 6px 0 0;
        font-weight: 500;
        color: var(--text);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }
    
    /* Sidebar with better text visibility */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 0;
    }
    
    [data-testid="stSidebarNav"] {
        background-color: #f0f2f6;
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] .stMarkdown {
        color: #2C3E50 !important;
    }
    
    /* Sidebar headings */
    .sidebar-heading {
        color: #2C3E50 !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--secondary);
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #D35400;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Info box */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid var(--accent);
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Version badge */
    .version-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background-color: var(--accent);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Guide styling */
    .guide-header {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent);
    }
    
    .guide-section {
        margin-bottom: 1.5rem;
    }
    
    .guide-section h3 {
        color: var(--primary);
        border-bottom: 1px solid #eee;
        padding-bottom: 0.5rem;
    }
    
    .download-button {
        display: inline-block;
        background-color: var(--accent);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .download-button:hover {
        background-color: #2980b9;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
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

# Fonction pour afficher le guide utilisateur
def show_user_guide():
    st.markdown("""
    <div class="guide-header">
        <h2>Guide de l'Utilisateur</h2>
        <p>Bienvenue dans Block Model Analyzer. Ce guide vous aidera à tirer le meilleur parti de l'application.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Introduction et fonctionnalités"):
        st.markdown("""
        <div class="guide-section">
            <h3>Introduction</h3>
            <p><b>Block Model Analyzer</b> est une application web interactive développée en Python avec Streamlit, conçue pour les géologues, ingénieurs miniers et professionnels des ressources qui travaillent avec des modèles de blocs. Elle permet d'analyser rapidement les modèles de blocs miniers, de calculer des statistiques descriptives, de générer des courbes tonnage-teneur et d'appliquer des contraintes spatiales via des fichiers DXF pour des estimations de ressources plus précises.</p>
            
            <h3>Fonctionnalités principales</h3>
            <ul>
                <li><b>Chargement de différents formats de données</b> (CSV, Excel)</li>
                <li><b>Intégration de fichiers DXF</b> pour contraintes spatiales</li>
                <li><b>Filtres intuitifs</b> sur coordonnées, teneurs et attributs catégoriels</li>
                <li><b>Calcul automatique du tonnage</b> à partir des dimensions et densités</li>
                <li><b>Statistiques descriptives complètes</b></li>
                <li><b>Courbes tonnage-teneur interactives</b></li>
                <li><b>Visualisation 3D</b> du modèle de blocs</li>
                <li><b>Export des résultats</b> aux formats CSV et Excel</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📂 Chargement des données"):
        st.markdown("""
        <div class="guide-section">
            <h3>Formats supportés</h3>
            <p>L'application prend en charge les formats suivants :</p>
            <ul>
                <li><b>CSV</b> (.csv) - Spécifiez le délimiteur et le séparateur décimal</li>
                <li><b>Excel</b> (.xlsx, .xls) - Spécifiez le nom de la feuille si nécessaire</li>
            </ul>
            
            <h3>Structure du modèle de blocs</h3>
            <p>Votre modèle de blocs doit contenir au minimum :</p>
            <ul>
                <li>Coordonnées (X, Y, Z)</li>
                <li>Teneurs</li>
                <li>Tonnage (ou densité pour le calculer)</li>
            </ul>
            
            <h3>Fichiers DXF</h3>
            <p>Vous pouvez charger deux types de fichiers DXF :</p>
            <ul>
                <li><b>Enveloppe minéralisée</b> - Un solide fermé définissant une zone d'intérêt</li>
                <li><b>Surface</b> - Une surface comme une topographie ou une conception de fosse</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Configuration et filtrage"):
        st.markdown("""
        <div class="guide-section">
            <h3>Sélection des colonnes</h3>
            <p>Après le chargement des données, vous devez spécifier :</p>
            <ul>
                <li>Les colonnes de coordonnées (X, Y, Z)</li>
                <li>La colonne de teneur</li>
                <li>La colonne de tonnage (ou les paramètres pour la calculer)</li>
            </ul>
            
            <h3>Calcul du tonnage</h3>
            <p>Si votre modèle ne contient pas de tonnage, vous pouvez le calculer en spécifiant :</p>
            <ul>
                <li>La colonne de densité (ou une valeur par défaut)</li>
                <li>Les dimensions du bloc (X, Y, Z)</li>
            </ul>
            
            <h3>Types de filtres</h3>
            <ul>
                <li><b>Filtres de coordonnées</b> - Limitez l'analyse à une zone spatiale spécifique</li>
                <li><b>Filtres de teneur</b> - Spécifiez une plage de teneurs à inclure</li>
                <li><b>Filtres catégoriels</b> - Sélectionnez des attributs spécifiques (types de roche, domaines...)</li>
                <li><b>Filtres spatiaux</b> - Contraignez l'analyse en fonction des fichiers DXF</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📊 Analyses disponibles"):
        st.markdown("""
        <div class="guide-section">
            <h3>Statistiques descriptives</h3>
            <p>L'onglet Statistiques fournit :</p>
            <ul>
                <li>Nombre de blocs, tonnage total</li>
                <li>Minimum, maximum, moyenne, médiane</li>
                <li>Écart-type, coefficient de variation</li>
                <li>Quartiles</li>
                <li>Histogramme de la distribution des teneurs</li>
            </ul>
            
            <h3>Courbes tonnage-teneur</h3>
            <p>L'onglet Courbe Tonnage-Teneur permet de :</p>
            <ul>
                <li>Définir une plage de teneurs de coupure</li>
                <li>Spécifier le nombre de points sur la courbe</li>
                <li>Visualiser un tableau détaillé des résultats</li>
                <li>Afficher une courbe interactive tonnage vs teneur moyenne</li>
                <li>Générer une courbe de contenu métallique</li>
            </ul>
            
            <h3>Visualisation 3D</h3>
            <p>L'onglet Visualisation 3D offre :</p>
            <ul>
                <li>Un nuage de points 3D coloré selon la teneur</li>
                <li>Des contrôles intuitifs de rotation, zoom et déplacement</li>
                <li>Des options de personnalisation (taille des points, palette de couleurs)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("💾 Export des résultats"):
        st.markdown("""
        <div class="guide-section">
            <h3>Formats d'export</h3>
            <ul>
                <li><b>CSV</b> - Format texte tabulaire compatible avec Excel, R, etc.</li>
                <li><b>Excel</b> - Feuilles de calcul au format .xlsx</li>
            </ul>
            
            <h3>Types de résultats exportables</h3>
            <ul>
                <li><b>Statistiques descriptives</b> - Via l'onglet Statistiques</li>
                <li><b>Tableaux tonnage-teneur</b> - Via l'onglet Courbe Tonnage-Teneur</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚠️ Dépannage et conseils"):
        st.markdown("""
        <div class="guide-section">
            <h3>Problèmes courants</h3>
            <table>
                <tr>
                    <th>Problème</th>
                    <th>Solution</th>
                </tr>
                <tr>
                    <td>Erreur de chargement de fichier</td>
                    <td>Vérifiez le format, le délimiteur et le séparateur décimal</td>
                </tr>
                <tr>
                    <td>Calculs spatiaux lents</td>
                    <td>Réduisez la taille du modèle ou simplifiez le DXF</td>
                </tr>
                <tr>
                    <td>Visualisation 3D lente</td>
                    <td>Appliquez plus de filtres pour réduire le nombre de points</td>
                </tr>
                <tr>
                    <td>Erreur "Memory Error"</td>
                    <td>Échantillonnez votre modèle ou augmentez la RAM disponible</td>
                </tr>
            </table>
            
            <h3>Conseils d'utilisation</h3>
            <ul>
                <li>Commencez par appliquer des filtres pour réduire la taille du jeu de données</li>
                <li>Pour les grands modèles, utilisez d'abord un échantillon représentatif</li>
                <li>Enregistrez régulièrement vos résultats d'analyse</li>
                <li>Pour les fichiers DXF, utilisez des modèles simplifiés si possible</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📞 Contact et support"):
        st.markdown("""
        <div class="guide-section">
            <h3>Besoin d'aide ?</h3>
            <p>Pour toute question ou suggestion d'amélioration :</p>
            
            <p><b>Didier Ouedraogo, P.Geo</b><br>
            Email: didier.ouedraogo@mining-analytics.com<br>
            LinkedIn: <a href="https://linkedin.com/in/didierouedraogo">linkedin.com/in/didierouedraogo</a><br>
            GitHub: <a href="https://github.com/didier-ouedraogo">github.com/didier-ouedraogo</a></p>
            
            <p><i>© 2025 Didier Ouedraogo. Tous droits réservés.</i></p>
        </div>
        """, unsafe_allow_html=True)

# Barre latérale pour les contrôles
with st.sidebar:
    tab1, tab2 = st.tabs(["📊 Application", "📘 Guide"])
    
    with tab1:
        st.markdown('<h2 class="sidebar-heading">Chargement des données</h2>', unsafe_allow_html=True)
        
        # Uploader de fichier de modèle de blocs
        block_model_file = st.file_uploader("Importer fichier de modèle de blocs", 
                                       type=["csv", "xlsx", "xls"],
                                       help="Formats supportés: CSV, Excel")
        
        # Options supplémentaires pour le chargement du fichier
        if block_model_file is not None:
            file_type = block_model_file.name.split('.')[-1].lower()
            if file_type == 'csv':
                delimiter = st.selectbox("Délimiteur", options=[",", ";", "\t"], index=0)
                decimal = st.selectbox("Séparateur décimal", options=[".", ","], index=0)
            else:
                sheet_name = st.text_input("Nom de la feuille Excel (vide = première feuille)", "")
                
        # Uploader de fichiers DXF
        st.markdown('<h3 class="sidebar-heading">Fichiers DXF (optionnels)</h3>', unsafe_allow_html=True)
        envelopes_file = st.file_uploader("Importer un fichier d'enveloppe DXF", type=["dxf"])
        surface_file = st.file_uploader("Importer un fichier de surface DXF (topographie, fosse)", type=["dxf"])
        
        # Informations sur l'application
        st.markdown('<div style="margin-top:3rem;"><hr></div>', unsafe_allow_html=True)
        st.markdown("""
        <div>
            <b>Block Model Analyzer v1.0.0</b><br>
            © 2025 Didier Ouedraogo, P.Geo<br><br>
            Application pour l'analyse statistique et l'évaluation de ressources minières.<br><br>
            <b>Fonctionnalités:</b>
            <ul style="margin-left:1rem;padding-left:0;">
                <li>Chargement de modèles de blocs</li>
                <li>Intégration de contraintes DXF</li>
                <li>Analyse statistique descriptive</li>
                <li>Courbes tonnage-teneur interactives</li>
                <li>Visualisation 3D simplifiée</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        show_user_guide()

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
            
            st.markdown(f"""
            <div class="info-box">
                <b>Données chargées avec succès!</b><br>
                Fichier: <i>{block_model_file.name}</i><br>
                <span class="badge">{len(df)} enregistrements</span>
                <span class="badge">{len(df.columns)} colonnes</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")

# Charger les fichiers DXF si présents
envelope_mesh = None
if envelopes_file is not None:
    with st.spinner("Chargement de l'enveloppe DXF..."):
        envelope_mesh = load_dxf_as_mesh(envelopes_file, is_surface=False)
        if envelope_mesh:
            st.success(f"Enveloppe DXF chargée avec succès: {envelopes_file.name}")
        else:
            st.warning("Impossible de charger l'enveloppe DXF comme maillage fermé")

surface_mesh = None
if surface_file is not None:
    with st.spinner("Chargement de la surface DXF..."):
        surface_mesh = load_dxf_as_mesh(surface_file, is_surface=True)
        if surface_mesh:
            st.success(f"Surface DXF chargée avec succès: {surface_file.name}")
        else:
            st.warning("Impossible de charger la surface DXF")

# Traitement et analyse des données
if df is not None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔍 Configuration de l\'analyse</div>', unsafe_allow_html=True)
    
    # Afficher l'aperçu des données
    st.subheader("Aperçu des données")
    st.dataframe(df.head())
    
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
                
                default_density = st.number_input("Densité par défaut (si non spécifiée)", min_value=0.1, max_value=10.0, value=2.7, step=0.1)
                block_size_x = st.number_input("Taille de bloc X (m)", min_value=0.1, value=5.0, step=0.5)
                block_size_y = st.number_input("Taille de bloc Y (m)", min_value=0.1, value=5.0, step=0.5)
                block_size_z = st.number_input("Taille de bloc Z (m)", min_value=0.1, value=5.0, step=0.5)
                
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
        st.markdown(f"""
        <div class="info-box">
            <b>Filtres spatiaux appliqués:</b><br>
            <span class="badge">{blocks_filtered} blocs supprimés</span>
            <span class="badge">{len(filtered_df)} blocs restants</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Afficher le nombre de blocs après filtrage
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Résultats des filtres</div>', unsafe_allow_html=True)
    
    percentage = len(filtered_df)/len(df)*100
    color = "green" if percentage > 50 else "orange" if percentage > 20 else "red"
    
    st.markdown(f"""
    <div style="display:flex;align-items:center;margin-bottom:1rem;">
        <div style="flex:1;">
            <h3 style="margin:0;font-size:1.1rem;">Blocs après filtrage</h3>
            <p style="margin:0;opacity:0.7;font-size:0.9rem;">Nombre de blocs restants après application de tous les filtres</p>
        </div>
        <div style="text-align:right;">
            <span style="font-size:1.8rem;font-weight:bold;color:{color};">{len(filtered_df):,}</span>
            <span style="font-size:0.9rem;opacity:0.7;"> / {len(df):,} ({percentage:.1f}%)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour différentes analyses
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Analyses</div>', unsafe_allow_html=True)
    
    tabs = st.tabs(["📈 Statistiques", "📉 Courbe Tonnage-Teneur", "🔍 Visualisation 3D"])
    
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
            
            # Mise en page moderne
            fig.update_layout(
                title="Courbe Tonnage-Teneur",
                xaxis=dict(
                    title="Teneur de coupure",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)'
                ),
                yaxis=dict(
                    title="Tonnage",
                    side="left",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)'
                ),
                yaxis2=dict(
                    title="Teneur moyenne",
                    side="right",
                    overlaying="y",
                    showgrid=False
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
                xaxis=dict(
                    title="Teneur de coupure",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)'
                ),
                yaxis=dict(
                    title="Contenu métallique",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.8)'
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
    
    with tabs[2]:
        st.header("Visualisation 3D")
        
        if not filtered_df.empty:
            # Limiter à 3000 points pour la performance
            sample_size = min(3000, len(filtered_df))
            sample_df = filtered_df.sample(sample_size) if len(filtered_df) > sample_size else filtered_df
            
            st.markdown("""
            <div class="info-box">
                <b>Mode de visualisation 3D simplifié</b><br>
                Cette vue présente un échantillon représentatif du modèle. Pour une visualisation plus complète, exportez les données et utilisez un logiciel de visualisation 3D spécialisé.
            </div>
            """, unsafe_allow_html=True)
            
            # Options de visualisation
            col1, col2 = st.columns(2)
            
            with col1:
                marker_size = st.slider("Taille des points", min_value=2, max_value=10, value=3)
            
            with col2:
                color_scale = st.selectbox("Palette de couleurs", 
                                        options=["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Turbo"],
                                        index=0)
            
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
                    opacity=0.8
                ),
                hovertemplate=
                f'X: %{{x:.2f}}<br>'+
                f'Y: %{{y:.2f}}<br>'+
                f'Z: %{{z:.2f}}<br>'+
                f'{grade_column}: %{{marker.color:.2f}}<extra></extra>'
            )])
            
            # Amélioration de l'apparence
            fig.update_layout(
                title=f"Nuage de points 3D du modèle de blocs ({sample_size} points)",
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
                margin=dict(l=0, r=0, b=0, t=40),
                paper_bgcolor='white',
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Légende explicative
            st.markdown("""
            <div style="background-color:#f8f9fa;padding:15px;border-radius:5px;margin-top:20px;font-size:0.9rem;">
                <b>Comment utiliser la visualisation 3D:</b>
                <ul>
                    <li><b>Rotation:</b> Cliquez et faites glisser avec la souris</li>
                    <li><b>Zoom:</b> Utilisez la molette de la souris ou pincez sur un écran tactile</li>
                    <li><b>Pan:</b> Cliquez avec le bouton droit et faites glisser</li>
                    <li><b>Réinitialiser la vue:</b> Double-cliquez sur le graphique</li>
                </ul>
                Les couleurs représentent les valeurs de teneur de {grade_column}.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée disponible pour la visualisation après filtrage.")
    
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