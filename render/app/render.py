import os
import subprocess
import zipfile
import requests


def buffered_readall(file, buff_size=1024):
    buffer = file.read(buff_size)
    while buffer:
        yield buffer
        buffer = file.read(buff_size)


class Render:
    blender_project_file: str

    def __init__(self, filename, grid_fs, api_host, auth_token):
        self.input_filename = filename
        arr = filename.split('/')
        self.base_dir = '/'.join(arr[:-1])
        self.common_dir = 'projects/' + self.base_dir
        self.archive_filename = arr[-1]
        self.project_id = int(arr[0])
        self.working_dir = self.common_dir + '/raw'
        self.output_dir = self.common_dir + '/out'
        os.makedirs(os.path.dirname(self.working_dir), exist_ok=True)
        os.makedirs(os.path.dirname(self.output_dir), exist_ok=True)
        self.grid_fs = grid_fs
        self.api_host = api_host
        self.auth_token = auth_token

    def _change_project_status(self, new_status):
        url = 'http://%s:5000/api/v1.0/projects/%d/status' % (self.api_host, self.project_id)
        json = {'status': new_status}
        headers = {'Bearer': self.auth_token}
        requests.patch(url, headers=headers, json=json)

    @staticmethod
    def ack_message(ch, tag):
        if ch.is_open:
            ch.basic_ack(tag)

    def _get_file_from_db(self, filename):
        return self.grid_fs.find_one({"filename": filename})

    def _save_project(self):
        file = self._get_file_from_db(self.input_filename)
        out_filename = 'projects/' + self.input_filename
        with open(out_filename, 'wb') as output_file:
            output_file.writelines(buffered_readall(file))
        return out_filename

    def _unzip_file(self):
        directory = self.common_dir + '/raw'
        os.makedirs(directory, exist_ok=True)
        with zipfile.ZipFile(self.common_dir + '/' + self.archive_filename, 'r') as zf:
            zf.extractall(directory)
        files = os.listdir(directory)
        for file in files:
            if file.endswith('.blend'):
                self.blender_project_file = '%s/raw/%s' % (self.common_dir, file)

    def _render(self):
        subprocess.run(["blender", "-b", self.blender_project_file, "-o",
                        "//../out/render_", "-F", "PNG", "-x", "1", "-a"])

    def _zip_rendered_anim(self):
        out_filename = self.common_dir + '/rendered.zip'
        with zipfile.ZipFile(out_filename, 'w') as archive:
            for file in os.listdir(self.output_dir):
                archive.write(self.output_dir + "/" + file, arcname=file)

    def _save_render_archive_to_db(self):
        with open(self.common_dir + '/rendered.zip', 'rb') as file:
            self.grid_fs.put(file, filename=self.base_dir + '/rendered.zip')

    def make_project(self):
        self._change_project_status("RENDERING")
        self._save_project()
        self._unzip_file()
        self._render()
        self._zip_rendered_anim()
        self._save_render_archive_to_db()
        self._change_project_status("RENDERED")
