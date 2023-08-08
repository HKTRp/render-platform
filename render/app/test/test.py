import unittest
from unittest.mock import Mock

from ..main import Render
import os
import shutil


class TestRenderer(unittest.TestCase):
    TEST_FILES = ['testcube.zip', 'test_cube_animated.zip', 'CozyRoom.zip']
    USER_ID = 1
    PROJECT_ID = 1

    @staticmethod
    def get_test_file(filename):
        test_name = filename.split('/')[-1]
        return open(os.path.join('app', 'test', test_name), 'rb')

    def make_project(self, filename_id):
        full_name = "%d/%d/%s" % (self.USER_ID, self.PROJECT_ID, self.TEST_FILES[filename_id])
        render = Render(full_name, None)
        render._get_file_from_db = Mock(side_effect=self.get_test_file)
        render._save_render_archive_to_db = Mock()
        render.make_project()

    def check_file(self, filename_id, frames_amount):
        self.make_project(filename_id)
        base_path = './projects/%d/%d' % (self.USER_ID, self.PROJECT_ID)
        out_path = os.path.join(base_path, 'out')
        out_file_path = os.path.join(base_path, 'rendered.zip')
        self.assertTrue(os.path.isdir(out_path))
        self.assertEqual(len(os.listdir(out_path)), frames_amount)
        self.assertTrue(os.path.isfile(out_file_path))

    def test_cube(self):
        self.check_file(0, 1)

    def test_cube_animation(self):
        self.check_file(1, 250)

    def tearDown(self) -> None:
        shutil.rmtree('./projects')
        self.PROJECT_ID += 1


if __name__ == "__main__":
    unittest.main()
