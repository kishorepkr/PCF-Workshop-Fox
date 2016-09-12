#!/usr/bin/python

from flask import Flask, request, redirect, url_for, send_from_directory
import json, os, logging
import cfworker
import analysis

BUBBLE_STATS = analysis.bubblestats()
PIE_STATS = analysis.piestats()

#---------------------------------------------------------------
#
# app routes: end points for the app's web interfaces
#
#---------------------------------------------------------------
worker = cfworker.cfworker( port=int(os.getenv('PORT')) )
worker.app = Flask(__name__, static_url_path='')

@worker.app.route('/')
def keen_chart():
        return worker.app.send_static_file('index.html')

@worker.app.route('/bubbles')
def bubble_chart():
        return worker.app.send_static_file('bubbles.html')

@worker.app.route('/sentiment')
def pie_chart():
        return worker.app.send_static_file('sentiment.html')

@worker.app.route('/timeline')
def timeline_chart():
        return worker.app.send_static_file('timeline.html')

@worker.app.route('/bubbles/post', methods=['POST'])
def post_bubbles():
        global BUBBLE_STATS
        try:
                trends = [str(f).lower() for f in request.get_json()['trends'] ]
		print "post_bubbles: %s" % trends
                BUBBLE_STATS.update( trends=trends )
        except Exception as e:
                print "post_bubbles: exception: %s"  % e
        finally:
                return json.dumps( BUBBLE_STATS.trend_count )

@worker.app.route('/metrics/field-value-counters/hashtags')
def metric_counter():
        global BUBBLE_STATS
        url = 'http://0.0.0.0:%d/metrics/field-value-counters/hashtags' % int(os.getenv('PORT'))
        return json.dumps({"name":"hashtags","links":[{"rel":"self","href": url}],"counts": BUBBLE_STATS.trend_count })

@worker.app.route('/pie/post', methods=['POST'])
def post_pie():
        global PIE_STATS
        try:
                sentiment = [request.get_json()['sentiment'] ]
                PIE_STATS.update( sentiment=sentiment )
                print PIE_STATS.sentiment_count
        except Exception as e:
                print e
        finally:
                return json.dumps( PIE_STATS.sentiment_count )

@worker.app.route('/metrics/field-value-counters/sentiment')
def pie_metric_counter():
        global PIE_STATS
        url = 'http://0.0.0.0:%d/metrics/field-value-counters/sentiment' % int(os.getenv('PORT'))
        return json.dumps({"name":"sentiment","links":[{"rel":"self","href": url}],"counts": PIE_STATS.sentiment_count })


@worker.app.route('/metrics/field-value-counters')
def field_counter():
        return ""

#---------------------------------------------------------------
#
# logging: suppresses some of the annoying Flask output
#
#---------------------------------------------------------------
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)
