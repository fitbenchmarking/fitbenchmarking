import os
import sys
import platform

from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class OutputGrabber(object):
    """
    Class used to grab standard output and standard error.
    """
    escape_char = "\b"

    def __init__(self, options):

        self.stdout = sys.stdout
        self.stdoutfd = self.stdout.fileno()

        self.stderr = sys.stderr
        self.stderrfd = self.stderr.fileno()

        self.capturedstdout = ""
        self.capturedstderr = ""

        # From issue 500 the output grabber does not currently on windows, thus
        # we set the __enter__ and __exit__ functions to pass through for this
        # case
        self.system = platform.system() != "Windows"

        self.external_output = options.external_output

    def __enter__(self):
        if self.system and self.external_output:
            self.start()
        return self

    def __exit__(self, type, value, traceback):
        if self.system and self.external_output:
            self.stop()

    def start(self):
        """
        Start capturing the stream data.
        """
        # Create a pipe so the stream can be captured:
        self.stdout_out, self.stdout_in = os.pipe()
        self.stderr_out, self.stderr_in = os.pipe()
        self.capturedstdout = ""
        self.capturedstderr = ""

        # Save a copy of the stream:
        self.stdoutfd_bak = os.dup(self.stdoutfd)
        self.stderrfd_bak = os.dup(self.stderrfd)

        # Replace the original stream with our write pipe:
        os.dup2(self.stdout_in, self.stdoutfd)
        os.dup2(self.stderr_in, self.stderrfd)

    def stop(self):
        """
        Stop capturing the stream data and save the text in `capturedtext`.
        """
        # Print the escape character to make the readOutput method stop:
        self.stdout.write(self.escape_char)
        self.stderr.write(self.escape_char)
        # Flush the stream to make sure all our data goes in before
        # the escape character:
        self.stdout.flush()
        self.stderr.flush()

        # Reads the output and stores it
        self.readOutput()

        if self.capturedstdout:
            LOGGER.info('Captured output: \n%s', self.capturedstdout)

        if self.capturedstderr:
            LOGGER.info('Captured error: \n%s', self.capturedstderr)

        # Close the pipes:
        os.close(self.stdout_in)
        os.close(self.stdout_out)
        os.close(self.stderr_in)
        os.close(self.stderr_out)

        # Restore the original streams:
        os.dup2(self.stdoutfd_bak, self.stdoutfd)
        os.dup2(self.stderrfd_bak, self.stderrfd)

        # Close the duplicate streams:
        os.close(self.stdoutfd_bak)
        os.close(self.stderrfd_bak)

    def readOutput(self):
        """
        Read the stream data (one byte at a time)
        and save the text in `captured<stream>`.
        """
        while True:
            char = os.read(self.stdout_out, 1).decode(sys.stdout.encoding)
            if not char or self.escape_char in char:
                break
            self.capturedstdout += char

        while True:
            char = os.read(self.stderr_out, 1).decode(sys.stderr.encoding)
            if not char or self.escape_char in char:
                break
            self.capturedstderr += char
