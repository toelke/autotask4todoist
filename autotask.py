# Copyright (c) 2020, Philipp Tölke
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import todoist
import paho.mqtt.client as mqtt
import json
import logging
import textwrap
import os


TOPIC = os.environ.get('MQTT_TOPIC', 'todoist/activity')

api = todoist.TodoistAPI(os.environ['TODOIST_API_KEY'])

logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger()


def split_by_indentation(s: str):
    """Expects the string to be completely dedented"""
    lines = s.split("\n")
    while lines:
        block = [lines.pop(0)]
        while lines and (lines[0].startswith(" ") or lines[0].startswith("\t")):
            block.append(lines.pop(0))
        yield "\n".join(block)


def handle_completed_task(task_id):
    item = api.items.get(task_id)
    for note in item["notes"]:
        content = note["content"]
        if content.startswith("On Complete:"):
            logger.info('Handling comment')
            tasks_with_comments = split_by_indentation(content)
            for task_with_comments in tasks_with_comments:
                if '\n' in task_with_comments:
                    task, comments = task_with_comments.split("\n", 1)
                    comments = textwrap.dedent(comments)
                else:
                    task = task_with_comments
                    comments = None
                # Remove 'On Complete:'
                task = task[12:].strip()
                logger.info(f"adding task {task}")
                new_task = api.quick.add(task)
                logger.info(f'added as id {new_task["id"]}')
                if comments:
                    logger.info("Adding comments")
                    api.notes.add(new_task["id"], comments)
        else:
            logger.info('Skipping comment')
    logger.info('Finished handling complete event')
    api.commit()


def on_message(client, userdata, message):
    try:
        logger.info("Message received")
        event = json.loads(message.payload.decode("utf-8"))
        if event["event_type"] == "completed":
            logger.info(f'Task {event["object_id"]} completed')
            return handle_completed_task(event["object_id"])
        logger.info("Ignoring event: %d %s", event["object_id"], event["event_type"])
    except Exception as e:
        logger.exception(e)
        raise


def on_connect(client, userdata, flags, rc):
    logger.info("Connected")
    client.subscribe(TOPIC)


def on_subscribe(client, userdata, mid, granted_ops):
    logger.info("Subscribed")


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

mqtt_client.connect(os.environ.get('MQTT_BROKER', '127.0.0.1'))
mqtt_client.loop_forever()
