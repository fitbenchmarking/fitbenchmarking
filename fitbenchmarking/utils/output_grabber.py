import os
import sys
import platform

from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class OutputGrabber(object):
    """
    Class used to grab standard output or another stream.
    """
    escape_char = "\b"

    def __init__(self, options):

        self.origstream = sys.stdout
        self.origstreamfd = self.origstream.fileno()
        self.capturedtext = ""
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
        self.pipe_out, self.pipe_in = os.pipe()
        self.capturedtext = ""
        # Save a copy of the stream:
        self.streamfd = os.dup(self.origstreamfd)
        # Replace the original stream with our write pipe:
        os.dup2(self.pipe_in, self.origstreamfd)

    def stop(self):
        """
        Stop capturing the stream data and save the text in `capturedtext`.
        """
        # Print the escape character to make the readOutput method stop:
        self.origstream.write(self.escape_char)
        # Flush the stream to make sure all our data goes in before
        # the escape character:
        self.origstream.flush()

        # Reads the output and stores it in capturedtext
        self.readOutput()

        if self.capturedtext:
            LOGGER.info('Captured output: \n%s', self.capturedtext)

        # Close the pipe:
        os.close(self.pipe_in)
        os.close(self.pipe_out)
        # Restore the original stream:
        os.dup2(self.streamfd, self.origstreamfd)
        # Close the duplicate stream:
        os.close(self.streamfd)

    def readOutput(self):
        """
        Read the stream data (one byte at a time)
        and save the text in `capturedtext`.
        """
        while True:
            char = os.read(self.pipe_out, 1).decode(sys.stdout.encoding)
            if not char or self.escape_char in char:
                break
            self.capturedtext += char
