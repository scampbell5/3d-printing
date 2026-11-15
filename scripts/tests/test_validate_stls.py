"""Sanity tests for the repository-wide STL integrity checks."""
from pathlib import Path
import tempfile
import unittest

import trimesh

from scripts.validate_stls import check_stl


class ValidationTests(unittest.TestCase):
    def test_good_watertight_box_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cube.stl'
            trimesh.creation.box(extents=(20, 20, 20)).export(path)
            self.assertTrue(check_stl(path).ok)

    def test_disconnected_solids_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'two-cubes.stl'
            a = trimesh.creation.box(extents=(10, 10, 10))
            b = trimesh.creation.box(extents=(10, 10, 10))
            b.apply_translation([30, 0, 0])
            trimesh.util.concatenate([a, b]).export(path)
            result = check_stl(path)
            self.assertFalse(result.ok)
            self.assertIn('shells=2', result.details)

    def test_git_lfs_pointer_fails_clearly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'pointer.stl'
            path.write_text('version https://git-lfs.github.com/spec/v1\n'
                            'oid sha256:' + '0' * 64 + '\nsize 10000\n')
            result = check_stl(path)
            self.assertFalse(result.ok)
            self.assertIn('Git LFS pointer', result.details)

    def test_invalid_mesh_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'broken.stl'
            path.write_bytes(b'not an STL')
            self.assertFalse(check_stl(path).ok)


if __name__ == '__main__':
    unittest.main()
