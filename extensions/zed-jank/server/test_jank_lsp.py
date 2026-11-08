import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from jank_lsp import Server, read_message


@unittest.skipUnless(shutil.which('clj-kondo'), 'clj-kondo is required')
class DefinitionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.lib = self.root / 'lib.jank'
        self.lib.write_text('(ns demo.lib)\n(defn draw [x] x)\n')
        self.main = self.root / 'main.jank'
        self.text = '(ns demo.main (:require [demo.lib :as lib :refer [draw]]))\n(defn run [x] (let [x x] (lib/draw x)))\n(draw 1)\n; lib/draw\n"lib/draw"\n(cpp/unknown)\n'
        self.main.write_text(self.text)
        self.server = Server(shutil.which('clj-kondo'))
        self.server.handle('initialize', {'rootUri': self.root.as_uri()})

    def goto(self, line, char):
        return self.server.definition({'textDocument': {'uri': self.main.as_uri()},
                                       'position': {'line': line, 'character': char}})

    def test_alias_and_refer(self):
        for line, char in [(1, 28), (2, 2)]:
            result = self.goto(line, char)
            self.assertEqual(result[0]['uri'], self.lib.as_uri())
            self.assertEqual(result[0]['range']['start'], {'line': 1, 'character': 6})

    def test_shadowed_locals(self):
        self.assertEqual(self.goto(1, 22)[0]['range']['start'], {'line': 1, 'character': 11})
        self.assertEqual(self.goto(1, 35)[0]['range']['start'], {'line': 1, 'character': 20})

    def test_namespace(self):
        self.assertEqual(self.goto(0, 26)[0]['range']['start'], {'line': 0, 'character': 4})

    def test_non_symbols(self):
        for line, char in [(3, 4), (4, 4), (5, 4)]:
            self.assertEqual(self.goto(line, char), [])

    def test_unsaved_and_close_and_disk_changes(self):
        self.server.handle('textDocument/didOpen', {'textDocument': {
            'uri': self.lib.as_uri(), 'text': '\n' + self.lib.read_text()}})
        self.assertEqual(self.goto(2, 2)[0]['range']['start']['line'], 2)
        self.server.handle('textDocument/didChange', {'textDocument': {'uri': self.lib.as_uri()},
            'contentChanges': [{'text': '\n\n' + self.lib.read_text()}]})
        self.assertEqual(self.goto(2, 2)[0]['range']['start']['line'], 3)
        self.server.handle('textDocument/didClose', {'textDocument': {'uri': self.lib.as_uri()}})
        self.assertEqual(self.goto(2, 2)[0]['range']['start']['line'], 1)
        self.lib.unlink()
        self.assertEqual(self.goto(2, 2), [])

    def test_same_file_utf16_and_reader_tag(self):
        text = '(ns demo.main)\n(def value 1)\n(str "😀" value)\n#cpp "int"\n'
        self.server.handle('textDocument/didOpen', {'textDocument': {
            'uri': self.main.as_uri(), 'text': text}})
        prefix = '(str "😀" '
        character = len(prefix.encode('utf-16-le')) // 2
        self.assertEqual(self.goto(2, character)[0]['range']['start'],
                         {'line': 1, 'character': 5})

    def test_wire_protocol(self):
        messages = [
            {'id': 1, 'method': 'initialize', 'params': {'rootUri': self.root.as_uri()}},
            {'method': 'initialized'},
            {'id': 2, 'method': 'textDocument/definition', 'params': {
                'textDocument': {'uri': self.main.as_uri()}, 'position': {'line': 2, 'character': 2}}},
            {'id': 3, 'method': 'unsupported'},
            {'id': 4, 'method': 'shutdown'}, {'method': 'exit'}]
        data = b''
        for message in messages:
            body = json.dumps(dict(jsonrpc='2.0', **message)).encode()
            data += f'Content-Length: {len(body)}\r\n\r\n'.encode() + body
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('jank_lsp.py')),
                                 shutil.which('clj-kondo')], input=data, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        import io
        stream = io.BytesIO(result.stdout)
        self.assertTrue(read_message(stream)['result']['capabilities']['definitionProvider'])
        self.assertEqual(read_message(stream)['result'][0]['uri'], self.lib.as_uri())
        self.assertEqual(read_message(stream)['error']['code'], -32601)
        self.assertIsNone(read_message(stream)['result'])


if __name__ == '__main__':
    unittest.main()
