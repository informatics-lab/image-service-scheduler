#!/usr/bin/env python

import boto
import boto.sqs
import boto.sqs.jsonmessage
import os
import iris

import sys
sys.path.append(".")
from config import manifest

class Job(object):
    """ message should be URI to OpenDAP """
    def __init__(self, message):
        body = message.get_body()
        self.open_dap = body
        self.data_file = body.split("/")[-1]
        self.model = self.data_file.split("_")[0]
        self.variable = "_".join(self.data_file.split("_")[1:-1])
        self.timestamp = self.data_file.split("_")[-1].split(".")[0]
        self.message = message
    
    def __str__(self):
        self.data_file

    def getTimes(self, tcoordname="time"):
        d = iris.load_cube(self.open_dap)
        with iris.FUTURE.context(cell_datetime_objects=True):
            return [t.point.isoformat() for t in d.coord(tcoordname).cells()]

    def getImgSvcJobMsgs(self):
        profile_names = manifest.getProfiles(self.model, self.variable)
        msgs = []
        for profile_name in profile_names:
            times = self.getTimes()
            for i, time in enumerate(times):
                msg = {"data_file": self.data_file,
                       "profile_name": profile_name,
                       "time_step": time,
                       "frame": i,
                       "nframes": len(times)}
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
    messages = queue.get_messages(1, visibility_timeout=visibility_timeout)
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
    thredds_queue = getQueue("thredds_queue")
    image_service_queue = getQueue("image_service_queue")

    job = getTHREDDSJob(thredds_queue)

    postImgSvcJobs(job.getImgSvcJobMsgs(), image_service_queue)
    thredds_queue.delete_message(job.message)

    sys.exit()