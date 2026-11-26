class CPU:
    def __init__(self):
        self.job = None

    def is_free(self):
        return self.job is None

    def add_job(self, job):
        self.job = job

    def remove_job(self):
        job = self.job
        self.job = None
        return job
