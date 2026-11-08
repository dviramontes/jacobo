"""Definition-only LSP for jank, using clj-kondo's Clojure analysis."""
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlparse

CONFIG = '{:output {:format :json :analysis {:locals true}}}'
SKIP = {'.git', '.jank', '.clj-kondo', '.lsp', 'target', 'node_modules', '.venv'}


def path_from_uri(uri):
    parsed = urlparse(uri)
    if parsed.scheme != 'file' or parsed.netloc not in ('', 'localhost'):
        raise ValueError('Only local file URIs are supported')
    return Path(unquote(parsed.path)).resolve()


def span(item):
    return {
        'start': {'line': item.get('name-row', item['row']) - 1,
                  'character': item.get('name-col', item['col']) - 1},
        'end': {'line': item.get('name-end-row', item.get('end-row', item['row'])) - 1,
                'character': item.get('name-end-col', item.get('end-col', item['col'])) - 1},
    }


def contains(item, pos):
    bounds = span(item)
    key = lambda p: (p['line'], p['character'])
    return key(bounds['start']) <= key(pos) < key(bounds['end'])


class Server:
    def __init__(self, kondo):
        self.kondo = kondo
        self.roots = []
        self.open_documents = {}
        self.cache = {}
        self.shutdown = False

    def analyze(self, path, text):
        previous = self.cache.get(path)
        if previous and previous[0] == text:
            return previous[1]
        root = next((r for r in self.roots if path.is_relative_to(r)), path.parent)
        result = subprocess.run(
            [self.kondo, '--lint', '-', '--filename', str(path), '--lang', 'clj',
             '--cache', 'false', '--config', CONFIG],
            input=text, text=True, capture_output=True, cwd=root, timeout=15)
        if result.returncode not in (0, 2, 3):
            raise RuntimeError(result.stderr or 'clj-kondo failed')
        analysis = json.loads(result.stdout)['analysis']
        self.cache[path] = (text, analysis)
        return analysis

    def index(self):
        paths = set(self.open_documents)
        for root in self.roots:
            for directory, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
                paths.update(Path(directory) / f for f in files if f.endswith('.jank'))
        analyses = {}
        for path in sorted(paths):
            try:
                text = self.open_documents.get(path)
                if text is None:
                    text = path.read_text(encoding='utf-8')
                analyses[path] = self.analyze(path, text)
            except FileNotFoundError:
                self.cache.pop(path, None)
        return analyses

    def definition(self, params):
        path = path_from_uri(params['textDocument']['uri'])
        analyses = self.index()
        current = analyses.get(path, {})
        pos = params['position']
        for usage in current.get('local-usages', []):
            if contains(usage, pos):
                return [self.location(path, d) for d in current.get('locals', [])
                        if d['id'] == usage['id']]
        for usage in current.get('var-usages', []):
            if contains(usage, pos):
                return [self.location(p, d) for p, a in analyses.items()
                        for d in a.get('var-definitions', [])
                        if (d['ns'], d['name']) == (usage.get('to'), usage['name'])]
        for usage in current.get('namespace-usages', []):
            if contains(usage, pos):
                return [self.location(p, d) for p, a in analyses.items()
                        for d in a.get('namespace-definitions', []) if d['name'] == usage['to']]
        return []

    @staticmethod
    def location(path, item):
        return {'uri': path.as_uri(), 'range': span(item)}

    def handle(self, method, params):
        if method == 'initialize':
            folders = params.get('workspaceFolders') or []
            uris = [f['uri'] for f in folders] or [params.get('rootUri')]
            self.roots = [path_from_uri(uri) for uri in uris if uri]
            return {'capabilities': {'definitionProvider': True,
                                     'textDocumentSync': {'openClose': True, 'change': 1}},
                    'serverInfo': {'name': 'jank-definitions', 'version': '0.0.2'}}
        if method == 'shutdown':
            self.shutdown = True
            return None
        if method == 'textDocument/didOpen':
            doc = params['textDocument']
            self.open_documents[path_from_uri(doc['uri'])] = doc['text']
        elif method == 'textDocument/didChange':
            for change in params['contentChanges']:
                self.open_documents[path_from_uri(params['textDocument']['uri'])] = change['text']
        elif method == 'textDocument/didClose':
            self.open_documents.pop(path_from_uri(params['textDocument']['uri']), None)
        elif method == 'textDocument/definition':
            return self.definition(params)
        elif method not in ('initialized', '$/cancelRequest', 'textDocument/didSave',
                            'workspace/didChangeConfiguration'):
            raise NotImplementedError(method)
        return None


def read_message(stream):
    headers = {}
    while True:
        line = stream.readline()
        if not line:
            return None
        if line in (b'\r\n', b'\n'):
            break
        name, value = line.decode('ascii').split(':', 1)
        headers[name.lower()] = value.strip()
    length = int(headers['content-length'])
    payload = stream.read(length)
    if len(payload) != length:
        raise EOFError('Truncated LSP message')
    return json.loads(payload)


def write_message(message):
    body = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(f'Content-Length: {len(body)}\r\n\r\n'.encode('ascii') + body)
    sys.stdout.buffer.flush()


def main():
    server = Server(sys.argv[1])
    while (message := read_message(sys.stdin.buffer)) is not None:
        method = message.get('method')
        if method == 'exit':
            return 0 if server.shutdown else 1
        response = {'jsonrpc': '2.0', 'id': message.get('id')}
        try:
            response['result'] = server.handle(method, message.get('params') or {})
        except NotImplementedError:
            response['error'] = {'code': -32601, 'message': f'Unknown method: {method}'}
        except Exception as error:
            print(f'jank-definitions: {error}', file=sys.stderr)
            response['error'] = {'code': -32603, 'message': str(error)}
        if 'id' in message:
            write_message(response)
    return 0


if __name__ == '__main__':
    sys.exit(main())
