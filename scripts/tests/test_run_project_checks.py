"""Ensure optional project check discovery does not need hardcoded project names."""
from pathlib import Path
import tempfile
import unittest

from scripts.run_project_checks import discover_checks, run_checks


class ProjectCheckTests(unittest.TestCase):
    def test_no_extra_checks_is_allowed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'designs').mkdir()
            self.assertEqual(discover_checks(root), [])
            self.assertTrue(run_checks(root))

    def test_runs_discovered_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            scripts = root / 'designs' / 'household' / 'example' / 'scripts'
            scripts.mkdir(parents=True)
            (scripts / 'check_meshes.py').write_text('raise SystemExit(0)\n')
            self.assertEqual(len(discover_checks(root)), 1)
            self.assertTrue(run_checks(root))
            (scripts / 'check_meshes.py').write_text('raise SystemExit(1)\n')
            self.assertFalse(run_checks(root))


if __name__ == '__main__':
    unittest.main()
