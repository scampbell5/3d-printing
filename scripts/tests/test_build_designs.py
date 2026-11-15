"""Quick tests for generic build manifest discovery and isolated artifacts."""
from pathlib import Path
import json
import tempfile
import unittest

from scripts.build_designs import (
    ManifestError, discover_projects, parse_manifest,
    run_builds, select_projects, command_for_project,
)


class BuilderTests(unittest.TestCase):
    def make_project(self, repo: Path, *, outputs=('generated.stl',), script=None):
        directory = repo / 'designs' / 'sample' / 'widget'
        (directory / 'cad').mkdir(parents=True)
        if script is None:
            script = ("from pathlib import Path\n"
                      "import os, trimesh\n"
                      "out = Path(os.environ['DESIGN_BUILD_OUTPUT_DIR'])\n"
                      "out.mkdir(parents=True, exist_ok=True)\n"
                      "trimesh.creation.box(extents=(20,20,20)).export(out / 'generated.stl')\n")
        (directory / 'cad' / 'make.py').write_text(script, encoding='utf-8')
        data = {
            'schema_version': 1,
            'id': 'sample/widget',
            'name': 'Example widget',
            'build': {'script': 'cad/make.py', 'outputs': list(outputs)},
        }
        (directory / 'design.json').write_text(json.dumps(data), encoding='utf-8')
        return directory

    def test_discovers_project_and_selects_by_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            found = discover_projects(root)
            self.assertEqual([p.slug for p in found], ['sample/widget'])
            self.assertEqual(select_projects(found, 'all'), found)
            self.assertEqual(select_projects(found, 'sample/widget'), found)
            with self.assertRaises(ManifestError):
                select_projects(found, 'typo')

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            data = json.loads((directory / 'design.json').read_text())
            data['build']['outputs'] = ['../escape.stl']
            (directory / 'design.json').write_text(json.dumps(data))
            with self.assertRaises(ManifestError):
                parse_manifest(directory / 'design.json', root)

    def test_rejects_mismatched_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            data = json.loads((directory / 'design.json').read_text())
            data['id'] = 'something/else'
            (directory / 'design.json').write_text(json.dumps(data))
            with self.assertRaises(ManifestError):
                discover_projects(root)

    def test_uv_dependency_group_is_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            data = json.loads((directory / 'design.json').read_text())
            data['build']['dependency_group'] = 'cad-my-project'
            (directory / 'design.json').write_text(json.dumps(data))
            (root / 'pyproject.toml').write_text('[dependency-groups]\ncad-my-project = ["trimesh"]\n')
            project = parse_manifest(directory / 'design.json', root)
            self.assertEqual(project.dependency_group, 'cad-my-project')
            self.assertIn('--group', command_for_project(project))
            self.assertIn('cad-my-project', command_for_project(project))
            self.assertIn('--locked', command_for_project(project))
            self.assertNotIn('pip', command_for_project(project))

    def test_unknown_uv_dependency_group_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            data = json.loads((directory / 'design.json').read_text())
            data['build']['dependency_group'] = 'missing'
            (directory / 'design.json').write_text(json.dumps(data))
            (root / 'pyproject.toml').write_text('[dependency-groups]\nci = ["trimesh"]\n')
            with self.assertRaises(ManifestError):
                parse_manifest(directory / 'design.json', root)

    def test_legacy_requirements_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            data = json.loads((directory / 'design.json').read_text())
            data['build']['requirements'] = 'cad/requirements.txt'
            (directory / 'design.json').write_text(json.dumps(data))
            with self.assertRaisesRegex(ManifestError, 'obsolete'):
                parse_manifest(directory / 'design.json', root)

    def test_build_writes_only_to_artifact_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = self.make_project(root)
            projects = discover_projects(root)
            artifact_root = root / 'dist' / 'builds'
            self.assertTrue(run_builds(projects, artifact_root, install=False))
            self.assertTrue((artifact_root / 'sample/widget/generated.stl').is_file())
            self.assertFalse((directory / 'stl/generated.stl').exists())
            self.assertIn('Overall: PASS', (artifact_root / 'BUILD-REPORT.md').read_text())

    def test_fails_when_expected_stl_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root, outputs=('generated.stl', 'missing.stl'))
            artifact_root = root / 'dist' / 'builds'
            self.assertFalse(run_builds(discover_projects(root), artifact_root, install=False))
            self.assertIn('missing generated STL', (artifact_root / 'BUILD-REPORT.md').read_text())

    def test_dry_run_does_not_generate_stl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            artifact_root = root / 'dist' / 'builds'
            self.assertTrue(run_builds(discover_projects(root), artifact_root, dry_run=True))
            self.assertFalse((artifact_root / 'sample/widget/generated.stl').exists())


if __name__ == '__main__':
    unittest.main()
