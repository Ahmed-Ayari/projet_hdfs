"""
Classe représentant un petit fichier dans le système HDFS.
"""


class SmallFile:
    """
    Représente un fichier avec son nom et sa taille.
    
    Attributes:
        name (str): Le nom du fichier
        size_mb (float): La taille du fichier en mégaoctets (MB)
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
    
    def to_dict(self) -> dict:
        """
        Convertit le fichier en dictionnaire.
        
        Returns:
            dict: Dictionnaire contenant les informations du fichier
        """
        return {
            "name": self.name,
            "size_mb": round(self.size_mb, 2)
        }
