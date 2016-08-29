import os
from datetime import datetime
import subprocess
import time

from lib import config
from lib.lib import log


class BaseRunner(object):
    TMP_FOLDER = config['tmp_folder']

    @classmethod
    def run_command(cls, command, debug=False):
        """ Run command and return its output. """
        if debug:
            log('Executing command "%s"' % command)
        process = os.popen(command)
        output = process.read()
        process.close()
        if debug:
            log('Command result: %s' % output)
        return output

    @classmethod
    def killall(cls, name, debug=False):
        """ Kill all processes with the given name. Block till all of killed processes get stopped. """
        cls.run_command('/usr/bin/killall -w %s 1>/dev/null 2>&1' % name, debug)

    @classmethod
    def run_background_command(cls, command, line_count=50, timeout=10, debug=False):
        """ Run command and return its output. max_line specifies the maximum number of lines that should be read. """
        tmp_file = '%s/check_%s.tmp' % (cls.TMP_FOLDER, os.getpid())
        output = ""
        start = datetime.now()
        try:
            subprocess.call('/usr/bin/nohup %s >%s 2>&1 &' % (command, tmp_file), shell=True)
            while (datetime.now() - start).total_seconds() < timeout:
                time.sleep(0.2)
                with open(tmp_file, 'r') as input:
                    output = input.read()
                if output.count('\n') >= line_count:
                    break
        except:
            pass
        finally:
            cls.delete_file(tmp_file)
        return output

    @classmethod
    def delete_file(cls, file_name):
        try:
            os.unlink(file_name)
        except:
            pass
