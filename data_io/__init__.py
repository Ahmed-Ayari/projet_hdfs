"""
Module data_io - Gestion des entrées/sorties (génération de fichiers, métadonnées).
"""

from .file_generator import FileGenerator
from .metadata_writer import MetadataWriter

__all__ = ['FileGenerator', 'MetadataWriter']
