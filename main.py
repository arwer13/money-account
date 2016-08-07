#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import importlib

import html_stuff
import config
from money import *




class HttpTestServer(BaseHTTPRequestHandler):



    def do_GET(self):
        importlib.reload(config)
        try:
            bk = load_data(config)
            model = make_model(bk, config.weekly_categories)
            self.do_GET_root(model)
        except Exception as e:
            self.do_GET_error(e)

    def do_GET_error(self, e):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_stuff.html_error_template.format(e).encode('utf-8'))

    def do_GET_root(self, model):
        html = html_stuff.represent_html(model)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    # def expenses_by_periods_plot(self, labels, values):
    #     ind = np.arange(len(values))
    #     plt.figure(figsize=(7,4))
    #     plt.bar(ind, values, facecolor='green', alpha=0.5, width=0.9)
    #     _, lbs = plt.xticks(ind + ind[1]/3, labels)
    #     plt.setp(lbs, rotation=70)
    #     plt.rc('font', size=9)
    #     plt.tight_layout()
    #     return plt.gcf()


if __name__ == "__main__":
    print('Started on port {}'.format(config.port))
    the_server = HTTPServer(("", config.port), HttpTestServer)
    try:
        the_server.serve_forever()
    except KeyboardInterrupt:
        pass

    the_server.server_close()
