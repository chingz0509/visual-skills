"""Guard against publishing secrets and accidentally bundling local files."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_privacy as privacy
import package


class PublicationTests(unittest.TestCase):
    def test_sensitive_values_are_reported_without_echoing_them(self):
        path = ('/Users/' + 'example/Documents/private.png').encode()
        secret = ('sk-' + 'X' * 30).encode()
        findings = privacy.audit_bytes('file.json', path + b' ' + secret)
        self.assertIn('personal absolute path', findings)
        self.assertIn('credential-like value', findings)
        self.assertNotIn(secret.decode(), str(findings))

    def test_untracked_or_unapproved_file_cannot_enter_install_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / 'skills/visual-skills'
            for name in package.REQUIRED:
                file = skill / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b'public skill content')
            private = skill / '.env'
            private.write_text('private local configuration')
            unapproved = skill / 'scripts/private-debug.py'
            unapproved.write_text('local debug note')
            candidates = [p for p in skill.rglob('*') if p.is_file()]
            with patch.object(package, 'ROOT', root), patch.object(package, 'SKILL', skill), patch.object(package, 'tracked_files', return_value=candidates):
                archive = package.package(root / 'dist')
            with zipfile.ZipFile(archive) as z:
                names = z.namelist()
                self.assertEqual(len(names), len(package.REQUIRED))
                self.assertFalse(any('.env' in name or 'private-debug' in name for name in names))


if __name__ == '__main__':
    unittest.main()
