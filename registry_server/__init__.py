"""
Lament Registry Server

A complete remote package registry server implementation for the Lament
programming language. Provides RESTful API for package management,
authentication, and statistics.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

__version__ = "1.0.0"
__author__ = "Zephyr, Rogue Linguist-AI"

from registry_server.server import RegistryServer, ServerConfig

__all__ = [
    "RegistryServer",
    "ServerConfig",
]
