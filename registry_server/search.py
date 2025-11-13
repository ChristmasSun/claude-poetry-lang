#!/usr/bin/env python3
"""
Search Engine for Lament Registry Server

Provides:
- Full-text search
- Tag-based search
- Dependency search
- Popularity ranking
- Search caching
- Elasticsearch integration (optional)

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import asyncio
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

# Try to import optional dependencies
try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False


# ============================================================================
# SEARCH ENGINE
# ============================================================================

class SearchEngine:
    """Main search engine for package registry."""

    def __init__(
        self,
        database_manager,
        elasticsearch_url: Optional[str] = None,
        cache_ttl: int = 300
    ):
        """
        Initialize search engine.

        Args:
            database_manager: Database manager instance
            elasticsearch_url: Optional Elasticsearch URL for advanced search
            cache_ttl: Cache time-to-live in seconds
        """
        self.db = database_manager
        self.cache_ttl = cache_ttl

        # Search cache
        self.search_cache: Dict[str, tuple] = {}  # query -> (timestamp, results)

        # Search index (in-memory for basic search)
        self.index: Dict[str, Set[str]] = defaultdict(set)  # term -> package names
        self.package_data: Dict[str, Dict[str, Any]] = {}  # package name -> data

        # Initialize Elasticsearch if available
        self.es_client = None
        if elasticsearch_url and ELASTICSEARCH_AVAILABLE:
            self.es_client = AsyncElasticsearch([elasticsearch_url])
            self.es_index_name = "lament-packages"

    async def initialize(self):
        """Initialize search engine."""
        if self.es_client:
            await self._init_elasticsearch()

        # Build initial index
        await self.rebuild_index()

    async def close(self):
        """Close search engine connections."""
        if self.es_client:
            await self.es_client.close()

    # ========================================================================
    # INDEXING
    # ========================================================================

    async def index_package(self, name: str, version: str, metadata: Any) -> None:
        """
        Index a package for search.

        Args:
            name: Package name
            version: Package version
            metadata: Package metadata
        """
        # Extract searchable fields
        description = metadata.description if hasattr(metadata, 'description') else metadata.get('description', '')
        author = metadata.author if hasattr(metadata, 'author') else metadata.get('author', '')
        keywords = metadata.keywords if hasattr(metadata, 'keywords') else metadata.get('keywords', [])

        # Store package data
        self.package_data[name] = {
            'name': name,
            'version': version,
            'description': description,
            'author': author,
            'keywords': keywords
        }

        # Index terms
        terms = self._extract_terms(name, description, author, keywords)
        for term in terms:
            self.index[term.lower()].add(name)

        # Index in Elasticsearch if available
        if self.es_client:
            await self._index_elasticsearch(name, version, metadata)

    async def remove_package(self, name: str, version: str) -> None:
        """
        Remove a package from search index.

        Args:
            name: Package name
            version: Package version
        """
        # Remove from in-memory index
        if name in self.package_data:
            del self.package_data[name]

        # Remove from term index
        for term_packages in self.index.values():
            term_packages.discard(name)

        # Remove from Elasticsearch
        if self.es_client:
            await self._remove_elasticsearch(name, version)

    async def rebuild_index(self) -> None:
        """Rebuild the entire search index from database."""
        # Clear existing index
        self.index.clear()
        self.package_data.clear()

        # Get all packages from database
        packages = await self.db.list_packages(limit=10000, offset=0)

        # Index each package
        for package in packages:
            await self.index_package(
                package['name'],
                package['version'],
                package
            )

    def _extract_terms(
        self,
        name: str,
        description: str,
        author: str,
        keywords: List[str]
    ) -> Set[str]:
        """Extract searchable terms from package metadata."""
        terms = set()

        # Add name (split on common separators)
        name_parts = re.split(r'[-_.]', name.lower())
        terms.update(name_parts)
        terms.add(name.lower())

        # Add description words
        if description:
            desc_words = re.findall(r'\w+', description.lower())
            terms.update(desc_words)

        # Add author
        if author:
            author_words = re.findall(r'\w+', author.lower())
            terms.update(author_words)

        # Add keywords
        for keyword in keywords:
            terms.add(keyword.lower())

        # Remove very short terms (less than 2 characters)
        terms = {t for t in terms if len(t) >= 2}

        return terms

    # ========================================================================
    # SEARCHING
    # ========================================================================

    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for packages.

        Args:
            query: Search query
            limit: Maximum results to return
            offset: Results offset for pagination
            filters: Optional filters (author, keywords, etc.)

        Returns:
            List of package search results
        """
        # Check cache first
        cache_key = f"{query}:{limit}:{offset}:{json.dumps(filters or {})}"
        if cache_key in self.search_cache:
            timestamp, results = self.search_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return results

        # Perform search
        if self.es_client:
            results = await self._search_elasticsearch(query, limit, offset, filters)
        else:
            results = await self._search_basic(query, limit, offset, filters)

        # Cache results
        self.search_cache[cache_key] = (datetime.now(), results)

        return results

    async def _search_basic(
        self,
        query: str,
        limit: int,
        offset: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Basic in-memory search."""
        query_terms = query.lower().split()
        matching_packages = set()

        # Find packages matching any query term
        for term in query_terms:
            # Exact matches
            if term in self.index:
                matching_packages.update(self.index[term])

            # Prefix matches
            for index_term in self.index:
                if index_term.startswith(term):
                    matching_packages.update(self.index[index_term])

        # Get package data and score
        results = []
        for package_name in matching_packages:
            if package_name not in self.package_data:
                continue

            package = self.package_data[package_name]

            # Apply filters
            if filters:
                if 'author' in filters and package['author'] != filters['author']:
                    continue
                if 'keywords' in filters:
                    filter_keywords = set(filters['keywords'])
                    package_keywords = set(package['keywords'])
                    if not filter_keywords.intersection(package_keywords):
                        continue

            # Calculate relevance score
            score = self._calculate_score(package, query_terms)

            # Get download count from database
            db_package = await self.db.get_package_version_info(
                package_name,
                package['version']
            )

            results.append({
                'name': package_name,
                'version': package['version'],
                'description': package['description'],
                'author': package['author'],
                'downloads': db_package['downloads'] if db_package else 0,
                'published_at': db_package['published_at'] if db_package else '',
                'score': score
            })

        # Sort by score (descending) then by downloads
        results.sort(key=lambda x: (x['score'], x['downloads']), reverse=True)

        # Apply pagination
        return results[offset:offset + limit]

    def _calculate_score(self, package: Dict[str, Any], query_terms: List[str]) -> float:
        """Calculate relevance score for a package."""
        score = 0.0

        name_lower = package['name'].lower()
        desc_lower = package['description'].lower()

        for term in query_terms:
            # Exact name match
            if term == name_lower:
                score += 10.0

            # Name contains term
            if term in name_lower:
                score += 5.0

            # Description contains term
            if term in desc_lower:
                score += 1.0

            # Keyword match
            if term in [k.lower() for k in package['keywords']]:
                score += 3.0

        return score

    # ========================================================================
    # ELASTICSEARCH INTEGRATION
    # ========================================================================

    async def _init_elasticsearch(self):
        """Initialize Elasticsearch index."""
        if not self.es_client:
            return

        # Create index if it doesn't exist
        exists = await self.es_client.indices.exists(index=self.es_index_name)
        if not exists:
            await self.es_client.indices.create(
                index=self.es_index_name,
                body={
                    'mappings': {
                        'properties': {
                            'name': {'type': 'text', 'boost': 3.0},
                            'version': {'type': 'keyword'},
                            'description': {'type': 'text'},
                            'author': {'type': 'text'},
                            'keywords': {'type': 'keyword'},
                            'dependencies': {'type': 'keyword'},
                            'downloads': {'type': 'integer'},
                            'published_at': {'type': 'date'}
                        }
                    }
                }
            )

    async def _index_elasticsearch(self, name: str, version: str, metadata: Any):
        """Index a package in Elasticsearch."""
        if not self.es_client:
            return

        doc = {
            'name': name,
            'version': version,
            'description': metadata.description if hasattr(metadata, 'description') else metadata.get('description', ''),
            'author': metadata.author if hasattr(metadata, 'author') else metadata.get('author', ''),
            'keywords': metadata.keywords if hasattr(metadata, 'keywords') else metadata.get('keywords', []),
            'dependencies': [d.get('name', '') for d in (metadata.dependencies if hasattr(metadata, 'dependencies') else metadata.get('dependencies', []))],
            'downloads': 0,
            'published_at': datetime.now().isoformat()
        }

        await self.es_client.index(
            index=self.es_index_name,
            id=f"{name}:{version}",
            body=doc
        )

    async def _remove_elasticsearch(self, name: str, version: str):
        """Remove a package from Elasticsearch."""
        if not self.es_client:
            return

        try:
            await self.es_client.delete(
                index=self.es_index_name,
                id=f"{name}:{version}"
            )
        except Exception:
            pass

    async def _search_elasticsearch(
        self,
        query: str,
        limit: int,
        offset: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search using Elasticsearch."""
        if not self.es_client:
            return []

        # Build query
        es_query = {
            'query': {
                'bool': {
                    'should': [
                        {'match': {'name': {'query': query, 'boost': 3.0}}},
                        {'match': {'description': {'query': query, 'boost': 1.0}}},
                        {'match': {'author': {'query': query, 'boost': 1.5}}},
                        {'term': {'keywords': {'value': query, 'boost': 2.0}}}
                    ],
                    'minimum_should_match': 1
                }
            },
            'sort': [
                {'_score': {'order': 'desc'}},
                {'downloads': {'order': 'desc'}}
            ],
            'from': offset,
            'size': limit
        }

        # Add filters
        if filters:
            must_clauses = []

            if 'author' in filters:
                must_clauses.append({'term': {'author': filters['author']}})

            if 'keywords' in filters:
                for keyword in filters['keywords']:
                    must_clauses.append({'term': {'keywords': keyword}})

            if must_clauses:
                es_query['query']['bool']['must'] = must_clauses

        # Execute search
        response = await self.es_client.search(
            index=self.es_index_name,
            body=es_query
        )

        # Format results
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            results.append({
                'name': source['name'],
                'version': source['version'],
                'description': source['description'],
                'author': source['author'],
                'downloads': source['downloads'],
                'published_at': source['published_at'],
                'score': hit['_score']
            })

        return results

    # ========================================================================
    # ADVANCED SEARCH
    # ========================================================================

    async def search_by_author(self, author: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search packages by author."""
        return await self.search("", limit=limit, filters={'author': author})

    async def search_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search packages by keyword."""
        return await self.search("", limit=limit, filters={'keywords': [keyword]})

    async def search_by_dependency(self, dependency: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search packages that depend on a specific package.

        Args:
            dependency: Dependency package name
            limit: Maximum results

        Returns:
            List of packages that depend on the specified package
        """
        # Query database for packages with this dependency
        all_packages = await self.db.list_packages(limit=1000, offset=0)

        results = []
        for package in all_packages:
            dependencies = package.get('dependencies', [])
            dep_names = [d.get('name', '') for d in dependencies]

            if dependency in dep_names:
                results.append({
                    'name': package['name'],
                    'version': package['version'],
                    'description': package['description'],
                    'author': package['author'],
                    'downloads': package['downloads'],
                    'published_at': package['published_at']
                })

        # Sort by downloads
        results.sort(key=lambda x: x['downloads'], reverse=True)

        return results[:limit]

    async def get_popular_packages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular packages by download count."""
        packages = await self.db.list_packages(limit=limit, offset=0)

        return [{
            'name': p['name'],
            'version': p['version'],
            'description': p['description'],
            'author': p['author'],
            'downloads': p['downloads'],
            'published_at': p['published_at']
        } for p in packages]

    async def get_trending_packages(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get trending packages based on recent downloads.

        Args:
            days: Number of days to consider
            limit: Maximum results

        Returns:
            List of trending packages
        """
        # This would require time-series download data
        # For now, just return popular packages
        return await self.get_popular_packages(limit)

    async def suggest_packages(self, query: str, limit: int = 5) -> List[str]:
        """
        Get package name suggestions for autocomplete.

        Args:
            query: Partial package name
            limit: Maximum suggestions

        Returns:
            List of suggested package names
        """
        query_lower = query.lower()
        suggestions = []

        for package_name in self.package_data:
            if package_name.lower().startswith(query_lower):
                suggestions.append(package_name)

        # Sort by popularity (would need download counts)
        suggestions.sort()

        return suggestions[:limit]

    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================

    async def clear_cache(self):
        """Clear search cache."""
        self.search_cache.clear()

    async def cleanup_cache(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = []

        for key, (timestamp, _) in self.search_cache.items():
            if (now - timestamp).total_seconds() >= self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.search_cache[key]

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.search_cache)
        now = datetime.now()

        expired_entries = sum(
            1 for timestamp, _ in self.search_cache.values()
            if (now - timestamp).total_seconds() >= self.cache_ttl
        )

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'cache_ttl': self.cache_ttl
        }
