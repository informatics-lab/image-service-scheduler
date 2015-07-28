#!/usr/bin/env python

import boto
import iris

import sys
sys.path.append(".")
import config

class Job(object):
    """ message should be URI to OpenDAP """
    def __init__(self, message):
        self.open_dap = message
        self.data_file = message.split("/")[-1]
        self.model = self.data_file.split("_")[0]
        self.variable = "_".join(self.data_file.split("_")[1:-1])
        self.timestamp = self.data_file.split("_")[-1].split(".")[0]
    
    def __str__(self):
        self.data_file

    def getTimes(self):
        d = iris.load_cube(self.open_dap)
        return [t for in d.coord("time")]

    def getImgSvcJobMsgs(self):
        profs = config.getProfiles(self.model, self.variable)
        msgs = []
        for prof in profs:
            for time in self.getTimes():
                msg = {"data_file": self.data_file,
                                  "profile": prof,
                                  "time_step": time}
                msgs.append(msg)

        return msgs


class NoJobsError(Exception):
    def __init__(self, value=""):
        self.value = value
    def __str__(self):
        return repr(self.value)


def getTHREDDSJob(queue_name="thredds_queue", visibility_timeout=60):
    conn = boto.sqs.connect_to_region(os.getenv("AWS_REGION"),
                                      aws_access_key_id=os.getenv("AWS_KEY"),
                                      aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    queue = conn.get_queue(queue_name)
    messages = queue.get_messages(visibility_timeout, number_messages=1)
    try:
        message = messages[0]
    except IndexError:
        raise NoJobsError()

    return Job(message.get_body())


def postImgSvcJobs(msgs, queue_name="image_service_queue"):
    conn = boto.sqs.connect_to_region(os.getenv("AWS_REGION"),
                                      aws_access_key_id=os.getenv("AWS_KEY"),
                                      aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))
    queue = conn.get_queue(queue_name)
    for msg in msgs:
        print "Adding " + msg + " to the img svc job queue"
        m = boto.sqs.message.Message()
        m.message_attributes(msg)
        queue.write(m)


if __name__ == "__main__":
    job = getTHREDDSJob()
    print "Picked up " + job
    postImgSvcJobs(job.getImgSvcJobMsgs())