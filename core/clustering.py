"""
Implémentation de l'algorithme de fusion de petits fichiers HDFS.

Algorithme utilisé: Clustering Hiérarchique Agglomératif avec Single-Linkage
Distance utilisée: Distance Euclidienne basée sur la taille des fichiers
Contrainte: Taille maximale d'un cluster ≤ taille de bloc HDFS (128 MB)
"""

from typing import List
from models.small_file import SmallFile, SMALL_FILE_THRESHOLD, SMALL_FILE_MAX_SIZE_MB
from models.cluster import Cluster
from .distance_matrix import DistanceMatrix
from .dendrogram import Dendrogram


class AgglomerativeClustering:
    """
    Implémentation de l'Algorithm 1 de l'article: "Small Files Merging Algorithm".
    
    Selon l'article (Section 3 - Background Theory):
    - "Agglomerative hierarchical clustering is a clustering algorithm that builds 
      a cluster hierarchy from the bottom-up"
    - "It starts by adding a cluster for each of the data points to be clustered, 
      followed by iterative pair-wise merging of clusters"
    - "The choice of clusters to merge at each iteration is based on a distance metric"
    - "Single-linkage clustering is the minimum distance between elements of each cluster"
    
    Attributes:
        max_cluster_size_mb (float): Taille de bloc HDFS (128 MB par défaut)
        clusters (List[Cluster]): Liste des clusters C = {C1, C2, ..., Cm}
        distance_matrix (DistanceMatrix): Matrice De(Fi, Fj) entre clusters
        dendrogram (Dendrogram): Représentation arborescente des fusions
    """
    
    def __init__(self, max_cluster_size_mb: float = 128.0):
        """
        Initialise l'algorithme de clustering.
        
        Selon l'article (Section 4): "The size of cluster should less than or 
        equal to default block size" (128 MB).
        
        Args:
            max_cluster_size_mb (float): Taille maximale d'un cluster (défaut: 128 MB)
        """
        self.max_cluster_size_mb = max_cluster_size_mb
        self.clusters = []
        self.distance_matrix = None
        self._iteration_count = 0
        # Dendrogramme: "The dendrogram is a multilevel hierarchy where clusters 
        # at one level are joined together to form the clusters at the next levels"
        self.dendrogram = Dendrogram()
        # Historique des étapes de l'Algorithm 1 (lignes 1-15)
        self._algorithm_steps = []
    
    def fit(self, files: List[SmallFile]) -> List[Cluster]:
        """
        Exécute l'Algorithm 1 (Small Files Merging Algorithm) sur les fichiers.
        
        Selon l'article (Section 4.1 - Algorithm 1):
        - Input: Small files S = {F1, F2, F3, ..., Fn}
        - Output: Cluster hierarchies C = {C1, C2, ..., Cm}
        
        Étapes principales:
        1. [Lignes 1-5] Calcul de la matrice de distance euclidienne De(Fi, Fj)
        2. [Ligne 6] Création de la matrice de distance
        3. [Ligne 7] Initialisation: C = {{F} | F ∈ S} (chaque fichier = 1 cluster)
        4. [Lignes 8-14] Boucle de fusion itérative avec contrainte de taille
        5. [Ligne 15] Retourne C (clusters finaux)
        
        Args:
            files (List[SmallFile]): Liste des fichiers S = {F1, F2, ..., Fn}
            
        Returns:
            List[Cluster]: Liste des clusters C = {C1, C2, ..., Cm}
        """
        print(f"\n{'='*60}")
        print(f"DÉMARRAGE DU CLUSTERING HIÉRARCHIQUE AGGLOMÉRATIF")
        print(f"{'='*60}")
        print(f"Configuration HDFS (selon article):")
        print(f"  - Taille de bloc: {self.max_cluster_size_mb} MB")
        print(f"  - Seuil petits fichiers: {SMALL_FILE_THRESHOLD*100:.0f}% = {SMALL_FILE_MAX_SIZE_MB:.1f} MB")
        print(f"  - Taille max cluster: {self.max_cluster_size_mb} MB")
        print(f"\nFichiers analysés:")
        print(f"  - Total reçu: {len(files)}")
        small_file_count = sum(1 for f in files if f.size_mb < SMALL_FILE_MAX_SIZE_MB)
        large_file_count = len(files) - small_file_count
        print(f"  - Petits fichiers (< {SMALL_FILE_MAX_SIZE_MB:.1f} MB): {small_file_count}")
        print(f"  - Fichiers exclus (>= {SMALL_FILE_MAX_SIZE_MB:.1f} MB): {large_file_count}")
        print(f"  - Méthode de linkage: SINGLE-LINKAGE")
        
        # [ALGORITHM 1 - Ligne 7] Initialisation: C = {{F} | F ∈ S}
        # Chaque fichier devient un cluster initial
        self._initialize_clusters(files)
        
        # [ALGORITHM 1 - Lignes 1-6] Création de la matrice de distance euclidienne
        # Selon l'article: "The Euclidean distance measure is used to cluster the small files"
        # Formule: d(i,j) = |size_i - size_j| (distance basée sur la taille)
        self.distance_matrix = DistanceMatrix(self.clusters)
        self._algorithm_steps.append("[Lignes 1-6] Matrice de distance euclidienne calculée")
        
        print(f"\nInitialisation terminée: {len(self.clusters)} clusters créés")
        print("\n[ALGORITHM 1 - Lignes 1-6] Calcul de la matrice de distance euclidienne...\n")
        
        # [ALGORITHM 1 - Lignes 8-14] Boucle de fusion itérative
        # "While sizeOfEachCluster |C| < 128MB Do"
        print("[ALGORITHM 1 - Lignes 8-14] Début du processus de fusion itératif...\n")
        self._algorithm_steps.append("[Ligne 7] Initialisation: C = {{F} | F ∈ S}")
        self._agglomerate()
        
        print(f"\n{'='*60}")
        print(f"CLUSTERING TERMINÉ")
        print(f"{'='*60}")
        print(f"Nombre de clusters finaux: {len(self.clusters)}")
        print(f"Nombre d'itérations: {self._iteration_count}")
        
        # Construire le dendrogramme et l'afficher
        self.dendrogram.build_from_clusters(self.clusters)
        
        return self.clusters
    
    def _initialize_clusters(self, files: List[SmallFile]) -> None:
        """
        [ALGORITHM 1 - Ligne 7] Initialise les clusters.
        
        Selon l'article: "C = {{F} | F ∈ S} // initial each file cluster"
        Chaque fichier Fi devient un cluster Ci contenant un seul fichier.
        
        Args:
            files (List[SmallFile]): Liste des fichiers S = {F1, F2, ..., Fn}
        """
        # Réinitialiser le compteur d'IDs pour cohérence
        Cluster.reset_counter()
        
        # C = {{F} | F ∈ S} - chaque fichier devient son propre cluster
        self.clusters = []
        for file in files:
            cluster = Cluster([file])
            self.clusters.append(cluster)
    
    def _agglomerate(self) -> None:
        """
        [ALGORITHM 1 - Lignes 8-14] Boucle principale de fusion agglomérative.
        
        Selon l'article:
        - [Ligne 8] "While sizeOfEachCluster |C| < 128MB Do"
        - [Ligne 9] "{C, C'} = min De(Fi, Fj)" (sélection par single-linkage)
        - [Ligne 10] "If (sizeOfCluster |C| + sizeOfCluster |C'|) <= 128MB Then"
        - [Ligne 11] "C = ({C} ∪ {C'})" (fusion des clusters)
        - [Ligne 13] "Update distance matrix (C, S, De)"
        
        La fusion continue tant que des paires peuvent être fusionnées
        sans dépasser la taille maximale de bloc HDFS (128 MB).
        """
        while len(self.distance_matrix) > 1:
            # Obtenir toutes les paires triées par distance
            all_pairs = self.distance_matrix.get_all_pairs_sorted()
            
            if not all_pairs:
                break
            
            # Chercher la première paire fusionnable
            merged_something = False
            
            for i, j, distance in all_pairs:
                cluster_i = self.distance_matrix.clusters[i]
                cluster_j = self.distance_matrix.clusters[j]
                
                # [Ligne 9] Sélection single-linkage: min De(Fi, Fj)
                # "The single-linkage clustering is the minimum distance between elements"
                print(f"[Ligne 9] Single-linkage: min distance = {distance:.2f} MB")
                
                # [Ligne 10] Vérification contrainte: |C| + |C'| <= 128MB
                total_size = cluster_i.get_total_size() + cluster_j.get_total_size()
                print(f"[Ligne 10] Contrainte: {cluster_i.get_total_size():.2f} + {cluster_j.get_total_size():.2f} = {total_size:.2f} MB <= {self.max_cluster_size_mb} MB")
                
                if cluster_i.can_merge_with(cluster_j, self.max_cluster_size_mb):
                    self._iteration_count += 1
                    
                    print(f"Fusion: Cluster {cluster_i.cluster_id} ({cluster_i.get_total_size():.2f} MB) + Cluster {cluster_j.cluster_id} ({cluster_j.get_total_size():.2f} MB)")
                    print(f"Distance euclidienne: {distance:.2f} MB")
                    
                    # [Ligne 11] C = ({C} ∪ {C'}) - Fusion des deux clusters
                    print(f"[Ligne 11] Fusion: C = (C{cluster_i.cluster_id} ∪ C{cluster_j.cluster_id})")
                    self.distance_matrix.merge_clusters(i, j)
                    
                    merged = self.distance_matrix.clusters[-1]
                    print(f"-> Nouveau cluster C{merged.cluster_id} créé ({merged.get_total_size():.2f} MB, {len(merged.files)} fichiers)")
                    
                    # Enregistrement dans le dendrogramme (structure hiérarchique)
                    self.dendrogram.record_merge(cluster_i.cluster_id, cluster_j.cluster_id, merged.cluster_id, distance)
                    
                    # [Ligne 13] Mise à jour de la matrice de distance
                    print(f"[Ligne 13] Mise à jour matrice de distance")
                    print(f"Clusters restants: {len(self.distance_matrix)}")
                    
                    # Enregistrer l'étape dans l'historique
                    self._algorithm_steps.append(f"Itération {self._iteration_count}: C{cluster_i.cluster_id} ∪ C{cluster_j.cluster_id} -> C{merged.cluster_id}")
                    
                    merged_something = True
                    break  # Sortir de la boucle for et recalculer les paires
            
            # Si aucune fusion n'a été effectuée, arrêter
            if not merged_something:
                print("\nAucune fusion supplémentaire possible avec la contrainte de taille.")
                break
        
        # [Ligne 15] Return(C) - Retourner les clusters finaux
        self.clusters = self.distance_matrix.clusters
        self._algorithm_steps.append(f"[Ligne 15] Return(C) avec {len(self.clusters)} clusters")
    
    def _all_pairs_checked(self, unfusable_pairs: set) -> bool:
        """
        Vérifie si toutes les paires de clusters ont été testées.
        
        Utilisé pour déterminer la condition d'arrêt de la boucle de fusion
        lorsque plus aucune paire ne peut être fusionnée sans violer
        la contrainte de taille (|C| + |C'| > 128 MB).
        
        Args:
            unfusable_pairs (set): Ensemble des paires (Ci, Cj) non fusionnables
            
        Returns:
            bool: True si toutes les paires ont été vérifiées
        """
        n = len(self.distance_matrix)
        total_pairs = n * (n - 1) // 2
        return len(unfusable_pairs) >= total_pairs
    
    def get_clusters(self) -> List[Cluster]:
        """
        Retourne la liste des clusters finaux C = {C1, C2, ..., Cm}.
        
        Correspond à l'Output de l'Algorithm 1: "Cluster hierarchies C".
        
        Returns:
            List[Cluster]: Liste des clusters fusionnés
        """
        return self.clusters
    
    def get_statistics(self) -> dict:
        """
        Retourne des statistiques sur le clustering pour évaluation.
        
        Selon l'article (Section 5 - Evaluation):
        - Nombre de clusters créés vs fichiers originaux
        - Réduction de la consommation mémoire du NameNode
        - Taille moyenne des clusters (doit être proche de 128 MB)
        
        Returns:
            dict: Statistiques incluant num_clusters, tailles, itérations
        """
        if not self.clusters:
            return {}
        
        sizes = [c.get_total_size() for c in self.clusters]
        file_counts = [len(c) for c in self.clusters]
        
        return {
            "num_clusters": len(self.clusters),
            "total_files": sum(file_counts),
            "avg_cluster_size_mb": sum(sizes) / len(sizes),
            "min_cluster_size_mb": min(sizes),
            "max_cluster_size_mb": max(sizes),
            "avg_files_per_cluster": sum(file_counts) / len(file_counts),
            "iterations": self._iteration_count
        }
    
    def print_algorithm_steps(self) -> None:
        """
        Affiche le journal d'exécution de l'Algorithm 1.
        
        Permet de tracer l'exécution complète de l'algorithme de fusion
        tel que décrit dans la Section 4.1 de l'article:
        "Algorithm 1: Small Files Merging Algorithm"
        
        Affiche chaque étape (lignes 1-15) avec les clusters fusionnés.
        """
        print(f"\n{'='*70}")
        print(f"JOURNAL D'EXÉCUTION - Algorithm 1: Small Files Merging")
        print(f"{'='*70}")
        for step in self._algorithm_steps:
            print(f"  {step}")
        print(f"{'='*70}")
