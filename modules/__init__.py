"""
Modules Package
Contains modular components for CRUD operations in the Library Management System.

This package includes the following modules:
- add_recs: Handles adding new records (books, users, loans)
- view_recs: Handles viewing and retrieving records
- update_recs: Handles updating existing records
- delete_recs: Handles deleting records
- search_recs: Handles searching and filtering records
"""

from .add_recs import AddRecordsModule
from .view_recs import ViewRecordsModule
from .update_recs import UpdateRecordsModule
from .delete_recs import DeleteRecordsModule
from .search_recs import SearchRecordsModule

__all__ = [
    'AddRecordsModule',
    'ViewRecordsModule',
    'UpdateRecordsModule',
    'DeleteRecordsModule',
    'SearchRecordsModule'
]

__version__ = '1.0.0'
__author__ = 'Library Management System Team'