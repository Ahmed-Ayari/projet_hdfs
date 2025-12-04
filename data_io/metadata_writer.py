"""
Classe pour écrire les métadonnées des clusters au format JSON.
"""

import json
import os
from typing import List
from models.cluster import Cluster


class MetadataWriter:
    """
    Écrit les métadonnées des clusters dans des fichiers JSON.
    
    Crée des fichiers JSON décrivant chaque cluster (fichiers contenus,
    taille totale, etc.) pour faciliter la gestion et le suivi.
    
    Attributes:
        output_dir (str): Répertoire où seront sauvegardés les fichiers de métadonnées
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialise le MetadataWriter.
        
        Args:
            output_dir (str): Chemin du répertoire de sortie
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """
        Crée le répertoire de sortie s'il n'existe pas.
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def write_cluster_metadata(self, cluster: Cluster, filename: str = None) -> str:
        """
        Écrit les métadonnées d'un cluster dans un fichier JSON.
        
        Args:
            cluster (Cluster): Le cluster dont on veut écrire les métadonnées
            filename (str): Nom du fichier (optionnel)
            
        Returns:
            str: Chemin du fichier créé
        """
        if filename is None:
            filename = f"cluster_{cluster.cluster_id}_metadata.json"
        
        output_path = os.path.join(self.output_dir, filename)
        
        metadata = cluster.to_dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def write_all_metadata(self, clusters: List[Cluster], summary_filename: str = "clusters_summary.json") -> str:
        """
        Écrit les métadonnées de tous les clusters dans un fichier unique.
        
        Args:
            clusters (List[Cluster]): Liste des clusters
            summary_filename (str): Nom du fichier de synthèse
            
        Returns:
            str: Chemin du fichier créé
        """
        print(f"\n{'='*60}")
        print(f"ÉCRITURE DES MÉTADONNÉES")
        print(f"{'='*60}")
        
        output_path = os.path.join(self.output_dir, summary_filename)
        
        # Créer un dictionnaire avec toutes les métadonnées
        all_metadata = {
            "total_clusters": len(clusters),
            "clusters": [cluster.to_dict() for cluster in clusters],
            "summary": self._generate_summary(clusters)
        }
        
        # Écrire dans le fichier JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Métadonnées écrites dans: {summary_filename}")
        print(f"Nombre de clusters: {len(clusters)}")
        
        # Écrire aussi un fichier individuel pour chaque cluster
        for cluster in clusters:
            self.write_cluster_metadata(cluster)
        
        print(f"Fichiers individuels créés: {len(clusters)}")
        
        return output_path
    
    def _generate_summary(self, clusters: List[Cluster]) -> dict:
        """
        Génère un résumé statistique des clusters.
        
        Args:
            clusters (List[Cluster]): Liste des clusters
            
        Returns:
            dict: Résumé avec statistiques
        """
        if not clusters:
            return {}
        
        total_files = sum(len(c.files) for c in clusters)
        total_size = sum(c.get_total_size() for c in clusters)
        sizes = [c.get_total_size() for c in clusters]
        file_counts = [len(c.files) for c in clusters]
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size, 2),
            "average_cluster_size_mb": round(total_size / len(clusters), 2),
            "min_cluster_size_mb": round(min(sizes), 2),
            "max_cluster_size_mb": round(max(sizes), 2),
            "average_files_per_cluster": round(total_files / len(clusters), 2),
            "min_files_per_cluster": min(file_counts),
            "max_files_per_cluster": max(file_counts),
            "file_reduction_rate_percent": round((1 - len(clusters) / total_files) * 100, 2) if total_files > 0 else 0
        }
    
    def write_detailed_report(self, clusters: List[Cluster], 
                             original_file_count: int,
                             filename: str = "detailed_report.txt") -> str:
        """
        Génère un rapport détaillé en format texte.
        
        Args:
            clusters (List[Cluster]): Liste des clusters
            original_file_count (int): Nombre de fichiers original
            filename (str): Nom du fichier de rapport
            
        Returns:
            str: Chemin du fichier créé
        """
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RAPPORT DE FUSION DE FICHIERS HDFS\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Nombre de fichiers originaux: {original_file_count}\n")
            f.write(f"Nombre de clusters créés: {len(clusters)}\n")
            
            if original_file_count > 0:
                reduction = (1 - len(clusters) / original_file_count) * 100
                f.write(f"Taux de réduction: {reduction:.2f}%\n\n")
            
            f.write("-"*80 + "\n")
            f.write("DÉTAILS DES CLUSTERS\n")
            f.write("-"*80 + "\n\n")
            
            for cluster in sorted(clusters, key=lambda c: c.cluster_id):
                f.write(f"Cluster ID: {cluster.cluster_id}\n")
                f.write(f"  Nombre de fichiers: {len(cluster.files)}\n")
                f.write(f"  Taille totale: {cluster.get_total_size():.2f} MB\n")
                f.write(f"  Fichiers:\n")
                
                for file in sorted(cluster.files, key=lambda f: f.name):
                    f.write(f"    - {file.name} ({file.size_mb:.2f} MB)\n")
                
                f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("="*80 + "\n")
        
        print(f"Rapport détaillé écrit dans: {filename}")
        
        return output_path
