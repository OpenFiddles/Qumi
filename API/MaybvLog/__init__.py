# API\MaybvLog\__init__.py
import os
import sys
#from ...BASE.Configure import *
from Configure import *
"""

Logging system just for Qumi. See qumi.log for details.

Author: XiLy

"""

class MabLog:
    def __init__(self, log="qumi.log"):
        """
        Inits the log system, use "log=" as a arg to define a place to put the log data at! Requires a code in the file to work.
        """
        self.log_file = log
        self.validation_status = False
    def _check_valid_file(self):
        with open(self.log_file, mode="r") as f:
            for line in f:
                if "QUMICS" in line:
                    self.validation_status = True
                    print("Valid .log found, now we is able to write to file.")
                else: 
                    self.validation_status = False # false is not activated.
                    print("No valid code found yet, checked line: [{}]".format(str(line)))
    def append(self, text):
        """Appends a line at the end of file."""
        if self.validation_status == True:
            with open(self.log_file, mode="a") as f:
                f.write("\n{}".format(text))
                f.close()
        else: print("Locked... We cannot modify a file that's not authentic!")
    def get_log(self, text):
        """Read the log file"""
        if self.validation_status == True:
            with open(self.log_file, mode="r") as f:
                return f.read()
        else: print("Locked... We cannot modify a file that's not authentic!")
    def _create_if_not_exist(self):
        try:
            with open(self.log_file, mode="x") as f:
                f.write("[Logger][Done]: Log is done...\n")
                f.write("[Code]: Input a code to unlock..,\n")
                f.write("[Input Code on this line]: \n")
                f.close()
        except FileExistsError as FEE:
            print("qumi.log exists, no need to create it!")

if __name__ == "__main__":
    c = MabLog()
    c._create_if_not_exist()
    c._check_valid_file()
    c.append("hi")