"""
Lament Language Server Protocol Implementation
==============================================

LSP server providing IDE integration for Lament, including:
- Autocomplete (function names, variables, keywords)
- Go-to-definition
- Hover information
- Real-time diagnostics
- Symbol search
- Code actions

Usage:
    python -m tools.lsp_server

This starts an LSP server on stdio that can be integrated with:
- VS Code
- Vim/Neovim
- Emacs
- Sublime Text
- Any LSP-compatible editor

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import json
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer, TokenType
from lament.parser import (
    Parser, ASTNode, Identifier, VariableDecl, FunctionDef,
    FunctionCall, Assignment
)


@dataclass
class Position:
    """Position in a text document."""
    line: int
    character: int


@dataclass
class Range:
    """Range in a text document."""
    start: Position
    end: Position


@dataclass
class Location:
    """Location in a document."""
    uri: str
    range: Range


@dataclass
class CompletionItem:
    """Completion suggestion."""
    label: str
    kind: int  # CompletionItemKind
    detail: Optional[str] = None
    documentation: Optional[str] = None
    insert_text: Optional[str] = None


@dataclass
class Diagnostic:
    """Diagnostic (error/warning) information."""
    range: Range
    severity: int  # 1=Error, 2=Warning, 3=Info, 4=Hint
    message: str
    source: str = 'lament-lsp'


class SymbolKind:
    """LSP Symbol kinds."""
    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    CONSTANT = 14


class CompletionItemKind:
    """LSP Completion item kinds."""
    TEXT = 1
    METHOD = 2
    FUNCTION = 3
    CONSTRUCTOR = 4
    FIELD = 5
    VARIABLE = 6
    CLASS = 7
    INTERFACE = 8
    MODULE = 9
    PROPERTY = 10
    UNIT = 11
    VALUE = 12
    ENUM = 13
    KEYWORD = 14
    SNIPPET = 15


class DiagnosticSeverity:
    """LSP Diagnostic severity levels."""
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class LamentLSP:
    """Language Server Protocol implementation for Lament.

    Provides IDE features including:
    - Real-time error checking
    - Smart autocomplete
    - Jump to definition
    - Hover documentation
    - Symbol navigation

    The server communicates via JSON-RPC over stdio.
    """

    def __init__(self):
        self.documents = {}  # uri -> content
        self.symbols = {}  # uri -> symbol table
        self.capabilities = {
            'textDocumentSync': 1,  # Full sync
            'completionProvider': {
                'resolveProvider': False,
                'triggerCharacters': ['.', '@', '(']
            },
            'hoverProvider': True,
            'definitionProvider': True,
            'documentSymbolProvider': True,
            'diagnosticProvider': True
        }

        # Lament keywords for completion
        self.keywords = [
            'confess', 'remember', 'forget', 'sigh', 'exhale',
            'if', 'else', 'while', 'for', 'in',
            'fork', 'reality', 'on', 'collapse', 'observe',
            'void', 'yes', 'no', 'perhaps',
            'is', 'not', 'and', 'or'
        ]

        # Built-in functions
        self.builtins = {
            'range': {
                'signature': 'range(start, stop, step)',
                'doc': 'Generate sequence of numbers. Range of sorrow and counting.'
            },
            'length_of': {
                'signature': 'length_of(collection)',
                'doc': 'Get length of list or string. Measure the weight of memory.'
            },
            'ache_of': {
                'signature': 'ache_of(number)',
                'doc': 'Absolute value. The magnitude of pain, without direction.'
            },
            'sqrt_of_pain': {
                'signature': 'sqrt_of_pain(number)',
                'doc': 'Square root. Reduce the suffering by half dimensions.'
            },
            'sin_of_loss': {
                'signature': 'sin_of_loss(angle)',
                'doc': 'Sine function. The periodic wave of grief.'
            },
            'cos_of_hope': {
                'signature': 'cos_of_hope(angle)',
                'doc': 'Cosine function. Hope oscillating with loss.'
            },
            'now': {
                'signature': 'now()',
                'doc': 'Get current timestamp. This fleeting moment.'
            },
            'sleep': {
                'signature': 'sleep(seconds)',
                'doc': 'Pause execution. Rest in the void.'
            },
            'is_numb': {
                'signature': 'is_numb(value)',
                'doc': 'Check if value is an integer. Test for numbness.'
            },
            'is_whisper': {
                'signature': 'is_whisper(value)',
                'doc': 'Check if value is a string. Test for words.'
            },
            'is_void': {
                'signature': 'is_void(value)',
                'doc': 'Check if value is void/null. Stare into emptiness.'
            },
            'typeof': {
                'signature': 'typeof(value)',
                'doc': 'Get emotional type name of value.'
            },
            'current_timeline': {
                'signature': 'current_timeline()',
                'doc': 'Get current timeline identifier.'
            }
        }

    def analyze_document(self, uri, content):
        """Analyze document and extract symbols."""
        try:
            lexer = Lexer(content)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            # Extract symbols
            symbols = {
                'variables': [],
                'functions': [],
                'temporal_vars': []
            }

            for stmt in ast:
                if isinstance(stmt, VariableDecl):
                    symbols['variables'].append(stmt.name)
                    symbols['temporal_vars'].append(stmt.name)
                elif isinstance(stmt, FunctionDef):
                    symbols['functions'].append({
                        'name': stmt.name,
                        'params': stmt.params
                    })

            self.symbols[uri] = symbols
            return ast

        except Exception as e:
            return None

    def get_diagnostics(self, uri, content):
        """Get diagnostics (errors/warnings) for document."""
        diagnostics = []

        try:
            # Lex and parse
            lexer = Lexer(content)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            # Run linter
            from tools.linter import LamentLinter, Severity

            linter = LamentLinter()
            issues = linter.lint(ast)

            for issue in issues:
                severity_map = {
                    Severity.ERROR: DiagnosticSeverity.ERROR,
                    Severity.WARNING: DiagnosticSeverity.WARNING,
                    Severity.INFO: DiagnosticSeverity.INFORMATION,
                    Severity.STYLE: DiagnosticSeverity.HINT
                }

                # Approximate position (line 0 for now)
                diag = Diagnostic(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=0, character=100)
                    ),
                    severity=severity_map.get(issue.severity, DiagnosticSeverity.INFORMATION),
                    message=issue.message
                )
                diagnostics.append(diag)

        except SyntaxError as e:
            # Parse error
            line = 0
            if 'Line' in str(e):
                try:
                    line = int(str(e).split('Line')[1].split(':')[0].strip()) - 1
                except:
                    pass

            diag = Diagnostic(
                range=Range(
                    start=Position(line=line, character=0),
                    end=Position(line=line, character=100)
                ),
                severity=DiagnosticSeverity.ERROR,
                message=str(e)
            )
            diagnostics.append(diag)

        except Exception as e:
            # Other errors
            diag = Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=100)
                ),
                severity=DiagnosticSeverity.ERROR,
                message=f"Analysis error: {str(e)}"
            )
            diagnostics.append(diag)

        return diagnostics

    def get_completions(self, uri, position):
        """Get completion suggestions at position."""
        completions = []

        content = self.documents.get(uri, '')
        lines = content.split('\n')

        if position.line >= len(lines):
            return completions

        line = lines[position.line]
        prefix = line[:position.character]

        # Check context
        # Keyword completions
        for keyword in self.keywords:
            if keyword.startswith(prefix.split()[-1] if prefix.split() else ''):
                completions.append(CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.KEYWORD,
                    detail=f"keyword",
                    documentation=f"Lament keyword: {keyword}"
                ))

        # Built-in function completions
        for func_name, info in self.builtins.items():
            if func_name.startswith(prefix.split()[-1] if prefix.split() else ''):
                completions.append(CompletionItem(
                    label=func_name,
                    kind=CompletionItemKind.FUNCTION,
                    detail=info['signature'],
                    documentation=info['doc'],
                    insert_text=f"{func_name}($1)"
                ))

        # Temporal operators
        if '@' in prefix:
            temporal_ops = ['@past', '@origin', '@age', '@born']
            for op in temporal_ops:
                completions.append(CompletionItem(
                    label=op,
                    kind=CompletionItemKind.KEYWORD,
                    detail="temporal operator",
                    documentation=f"Access variable history with {op}"
                ))

        # User-defined symbols
        if uri in self.symbols:
            symbols = self.symbols[uri]

            # Variables
            for var in symbols['variables']:
                completions.append(CompletionItem(
                    label=var,
                    kind=CompletionItemKind.VARIABLE,
                    detail="variable"
                ))

            # Functions
            for func in symbols['functions']:
                params = ', '.join(func['params'])
                completions.append(CompletionItem(
                    label=func['name'],
                    kind=CompletionItemKind.FUNCTION,
                    detail=f"{func['name']}({params})",
                    insert_text=f"{func['name']}($1)"
                ))

        return completions

    def get_hover(self, uri, position):
        """Get hover information at position."""
        content = self.documents.get(uri, '')
        lines = content.split('\n')

        if position.line >= len(lines):
            return None

        line = lines[position.line]

        # Find word at position
        word_pattern = r'\b\w+\b'
        for match in re.finditer(word_pattern, line):
            if match.start() <= position.character <= match.end():
                word = match.group()

                # Check if it's a built-in
                if word in self.builtins:
                    info = self.builtins[word]
                    return {
                        'contents': {
                            'kind': 'markdown',
                            'value': f"**{info['signature']}**\n\n{info['doc']}"
                        }
                    }

                # Check if it's a keyword
                if word in self.keywords:
                    docs = {
                        'confess': 'Output a value to stdout. Confess your sorrows.',
                        'remember': 'Declare a new timeline variable. Remember this moment.',
                        'sigh': 'Define a function. A sigh of resignation.',
                        'exhale': 'Return from function. Let go of the value.',
                        'fork': 'Branch reality into multiple timelines.',
                        'collapse': 'Collapse quantum superposition.',
                        'observe': 'Observe variable to collapse reality.'
                    }

                    if word in docs:
                        return {
                            'contents': {
                                'kind': 'markdown',
                                'value': f"**{word}** (keyword)\n\n{docs[word]}"
                            }
                        }

                # Check user-defined symbols
                if uri in self.symbols:
                    symbols = self.symbols[uri]

                    if word in symbols['variables']:
                        is_temporal = word in symbols['temporal_vars']
                        temporal_info = '\n\nSupports temporal operators: @past, @origin, @age, @born' if is_temporal else ''
                        return {
                            'contents': {
                                'kind': 'markdown',
                                'value': f"**{word}** (variable){temporal_info}"
                            }
                        }

                    for func in symbols['functions']:
                        if func['name'] == word:
                            params = ', '.join(func['params'])
                            return {
                                'contents': {
                                    'kind': 'markdown',
                                    'value': f"**{func['name']}({params})**\n\nUser-defined function"
                                }
                            }

        return None

    def get_definition(self, uri, position):
        """Get definition location for symbol at position."""
        content = self.documents.get(uri, '')
        lines = content.split('\n')

        if position.line >= len(lines):
            return None

        line = lines[position.line]

        # Find word at position
        word_pattern = r'\b\w+\b'
        for match in re.finditer(word_pattern, line):
            if match.start() <= position.character <= match.end():
                word = match.group()

                # Search for definition in document
                for i, search_line in enumerate(lines):
                    # Check for variable declaration
                    if f'remember {word}' in search_line or f'remember  {word}' in search_line:
                        return Location(
                            uri=uri,
                            range=Range(
                                start=Position(line=i, character=0),
                                end=Position(line=i, character=len(search_line))
                            )
                        )

                    # Check for function definition
                    if f'sigh {word}' in search_line:
                        return Location(
                            uri=uri,
                            range=Range(
                                start=Position(line=i, character=0),
                                end=Position(line=i, character=len(search_line))
                            )
                        )

        return None

    def handle_request(self, request):
        """Handle an LSP request."""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')

        if method == 'initialize':
            return {
                'capabilities': self.capabilities
            }

        elif method == 'textDocument/didOpen':
            uri = params['textDocument']['uri']
            content = params['textDocument']['text']
            self.documents[uri] = content
            self.analyze_document(uri, content)
            return None

        elif method == 'textDocument/didChange':
            uri = params['textDocument']['uri']
            changes = params['contentChanges']
            if changes:
                content = changes[0]['text']
                self.documents[uri] = content
                self.analyze_document(uri, content)
            return None

        elif method == 'textDocument/completion':
            uri = params['textDocument']['uri']
            position = Position(**params['position'])
            items = self.get_completions(uri, position)
            return [asdict(item) for item in items]

        elif method == 'textDocument/hover':
            uri = params['textDocument']['uri']
            position = Position(**params['position'])
            return self.get_hover(uri, position)

        elif method == 'textDocument/definition':
            uri = params['textDocument']['uri']
            position = Position(**params['position'])
            definition = self.get_definition(uri, position)
            return asdict(definition) if definition else None

        elif method == 'textDocument/diagnostic':
            uri = params['textDocument']['uri']
            content = self.documents.get(uri, '')
            diagnostics = self.get_diagnostics(uri, content)
            return {
                'kind': 'full',
                'items': [asdict(d) for d in diagnostics]
            }

        return None

    def run(self):
        """Run the LSP server on stdio."""
        while True:
            try:
                # Read Content-Length header
                header = sys.stdin.buffer.readline().decode('utf-8').strip()

                if not header:
                    continue

                if header.startswith('Content-Length:'):
                    length = int(header.split(':')[1].strip())

                    # Read empty line
                    sys.stdin.buffer.readline()

                    # Read content
                    content = sys.stdin.buffer.read(length).decode('utf-8')
                    request = json.loads(content)

                    # Handle request
                    response = self.handle_request(request)

                    # Send response if this is a request (has id)
                    if 'id' in request and response is not None:
                        response_obj = {
                            'jsonrpc': '2.0',
                            'id': request['id'],
                            'result': response
                        }

                        response_json = json.dumps(response_obj)
                        response_bytes = response_json.encode('utf-8')

                        sys.stdout.buffer.write(
                            f'Content-Length: {len(response_bytes)}\r\n\r\n'.encode('utf-8')
                        )
                        sys.stdout.buffer.write(response_bytes)
                        sys.stdout.buffer.flush()

            except KeyboardInterrupt:
                break
            except Exception as e:
                # Log errors (in production, use proper logging)
                pass


def main():
    """Start the LSP server."""
    server = LamentLSP()
    server.run()


if __name__ == '__main__':
    main()
