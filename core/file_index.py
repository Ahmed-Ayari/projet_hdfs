"""
Index pour la récupération de fichiers individuels depuis les clusters fusionnés.
Permet de retrouver un fichier spécifique dans un fichier fusionné.
"""

from typing import Dict, List, Optional, Tuple
from models.cluster import Cluster
from models.small_file import SmallFile
import os


class FileIndex:
    """
    Maintient un index pour localiser les fichiers individuels dans les clusters fusionnés.
    
    Selon l'article: "NameNode only maintains the metadata of merged files"
    Cet index permet de retrouver les fichiers originaux.
    
    Attributes:
        index (Dict): Mapping filename -> (cluster_id, offset, size)
    """
    
    def __init__(self):
        """Initialise l'index vide."""
        self.index: Dict[str, Tuple[int, int, int]] = {}
        self.cluster_files: Dict[int, List[str]] = {}
    
    def build_index(self, clusters: List[Cluster]) -> None:
        """
        Construit l'index à partir des clusters.
        
        Pour chaque fichier, stocke:
        - cluster_id: ID du cluster contenant le fichier
        - offset: Position du fichier dans le fichier fusionné (en bytes)
        - size: Taille du fichier (en bytes)
        
        Args:
            clusters (List[Cluster]): Liste des clusters
        """
        self.index.clear()
        self.cluster_files.clear()
        
        for cluster in clusters:
            offset = 0
            file_list = []
            
            for file in cluster.files:
                # Calculer la taille en bytes
                size_bytes = int(file.size_mb * 1024 * 1024)
                
                # Ajouter l'en-tête du fichier (pour la simulation)
                header = f"FILE: {file.name}\n".encode('utf-8')
                header_size = len(header)
                
                # Stocker dans l'index: (cluster_id, offset, taille_totale)
                self.index[file.name] = (cluster.cluster_id, offset, size_bytes + header_size)
                file_list.append(file.name)
                
                # Mettre à jour l'offset pour le prochain fichier
                offset += size_bytes + header_size
            
            self.cluster_files[cluster.cluster_id] = file_list
        
        print(f"\n✓ Index construit: {len(self.index)} fichiers indexés dans {len(self.cluster_files)} clusters")
    
    def get_file_location(self, filename: str) -> Optional[Tuple[int, int, int]]:
        """
        Obtient la localisation d'un fichier.
        
        Args:
            filename (str): Nom du fichier recherché
            
        Returns:
            Optional[Tuple[int, int, int]]: (cluster_id, offset, size) ou None
        """
        return self.index.get(filename)
    
    def extract_file(self, filename: str, merged_files_dir: str) -> Optional[bytes]:
        """
        Extrait le contenu d'un fichier depuis un cluster fusionné.
        
        Args:
            filename (str): Nom du fichier à extraire
            merged_files_dir (str): Répertoire contenant les fichiers fusionnés
            
        Returns:
            Optional[bytes]: Contenu du fichier ou None si non trouvé
        """
        location = self.get_file_location(filename)
        if location is None:
            print(f"✗ Fichier '{filename}' non trouvé dans l'index")
            return None
        
        cluster_id, offset, size = location
        merged_file_path = os.path.join(merged_files_dir, f"cluster_{cluster_id}.bin")
        
        if not os.path.exists(merged_file_path):
            print(f"✗ Fichier fusionné '{merged_file_path}' non trouvé")
            return None
        
        try:
            with open(merged_file_path, 'rb') as f:
                f.seek(offset)
                content = f.read(size)
            
            print(f"✓ Fichier '{filename}' extrait du cluster {cluster_id} (offset: {offset}, size: {size} bytes)")
            return content
        except Exception as e:
            print(f"✗ Erreur lors de l'extraction de '{filename}': {e}")
            return None
    
    def list_files_in_cluster(self, cluster_id: int) -> List[str]:
        """
        Liste tous les fichiers contenus dans un cluster.
        
        Args:
            cluster_id (int): ID du cluster
            
        Returns:
            List[str]: Liste des noms de fichiers
        """
        return self.cluster_files.get(cluster_id, [])
    
    def get_index_summary(self) -> dict:
        """
        Obtient un résumé de l'index.
        
        Returns:
            dict: Statistiques sur l'index
        """
        return {
            "total_files_indexed": len(self.index),
            "total_clusters": len(self.cluster_files),
            "files_per_cluster": {
                cluster_id: len(files) 
                for cluster_id, files in self.cluster_files.items()
            }
        }
    
    def print_index(self) -> None:
        """Affiche l'index complet."""
        print(f"\n{'='*70}")
        print(f"FILE INDEX - Mapping des fichiers vers clusters")
        print(f"{'='*70}")
        
        for cluster_id in sorted(self.cluster_files.keys()):
            files = self.cluster_files[cluster_id]
            print(f"\nCluster {cluster_id} ({len(files)} fichiers):")
            
            for filename in files:
                cluster_id, offset, size = self.index[filename]
                print(f"  - {filename:30s} | Offset: {offset:8d} bytes | Size: {size:8d} bytes")
        
        print(f"\n{'='*70}")
