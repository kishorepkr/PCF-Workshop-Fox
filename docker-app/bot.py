
#!/usr/bin/python
from twython import TwythonStreamer
import time, os
from routing import worker
import analysis
import datetime

#---------------------------------------------------------------
#
# Twitter Streamer
#
#---------------------------------------------------------------
class MyStreamer(TwythonStreamer):

        def on_success(self, data):
		""" compute sentiment and populate charts """
                analysis.populate(data)

        def on_error(self, status_code, data):
                print 'Bot error, status code = %s' % status_code
                time.sleep(60)
                streamRun()

        def on_timeout(self):
                print 'Bot timeout, sleeping for 60 seconds. Zzzzzz....'
                time.sleep(60)
                streamRun()


def streamRun():
        try:
		print "Initializing stream"
                stream = MyStreamer(os.getenv('APP_KEY'), os.getenv('APP_SECRET'),
                        os.getenv('OAUTH_TOKEN'), os.getenv('OAUTH_TOKEN_SECRET'), client_args={'verify':False} )
                track = sorted(set([tag.lower().strip() for tag in os.getenv('INCLUDE_TWITTER_HASH').split(',') ] ) )
                stream.statuses.filter(track=track)

        except Exception as e:
		print 'Bot error, streamRun exception: %s' % e
                time.sleep(60)
                streamRun()


def restartBot():
	python = sys.executable
	os.execl(python, python, * sys.argv)


if __name__=='__main__':
	try:
		worker.start()
		streamRun()

	except Exception as e:
		print 'Bot error, main exception: %s' % e
		worker.stop()
		restartBot()

	worker.stop()
