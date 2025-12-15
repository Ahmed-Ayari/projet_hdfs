"""
Construction et visualisation du dendrogramme (arbre hiérarchique de fusion).

Selon l'article (Section 3 - Background Theory):
- "The result of hierarchical clustering is a tree-representation of the objects, 
   which is also known as dendrogram"
- "The dendrogram is a multilevel hierarchy where clusters at one level are 
   joined together to form the clusters at the next levels"
- "This makes it possible to decide the level at which to cut the tree for 
   generating suitable groups of a data objects"

Exemple de l'article (Figure 2 - Section 4.2):
- F1-F3 forment Cluster 1 (90 MB)
- F2-F4-F6-F5 forment Cluster 2 (120 MB)
"""

from typing import List, Optional, Tuple
from models.cluster import Cluster
from models.small_file import SmallFile


class MergeNode:
    """
    Représente un noeud dans l'arbre de fusion (dendrogramme).
    
    Attributes:
        cluster_id (int): ID du cluster
        files (List[SmallFile]): Fichiers dans ce noeud
        left (Optional[MergeNode]): Enfant gauche (cluster fusionné)
        right (Optional[MergeNode]): Enfant droit (cluster fusionné)
        merge_distance (float): Distance lors de la fusion
        total_size (float): Taille totale du cluster
    """
    
    def __init__(self, cluster_id: int, files: List[SmallFile], 
                 merge_distance: float = 0.0):
        """
        Initialise un noeud de fusion.
        
        Args:
            cluster_id (int): ID du cluster
            files (List[SmallFile]): Fichiers contenus
            merge_distance (float): Distance de fusion
        """
        self.cluster_id = cluster_id
        self.files = files
        self.left: Optional[MergeNode] = None
        self.right: Optional[MergeNode] = None
        self.merge_distance = merge_distance
        self.total_size = sum(f.size_mb for f in files)
        self.is_leaf = True
    
    def merge(self, other: 'MergeNode', new_id: int, distance: float) -> 'MergeNode':
        """
        Fusionne ce noeud avec un autre.
        
        Args:
            other (MergeNode): Autre noeud à fusionner
            new_id (int): ID du nouveau cluster
            distance (float): Distance de fusion
            
        Returns:
            MergeNode: Nouveau noeud fusionné
        """
        merged = MergeNode(new_id, self.files + other.files, distance)
        merged.left = self
        merged.right = other
        merged.is_leaf = False
        return merged
    
    def get_height(self) -> int:
        """Calcule la hauteur de l'arbre."""
        if self.is_leaf:
            return 1
        left_height = self.left.get_height() if self.left else 0
        right_height = self.right.get_height() if self.right else 0
        return 1 + max(left_height, right_height)
    
    def get_leaf_names(self) -> List[str]:
        """Obtient les noms de tous les fichiers feuilles."""
        if self.is_leaf:
            return [f.name for f in self.files]
        names = []
        if self.left:
            names.extend(self.left.get_leaf_names())
        if self.right:
            names.extend(self.right.get_leaf_names())
        return names


class Dendrogram:
    """
    Construit et visualise le dendrogramme des fusions hiérarchiques.
    
    Selon l'article (Section 3):
    "The dendrogram is a multilevel hierarchy where clusters at one level 
    are joined together to form the clusters at the next levels"
    
    Structure arborescente:
    - Feuilles: Fichiers individuels F1, F2, ..., Fn
    - Noeuds internes: Clusters fusionnés C1, C2, ..., Cm
    - Racines: Clusters finaux (taille ≤ 128 MB chacun)
    
    Attributes:
        roots (List[MergeNode]): Racines de l'arbre (clusters finaux)
        merge_history (List[Tuple]): Historique des fusions (Ci, Cj, C', distance)
    """
    
    def __init__(self):
        """Initialise le dendrogramme vide."""
        self.roots: List[MergeNode] = []
        self.merge_history: List[Tuple[int, int, int, float]] = []
    
    def record_merge(self, cluster_i_id: int, cluster_j_id: int, 
                    new_cluster_id: int, distance: float) -> None:
        """
        Enregistre une opération de fusion.
        
        Args:
            cluster_i_id (int): ID du premier cluster
            cluster_j_id (int): ID du second cluster
            new_cluster_id (int): ID du cluster résultant
            distance (float): Distance de fusion
        """
        self.merge_history.append((cluster_i_id, cluster_j_id, new_cluster_id, distance))
    
    def build_from_clusters(self, final_clusters: List[Cluster]) -> None:
        """
        Construit le dendrogramme à partir des clusters finaux.
        
        Args:
            final_clusters (List[Cluster]): Clusters finaux après fusion
        """
        self.roots = [
            MergeNode(cluster.cluster_id, cluster.files, 0.0)
            for cluster in final_clusters
        ]
    
    def print_tree(self, node: Optional[MergeNode] = None, 
                   prefix: str = "", is_last: bool = True) -> None:
        """
        Affiche l'arbre hiérarchique en format texte.
        
        Args:
            node (Optional[MergeNode]): Nœud à afficher
            prefix (str): Préfixe pour l'indentation
            is_last (bool): Si c'est le dernier enfant
        """
        if node is None:
            # Afficher tous les arbres
            print(f"\n{'='*70}")
            print(f"DENDROGRAM - Structure Hiérarchique (selon article)")
            print(f"{'='*70}\n")
            
            for i, root in enumerate(self.roots):
                print(f"Arbre {i+1} (Cluster {root.cluster_id}):")
                self.print_tree(root, "", True)
                print()
            return
        
        # Afficher le nœud actuel
        connector = "└── " if is_last else "├── "
        
        if node.is_leaf:
            files_str = ", ".join([f.name for f in node.files[:3]])
            if len(node.files) > 3:
                files_str += f"... (+{len(node.files)-3})"
            print(f"{prefix}{connector}Cluster {node.cluster_id} "
                  f"({node.total_size:.1f}MB) [{files_str}]")
        else:
            print(f"{prefix}{connector}Cluster {node.cluster_id} "
                  f"({node.total_size:.1f}MB) [distance={node.merge_distance:.1f}]")
            
            # Afficher les enfants
            new_prefix = prefix + ("    " if is_last else "│   ")
            if node.left:
                self.print_tree(node.left, new_prefix, False)
            if node.right:
                self.print_tree(node.right, new_prefix, True)
    
    def print_merge_history(self) -> None:
        """Affiche l'historique des fusions."""
        print(f"\n{'='*70}")
        print(f"HISTORIQUE DES FUSIONS")
        print(f"{'='*70}\n")
        
        if not self.merge_history:
            print("Aucune fusion enregistrée")
            return
        
        for i, (c1, c2, new_c, dist) in enumerate(self.merge_history, 1):
            print(f"Fusion {i}: Cluster {c1} + Cluster {c2} → "
                  f"Cluster {new_c} (distance: {dist:.2f})")
        
        print(f"\n{'='*70}")
    
    def get_statistics(self) -> dict:
        """
        Obtient les statistiques du dendrogramme.
        
        Returns:
            dict: Statistiques sur la structure
        """
        if not self.roots:
            return {"total_trees": 0, "total_merges": 0}
        
        return {
            "total_trees": len(self.roots),
            "total_merges": len(self.merge_history),
            "max_height": max(root.get_height() for root in self.roots),
            "total_leaves": sum(len(root.get_leaf_names()) for root in self.roots)
        }
