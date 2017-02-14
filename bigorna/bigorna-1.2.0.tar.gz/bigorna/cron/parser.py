from schedule import Job


class ParsingError(Exception):
    pass


class ScheduleParser:
    """
    Valid expressions:
    * every <num> <instant>
    * every <instant> at <time>
    """
    START = 'every'
    INSTANT = 'instant'
    AT = 'at'
    TIME = 'time'

    def __init__(self, scheduler, sched_jobs_cfg: list, run_job_fn):
        self.sched = scheduler
        self.sched_jobs_cfg = sched_jobs_cfg
        self.run_job_fn = run_job_fn

    def parse(self):
        from bigorna.cron.base import CronJob
        jobs = []
        for cfg in self.sched_jobs_cfg:
            job = CronJob(cfg['name'], cfg['task'], cfg.get('params', {}))
            self.parse_when(cfg['when'], job)
            jobs.append(job)
        return jobs

    def parse_when(self, times, job):
        for time in times:
            tokens = time.split()
            expression = self.parse_time_expression(tokens, self.sched, ScheduleParser.START)
            expression.do(self.run_job_fn, job)

    def parse_time_expression(self, tokens, expression, symbol):
        if len(tokens) == 0:
            return expression

        current_tk = tokens[0]
        tokens = tokens[1:]
        if symbol == ScheduleParser.START and current_tk.lower() == 'every':
            expression = expression.every
            return self.parse_time_expression(tokens, expression, ScheduleParser.INSTANT)
        elif symbol == ScheduleParser.INSTANT:
            try:
                num = int(current_tk)
                expression = expression(num)
                return self.parse_time_expression(tokens, expression, ScheduleParser.INSTANT)
            except ValueError:
                if not isinstance(expression, Job):
                    expression = expression()
                expression = expression.__getattribute__(current_tk)
                return self.parse_time_expression(tokens, expression, ScheduleParser.AT)
        elif symbol == ScheduleParser.AT:
            expression = expression.at
            return self.parse_time_expression(tokens, expression, ScheduleParser.TIME)
        elif symbol == ScheduleParser.TIME:
            return expression(current_tk)
        else:
            raise ParsingError("Invalid expression. Current token: %s, remaining tokens: %s" %
                               (current_tk, tokens))
