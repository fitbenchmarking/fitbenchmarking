import os
import sys
import platform

from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class OutputGrabber:
    """
    Class used to grab outputs for stdout and stderr
    """
    def __init__(self, options):
        self.stdout_grabber = StreamGrabber(sys.stdout)
        self.stderr_grabber = StreamGrabber(sys.stderr)

        # From issue 500 the output grabber does not currently on windows, thus
        # we set the __enter__ and __exit__ functions to pass through for this
        # case
        self.system = platform.system() != "Windows"

        self.external_output = options.external_output

    def __enter__(self):
        if self.system and self.external_output != 'debug':
            self.stdout_grabber.start()
            self.stderr_grabber.start()
        return self

    def __exit__(self, type, value, traceback):
        if self.system and self.external_output:
            self.stdout_grabber.stop()
            self.stderr_grabber.stop()
            if self.stdout_grabber.capturedtext:
                self._log('Captured output: \n%s',
                          self.stdout_grabber.capturedtext)

            if self.stderr_grabber.capturedtext:
                self._log('Captured error: \n%s',
                          self.stderr_grabber.capturedtext)

    def _log(self, str_log, *args):
        if self.external_output == 'log_only':
            LOGGER.debug(str_log, *args)
        else:
            LOGGER.info(str_log, *args)


class StreamGrabber:
    """
    Class used to grab an output stream.
    """
    escape_char = "\b"

    def __init__(self, stream):

        self.origstream = stream
        self.origstreamfd = stream.fileno()
        self.encoding = stream.encoding

        self.capturedtext = ""

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

        # Close the pipes:
        os.close(self.pipe_in)
        os.close(self.pipe_out)

        # Restore the original streams:
        os.dup2(self.streamfd, self.origstreamfd)

        # Close the duplicate streams:
        os.close(self.streamfd)

    def readOutput(self):
        """
        Read the stream data (one byte at a time)
        and save the text in `capturedtext`.
        """
        while True:
            char = os.read(self.pipe_out, 1).decode(self.encoding)
            if not char or self.escape_char in char:
                break
            self.capturedtext += char
