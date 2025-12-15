"""
Modèle représentant un petit fichier dans le système HDFS.

Selon l'article (Section 1 - Introduction):
- "A small file is a file whose size is less than the HDFS block size"
- "The default threshold for this system is set to (0.75) 75% of default block size (128 MB)"
- "Each file requires 150 bytes of memory space to store metadata in NameNode"

Configuration HDFS utilisée:
- Taille de bloc: 128 MB (standard HDFS)
- Seuil petits fichiers: 75% = 96 MB
- Fichiers < 96 MB → considérés comme "petits fichiers"
- Fichiers ≥ 96 MB → traités directement par HDFS
"""

# Configuration HDFS selon l'article (Section 4):
# "The small file is a file, whose size is less than 75% of default block size (128MB)"
HDFS_BLOCK_SIZE_MB = 128.0  # Taille de bloc HDFS standard
SMALL_FILE_THRESHOLD = 0.75  # Seuil: 75% de la taille de bloc
SMALL_FILE_MAX_SIZE_MB = HDFS_BLOCK_SIZE_MB * SMALL_FILE_THRESHOLD  # 96 MB


class SmallFile:
    """
    Représente un fichier Fi dans l'ensemble S = {F1, F2, ..., Fn}.
    
    Selon l'article (Section 4 - Algorithm 1):
    - Input: "Small files S = {F1, F2, F3, ..., Fn}"
    - Chaque fichier a un nom et une taille en MB
    - La taille est utilisée pour calculer la distance euclidienne
    
    Attributes:
        name (str): Nom du fichier (ex: "doc1.txt")
        size_mb (float): Taille du fichier en mégaoctets (MB)
    """
    
    def __init__(self, name: str, size_mb: float):
        """
        Initialise un objet SmallFile.
        
        Args:
            name (str): Le nom du fichier
            size_mb (float): La taille du fichier en MB
            
        Raises:
            ValueError: Si la taille est négative ou nulle
        """
        if size_mb <= 0:
            raise ValueError(f"La taille du fichier doit être positive: {size_mb}")
        
        self.name = name
        self.size_mb = size_mb
    
    def __repr__(self) -> str:
        """
        Représentation textuelle du fichier.
        
        Returns:
            str: Une chaîne décrivant le fichier
        """
        return f"SmallFile(name='{self.name}', size_mb={self.size_mb:.2f})"
    
    def __str__(self) -> str:
        """
        Conversion en chaîne pour l'affichage.
        
        Returns:
            str: Le nom et la taille du fichier
        """
        return f"{self.name} ({self.size_mb:.2f} MB)"
    
    def is_eligible_for_merging(self) -> bool:
        """
        Vérifie si le fichier est éligible pour la fusion (< 75% de la taille de bloc).
        Selon l'article: "If the file is a small file, the system will put it 
        in the hierarchical structure according to the proposed algorithm."
        
        Returns:
            bool: True si le fichier est un "petit fichier" (< 96 MB)
        """
        return self.size_mb < SMALL_FILE_MAX_SIZE_MB
    
    def to_dict(self) -> dict:
        """
        Convertit le fichier en dictionnaire.
        
        Returns:
            dict: Dictionnaire contenant les informations du fichier
        """
        return {
            "name": self.name,
            "size_mb": round(self.size_mb, 2),
            "is_small_file": self.is_eligible_for_merging()
        }
    
    @staticmethod
    def is_small_file(size_mb: float) -> bool:
        """
        Vérifie si une taille donnée correspond à un petit fichier.
        Selon l'article: "The default threshold for this system is set to 
        (0.75) 75% of default block size (128 MB)."
        
        Args:
            size_mb (float): Taille du fichier en MB
            
        Returns:
            bool: True si la taille < 96 MB (75% de 128 MB)
        """
        return size_mb < SMALL_FILE_MAX_SIZE_MB
    
    @staticmethod
    def get_threshold_info() -> dict:
        """
        Retourne les informations sur le seuil HDFS.
        
        Returns:
            dict: Configuration du seuil
        """
        return {
            "hdfs_block_size_mb": HDFS_BLOCK_SIZE_MB,
            "threshold": SMALL_FILE_THRESHOLD,
            "small_file_max_size_mb": SMALL_FILE_MAX_SIZE_MB
        }
