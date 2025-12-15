"""
Programme principal - Fusion de petits fichiers pour système HDFS
Utilise le clustering hiérarchique agglomératif avec single-linkage.

Auteur: Projet HDFS
Date: 2025
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.small_file import SmallFile, HDFS_BLOCK_SIZE_MB, SMALL_FILE_THRESHOLD, SMALL_FILE_MAX_SIZE_MB
from models.cluster import Cluster
from core.distance_matrix import DistanceMatrix
from core.clustering import AgglomerativeClustering
from core.merger import FileMerger
from core.namenode_memory import NameNodeMemory
from core.file_index import FileIndex
from data_io.file_generator import FileGenerator
from data_io.metadata_writer import MetadataWriter


def print_header():
    """Affiche l'en-tête du programme."""
    print("\n" + "="*80)
    print(" "*20 + "SYSTÈME DE FUSION DE FICHIERS HDFS")
    print(" "*15 + "Clustering Hiérarchique Agglomératif")
    print(" "*20 + "Méthode: Single-Linkage")
    print(" "*15 + "Basé sur l'article de recherche HDFS")
    print("="*80)
    print(f"\n📋 Configuration (selon article de recherche):")
    print(f"  • Taille de bloc HDFS: {HDFS_BLOCK_SIZE_MB} MB")
    print(f"  • Seuil petits fichiers: {SMALL_FILE_THRESHOLD * 100:.0f}% = {SMALL_FILE_MAX_SIZE_MB} MB")
    print(f"  • Fichiers < {SMALL_FILE_MAX_SIZE_MB} MB → éligibles pour fusion")
    print(f"  • Fichiers ≥ {SMALL_FILE_MAX_SIZE_MB} MB → traités directement en HDFS")
    print("="*80 + "\n")


def print_footer():
    """Affiche le pied de page du programme."""
    print("\n" + "="*80)
    print(" "*25 + "TRAITEMENT TERMINÉ AVEC SUCCÈS")
    print("="*80 + "\n")


def example_1_realistic_scenario():
    """
    Exemple 1: Scénario réaliste avec génération automatique de fichiers.
    
    Utilise un mélange de fichiers de différentes tailles pour simuler
    un environnement HDFS typique.
    """
    print("\n" + "-"*80)
    print("EXEMPLE 1: SCÉNARIO RÉALISTE (FICHIERS MIXTES)")
    print("-"*80)
    
    # Paramètres
    max_cluster_size = 128.0  # MB
    output_dir = "output"
    
    # 1. Générer des fichiers de test
    generator = FileGenerator(seed=42)
    files = generator.generate_realistic_scenario("mixed")
    FileGenerator.display_files(files, max_display=15)
    
    # 2. Appliquer le clustering
    clustering = AgglomerativeClustering(max_cluster_size_mb=max_cluster_size)
    clusters = clustering.fit(files)
    
    # 3. Afficher les statistiques
    stats = clustering.get_statistics()
    print(f"\n📊 STATISTIQUES DU CLUSTERING (selon article):")
    print(f"  Fichiers analysés:")
    print(f"    - Total reçu: {stats.get('total_files_received', 0)}")
    print(f"    - Petits fichiers (< {stats.get('threshold_mb', 96)} MB): {stats.get('small_files_processed', 0)}")
    print(f"    - Exclus (≥ {stats.get('threshold_mb', 96)} MB): {stats.get('files_excluded', 0)}")
    print(f"\n  Résultats du clustering:")
    print(f"    - Clusters créés: {stats['num_clusters']}")
    print(f"    - Taille moyenne: {stats.get('avg_cluster_size_mb', 0):.2f} MB")
    print(f"    - Taille min: {stats.get('min_cluster_size_mb', 0):.2f} MB")
    print(f"    - Taille max: {stats.get('max_cluster_size_mb', 0):.2f} MB")
    print(f"    - Fichiers/cluster: {stats.get('avg_files_per_cluster', 0):.2f}")
    print(f"    - Itérations: {stats['iterations']}")
    
    # 4. Afficher le dendrogramme (selon article)
    clustering.dendrogram.print_tree()
    clustering.dendrogram.print_merge_history()
    
    # 5. Analyse mémoire NameNode (selon article)
    namenode = NameNodeMemory()
    print(namenode.get_detailed_report(files, clusters))
    
    # 6. Fusionner les fichiers
    merger = FileMerger(output_dir=output_dir)
    merged_files = merger.merge_all_clusters(clusters)
    
    # 7. Créer l'index de fichiers (pour récupération)
    file_index = FileIndex()
    file_index.build_index(clusters)
    file_index.print_index()
    
    # 8. Écrire les métadonnées
    metadata_writer = MetadataWriter(output_dir=output_dir)
    metadata_writer.write_all_metadata(clusters, summary_filename="example1_clusters.json")
    metadata_writer.write_detailed_report(clusters, len(files), filename="example1_report.txt")
    
    # 9. Afficher les étapes de l'algorithme
    clustering.print_algorithm_steps()
    
    print(f"\n✓ Exemple 1 terminé - Résultats dans le dossier '{output_dir}'")


def example_2_custom_files():
    """
    Exemple 2: Liste personnalisée de fichiers.
    
    Crée manuellement une liste de fichiers pour démontrer
    le fonctionnement du clustering sur des données spécifiques.
    """
    print("\n" + "-"*80)
    print("EXEMPLE 2: LISTE PERSONNALISÉE DE FICHIERS")
    print("-"*80)
    
    # Créer manuellement une liste de fichiers
    files = [
        SmallFile("doc1.txt", 10.0),
        SmallFile("doc2.txt", 12.0),
        SmallFile("img1.jpg", 25.0),
        SmallFile("video1.mp4", 45.0),
        SmallFile("data1.csv", 8.0),
        SmallFile("data2.csv", 9.0),
        SmallFile("img2.jpg", 28.0),
        SmallFile("doc3.txt", 11.0),
        SmallFile("video2.mp4", 48.0),
        SmallFile("archive.zip", 35.0),
        SmallFile("backup.tar", 33.0),
        SmallFile("log1.log", 5.0),
        SmallFile("log2.log", 6.0),
        SmallFile("config.xml", 2.0),
        SmallFile("script.py", 3.0),
    ]
    
    print(f"\nFichiers créés: {len(files)}")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    
    # 1. Clustering avec algorithme agglomératif hiérarchique
    print("\n" + "="*80)
    print("PHASE DE CLUSTERING")
    print("="*80)
    clustering = AgglomerativeClustering(max_cluster_size_mb=128.0)
    clusters = clustering.fit(files)
    
    # 2. Afficher le dendrogramme
    print("\n" + "="*80)
    print("DENDROGRAMME (Structure Hiérarchique)")
    print("="*80)
    clustering.dendrogram.print_tree()
    clustering.dendrogram.print_merge_history()
    
    # 3. Analyse mémoire NameNode
    print("\n" + "="*80)
    print("ANALYSE MÉMOIRE NAMENODE")
    print("="*80)
    namenode = NameNodeMemory()
    print(namenode.get_detailed_report(files, clusters))
    
    # 4. Fusion des fichiers
    print("\n" + "="*80)
    print("FUSION DES FICHIERS")
    print("="*80)
    merger = FileMerger(output_dir="output")
    merger.merge_all_clusters(clusters)
    
    # 5. Créer l'index de fichiers
    file_index = FileIndex()
    file_index.build_index(clusters)
    file_index.print_index()
    
    # 6. Écrire les métadonnées
    metadata_writer = MetadataWriter(output_dir="output")
    metadata_writer.write_all_metadata(clusters, summary_filename="example2_clusters.json")
    metadata_writer.write_detailed_report(clusters, len(files), filename="example2_report.txt")
    
    # 7. Afficher les étapes de l'algorithme
    clustering.print_algorithm_steps()
    
    print(f"\n✓ Exemple 2 terminé - Résultats dans le dossier 'output'")


def example_3_small_files():
    """
    Exemple 3: Beaucoup de très petits fichiers.
    
    Simule le scénario typique du "small files problem" dans HDFS
    où de nombreux petits fichiers créent une surcharge de métadonnées.
    """
    print("\n" + "-"*80)
    print("EXEMPLE 3: PROBLÈME DES PETITS FICHIERS (SMALL FILES PROBLEM)")
    print("-"*80)
    
    # Générer beaucoup de petits fichiers
    generator = FileGenerator(seed=123)
    files = generator.generate_realistic_scenario("small")
    
    print(f"\nNombre de fichiers: {len(files)}")
    print(f"Taille totale: {sum(f.size_mb for f in files):.2f} MB")
    print(f"Taille moyenne: {sum(f.size_mb for f in files) / len(files):.2f} MB")
    
    # 1. Clustering avec algorithme agglomératif hiérarchique
    print("\n" + "="*80)
    print("PHASE DE CLUSTERING")
    print("="*80)
    clustering = AgglomerativeClustering(max_cluster_size_mb=128.0)
    clusters = clustering.fit(files)
    
    # 2. Calculer le taux de réduction
    reduction_rate = (1 - len(clusters) / len(files)) * 100
    print(f"\n📊 RÉSULTAT:")
    print(f"  Fichiers originaux: {len(files)}")
    print(f"  Clusters créés: {len(clusters)}")
    print(f"  Réduction: {reduction_rate:.2f}%")
    print(f"  → Économie de {len(files) - len(clusters)} entrées de métadonnées!")
    
    # 3. Afficher le dendrogramme
    print("\n" + "="*80)
    print("DENDROGRAMME (Structure Hiérarchique)")
    print("="*80)
    clustering.dendrogram.print_tree()
    clustering.dendrogram.print_merge_history()
    
    # 4. Analyse mémoire NameNode
    print("\n" + "="*80)
    print("ANALYSE MÉMOIRE NAMENODE")
    print("="*80)
    namenode = NameNodeMemory()
    print(namenode.get_detailed_report(files, clusters))
    
    # 5. Fusion des fichiers
    print("\n" + "="*80)
    print("FUSION DES FICHIERS")
    print("="*80)
    merger = FileMerger(output_dir="output")
    merger.merge_all_clusters(clusters)
    
    # 6. Créer l'index de fichiers
    file_index = FileIndex()
    file_index.build_index(clusters)
    file_index.print_index()
    
    # 7. Écrire les métadonnées
    metadata_writer = MetadataWriter(output_dir="output")
    metadata_writer.write_all_metadata(clusters, summary_filename="example3_clusters.json")
    metadata_writer.write_detailed_report(clusters, len(files), filename="example3_report.txt")
    
    # 8. Afficher les étapes de l'algorithme
    clustering.print_algorithm_steps()
    
    print(f"\n✓ Exemple 3 terminé - Résultats dans le dossier 'output'")


def interactive_mode():
    """
    Mode interactif permettant à l'utilisateur de configurer le clustering.
    """
    print("\n" + "-"*80)
    print("MODE INTERACTIF")
    print("-"*80)
    
    try:
        # Demander le nombre de fichiers
        num_files = int(input("\nNombre de fichiers à générer (ex: 30): "))
        
        # Demander la taille maximale du cluster
        max_size = float(input("Taille maximale d'un cluster en MB (ex: 128): "))
        
        # Demander le type de scénario
        print("\nScénarios disponibles:")
        print("  1. Mixed (mélange)")
        print("  2. Small (petits fichiers)")
        print("  3. Medium (fichiers moyens)")
        print("  4. Large (gros fichiers)")
        scenario_choice = input("Choisir un scénario (1-4): ")
        
        scenario_map = {
            "1": "mixed",
            "2": "small",
            "3": "medium",
            "4": "large"
        }
        scenario = scenario_map.get(scenario_choice, "mixed")
        
        # Générer les fichiers
        generator = FileGenerator()
        
        if num_files <= 20:
            files = generator.generate_realistic_scenario(scenario)
        else:
            files = generator.generate(num_files)
        
        FileGenerator.display_files(files, max_display=10)
        
        # Clustering
        clustering = AgglomerativeClustering(max_cluster_size_mb=max_size)
        clusters = clustering.fit(files)
        
        # Fusion et métadonnées
        merger = FileMerger(output_dir="output")
        merger.merge_all_clusters(clusters)
        
        metadata_writer = MetadataWriter(output_dir="output")
        metadata_writer.write_all_metadata(clusters, summary_filename="interactive_clusters.json")
        metadata_writer.write_detailed_report(clusters, len(files), filename="interactive_report.txt")
        
        print(f"\n✓ Traitement terminé - Résultats dans le dossier 'output'")
        
    except ValueError as e:
        print(f"\n❌ Erreur de saisie: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠ Opération annulée par l'utilisateur.")


def main():
    """
    Fonction principale du programme.
    """
    print_header()
    
    # Menu principal
    print("Choisissez un mode d'exécution:\n")
    print("  1. Exemple 1: Scénario réaliste (fichiers mixtes)")
    print("  2. Exemple 2: Liste personnalisée de fichiers")
    print("  3. Exemple 3: Problème des petits fichiers")
    print("  4. Mode interactif")
    print("  5. Exécuter tous les exemples")
    print("  0. Quitter\n")
    
    choice = input("Votre choix (0-5): ").strip()
    
    if choice == "1":
        example_1_realistic_scenario()
    elif choice == "2":
        example_2_custom_files()
    elif choice == "3":
        example_3_small_files()
    elif choice == "4":
        interactive_mode()
    elif choice == "5":
        example_1_realistic_scenario()
        example_2_custom_files()
        example_3_small_files()
    elif choice == "0":
        print("\nAu revoir!")
        return
    else:
        print("\n❌ Choix invalide. Exécution de l'exemple 1 par défaut...\n")
        example_1_realistic_scenario()
    
    print_footer()


if __name__ == "__main__":
    main()
