import asyncio
import shlex
import sys
import os
import html


class Executor(object):
    """docstring for Executor"""

    async def _read(self, stream, filter):
        async for line in stream:
            line = filter(html.escape(line.decode().rstrip()))
            print(line)
            sys.stdout.flush()

    async def _run(self, cmd, pid_callback):

        ENV = os.environ.copy()
        ENV['PYTHONUNBUFFERED']='1'

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            env=ENV,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            pid_callback(proc.pid)
        except:
            pass

        aws = [
            self._read(proc.stdout, self.format_stdout),
            self._read(proc.stderr, self.format_stderr)
        ]
        await asyncio.gather(*aws)
        self.status = proc.returncode



    def run(self, cmd, pid_callback=None):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run(cmd, pid_callback))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        return self.status

    def format_stdout(self, line):
        return line

    def format_stderr(self, line):
        return line


if __name__ == '__main__':
    code = r'''
import datetime, time, sys
for i in range(10):
    print(datetime.datetime.now(), 'äöå')
    time.sleep(.1)
    x = 1/(9-i)
sys.exit(0)
    '''

    class MyExecutor(Executor):

        def format_stderr(self, line):
            return f"<error>{line}</error>"


    e = MyExecutor()
    cmd = ['python3', '-c', code]
    status = e.run()
    print(status)