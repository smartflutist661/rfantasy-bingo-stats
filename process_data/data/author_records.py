"""
Created on Apr 7, 2023

@author: fred
"""
from collections import defaultdict

from ..types.author_info import AuthorInfo
from ..types.defined_types import Author

AUTHOR_INFO: defaultdict[Author, AuthorInfo] = defaultdict(AuthorInfo)
