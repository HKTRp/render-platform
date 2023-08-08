import pika
from pymongo import MongoClient
import gridfs
import os
import threading

from render import Render

env_vars = dict(os.environ)

if env_vars['MONGO_USERNAME']:
    mongodb_connection = MongoClient(env_vars['MONGO_HOST'],
                                     int(env_vars['MONGO_PORT']),
                                     username=env_vars['MONGO_USERNAME'],
                                     password=env_vars['MONGO_PASSWORD'])
else:
    mongodb_connection = MongoClient(env_vars['MONGO_HOST'],
                                     int(env_vars['MONGO_PORT']))
grid_fs = gridfs.GridFS(mongodb_connection.grid_file)


def run():
    credentials = pika.PlainCredentials(env_vars['RABBIT_USERNAME'], env_vars['RABBIT_PASSWORD'])
    with pika.BlockingConnection(pika.ConnectionParameters(env_vars['RABBIT_HOST'],
                                                           port=int(env_vars['RABBIT_PORT']),
                                                           credentials=credentials)) as connection:
        with connection.channel() as rabbit_channel:
            rabbit_channel.queue_declare("OnRender")
            rabbit_channel.basic_qos(prefetch_count=1)
            print("Connected, waiting for tasks")
            rabbit_channel.basic_consume(on_message_callback=render_project, queue="OnRender")
            try:
                rabbit_channel.start_consuming()
            except KeyboardInterrupt:
                rabbit_channel.stop_consuming()


def make_project_and_ack(render, ch, tag):
    render.make_project()
    ch.connection.add_callback_threadsafe(lambda: render.ack_message(ch, tag))


def render_project(ch, method, properties, body):
    render = Render(body.decode('utf-8'), grid_fs, env_vars['API_HOST'], env_vars['RENDER_AUTH_TOKEN'])
    threading.Thread(target=lambda: make_project_and_ack(render, ch, method.delivery_tag)).start()


if __name__ == "__main__":
    run()
