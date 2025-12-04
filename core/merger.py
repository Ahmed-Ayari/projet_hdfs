"""
Classe pour fusionner physiquement les fichiers d'un cluster.
"""

import os
from typing import List
from models.cluster import Cluster


class FileMerger:
    """
    Responsable de la fusion physique des fichiers dans un cluster.
    
    Crée un fichier binaire fusionné pour chaque cluster en concaténant
    les contenus des fichiers individuels.
    
    Attributes:
        output_dir (str): Répertoire où seront sauvegardés les fichiers fusionnés
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialise le FileMerger.
        
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
            print(f"Répertoire de sortie créé: {self.output_dir}")
    
    def merge_cluster(self, cluster: Cluster) -> str:
        """
        Fusionne tous les fichiers d'un cluster en un seul fichier.
        
        Crée un fichier binaire nommé cluster_<id>.bin contenant
        les données simulées de tous les fichiers du cluster.
        
        Args:
            cluster (Cluster): Le cluster à fusionner
            
        Returns:
            str: Chemin du fichier fusionné créé
        """
        output_filename = f"cluster_{cluster.cluster_id}.bin"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Créer un fichier binaire fusionné
        with open(output_path, 'wb') as merged_file:
            for file in cluster.files:
                # Simuler le contenu du fichier
                # Dans un vrai système, on lirait les fichiers réels
                file_data = self._simulate_file_content(file.name, file.size_mb)
                merged_file.write(file_data)
        
        actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  → Fichier créé: {output_filename} ({actual_size_mb:.2f} MB)")
        
        return output_path
    
    def _simulate_file_content(self, filename: str, size_mb: float) -> bytes:
        """
        Simule le contenu d'un fichier.
        
        Crée des données binaires simulées pour représenter un fichier.
        Dans un système réel, on lirait le vrai contenu du fichier.
        
        Args:
            filename (str): Nom du fichier
            size_mb (float): Taille souhaitée en MB
            
        Returns:
            bytes: Données binaires simulées
        """
        # Calculer le nombre d'octets
        num_bytes = int(size_mb * 1024 * 1024)
        
        # Créer un en-tête avec le nom du fichier
        header = f"FILE: {filename}\n".encode('utf-8')
        
        # Remplir avec des données (répétition d'un pattern)
        pattern = b'X' * 1024  # 1 KB de données
        num_patterns = (num_bytes - len(header)) // len(pattern)
        remainder = (num_bytes - len(header)) % len(pattern)
        
        content = header + (pattern * num_patterns) + (pattern[:remainder])
        
        return content
    
    def merge_all_clusters(self, clusters: List[Cluster]) -> List[str]:
        """
        Fusionne tous les clusters en fichiers séparés.
        
        Args:
            clusters (List[Cluster]): Liste des clusters à fusionner
            
        Returns:
            List[str]: Liste des chemins des fichiers créés
        """
        print(f"\n{'='*60}")
        print(f"FUSION DES FICHIERS")
        print(f"{'='*60}")
        print(f"Nombre de clusters à fusionner: {len(clusters)}")
        
        merged_files = []
        
        for idx, cluster in enumerate(clusters, 1):
            print(f"\nCluster {cluster.cluster_id} ({len(cluster.files)} fichiers, "
                  f"{cluster.get_total_size():.2f} MB):")
            
            output_path = self.merge_cluster(cluster)
            merged_files.append(output_path)
        
        print(f"\n{'='*60}")
        print(f"FUSION TERMINÉE")
        print(f"{'='*60}")
        print(f"Fichiers créés: {len(merged_files)}")
        print(f"Répertoire: {self.output_dir}")
        
        return merged_files
    
    def get_merge_summary(self, clusters: List[Cluster]) -> dict:
        """
        Génère un résumé de la fusion.
        
        Args:
            clusters (List[Cluster]): Liste des clusters
            
        Returns:
            dict: Résumé avec statistiques
        """
        total_files = sum(len(c.files) for c in clusters)
        total_size = sum(c.get_total_size() for c in clusters)
        
        return {
            "total_clusters": len(clusters),
            "total_files": total_files,
            "total_size_mb": round(total_size, 2),
            "reduction_rate": round((1 - len(clusters) / total_files) * 100, 2) if total_files > 0 else 0,
            "output_directory": self.output_dir
        }
