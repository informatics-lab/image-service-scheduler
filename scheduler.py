#!/usr/bin/env python

import boto
import boto.sqs
import boto.sqs.jsonmessage
import os
import iris
import json

import sys
sys.path.append(".")
from config import manifest

class Job(object):
    """ message should be URI to OpenDAP """
    def __init__(self,  message):
        body = json.loads(message.get_body())["Message"]
        self.open_dap = body
        self.data_file = body.split("/")[-1]
        info = manifest.runnames[self.data_file.split("_")[0]]
        self.model = info["model"]
        self.variable = "_".join(self.data_file.split("_")[1:-3])
        self.timestamp = self.data_file.split("_")[-2]
        self.profile_name = info["profile"]
        self.message = message
        self.nframes = info["nframes"]
    
    def __str__(self):
        self.data_file

    def getTimes(self, tcoordname="time"):
        d = iris.load_cube(os.path.join(os.getenv("DATA_DIR"), self.data_file))
        with iris.FUTURE.context(cell_datetime_objects=True):
            return [t.point.isoformat() for t in d.coord(tcoordname).cells()]

    def getImgSvcJobMsgs(self):
        msgs = []

        times = self.getTimes()
        for i, time in enumerate(times):
            msg = {"data_file": self.data_file,
                   "open_dap": self.open_dap,
                   "variable": self.variable,
                   "model": self.model,
                   "profile_name": self.profile_name,
                   "time_step": time,
                   "frame": int(self.data_file[-5:-3]) - 1 + i, # bespoke for umqvaa HACK HACKITY HACK
                   "nframes": self.nframes;}
            msgs.append(msg)

        return msgs


class NoJobsError(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return repr(self.value)


def getQueue(queue_name):
    conn = boto.sqs.connect_to_region(os.getenv("AWS_REGION"),
                                      aws_access_key_id=os.getenv("AWS_KEY"),
                                      aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    queue = conn.get_queue(queue_name)
    return queue


def getTHREDDSJob(queue, visibility_timeout=60):
    print "Getting job"
    messages = queue.get_messages(num_messages=1, visibility_timeout=visibility_timeout)
    try:
        message = messages[0]
    except IndexError:
        raise NoJobsError()

    job = Job(message)
    
    return job


def postImgSvcJobs(msgs, queue):
    nframes = len(msgs)
    for i, msg in enumerate(msgs):
        print "Adding " + str(msg) + " to the img svc job queue"
        m = boto.sqs.jsonmessage.JSONMessage()
        m.set_body(msg)
        queue.write(m)


if __name__ == "__main__":
    image_service_scheduler_queue = getQueue("image_service_scheduler_queue")
    image_service_queue = getQueue("image_service_queue")

    job = getTHREDDSJob(image_service_scheduler_queue)

    postImgSvcJobs(job.getImgSvcJobMsgs(), image_service_queue)
    image_service_scheduler_queue.delete_message(job.message)

    sys.exit()