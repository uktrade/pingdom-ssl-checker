import threading
import os
import time
import json
import subprocess


class RunCheck(object):
	def __init__(self):

		self.interval = int(os.environ.get('CHECK_INTERVAL'))

		print "This check will run every %ds" % self.interval
		# self.create_url_status()
		RunCheck.create_url_status()

		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True  # Daemonize thread
		thread.start()

	@staticmethod
	def create_url_status():
		# copy url list to json format list
		first_run = True
		with open('url_status.json', 'w') as out:
			out.write('{}'.format("{"))
			url_contents = [url_content.rstrip('\n') for url_content in open('url_list')]

			for current_url in url_contents:
				if not current_url.startswith("#"):

					if first_run:
						out.write('{}{}{}'.format("\"", current_url, "\":\"(ok)\""))

						first_run = False
					else:
						out.write('{}{}{}'.format(",\"", current_url, "\":\"(ok)\""))

			out.write('{}'.format("}"))

	@staticmethod
	def get_ssl_status(url):
		# print url
		ssl_check = "echo | openssl s_client -connect " \
					+ url \
					+ ":443 -CAfile /etc/ssl/certs/ca-certificates.crt -tls1 2>/dev/null |grep Verify |awk '{print $5}'"

		ssl_response = subprocess.check_output(ssl_check, shell=True)
		return ssl_response[:4]

	def run(self):
		""" Method that runs forever """
		# check_log_url = "https://pingdom-ssl-checker.ukti.io/logs.html"

		while True:
			with open('url_status.json') as json_file:
				url_list_json = json.load(json_file)
			xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			xml_out_2 = "<pingdom_http_custom_check>"
			xml_out_5 = "</pingdom_http_custom_check>"

			time_str = time.strftime(" Returned @ Time Of Failure: %d/%m/%Y-%H:%M:%S")
			ssl_status = True
			t0 = time.time()

			with open('app/templates/logs.html', 'w') as out:
				out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Redirect check - logs</h1>', '<p>'))

			for current_url, status in url_list_json.iteritems():

					ssl_response = RunCheck.get_ssl_status(current_url)

					if ssl_response != '(ok)':
						ssl_response = "Bad cert please check site!"
					print "Checking URL: %s\tResponse: %s" % (current_url, ssl_response)

					if ssl_response != status:
						ssl_status = False

						with open('app/templates/logs.html', 'a') as out:
							out.write('{}{}{}{}{}{}{}{}{}\n'.format(
																	'Source: ',
																	current_url,
																	'    Expected result: ',
																	status,
																	'    Actual result: ',
																	ssl_response,
																	' -- Result: ',
																	'BAD',
																	'<br/>'))

						if status == '(ok)':
							url_list_json[current_url] = ssl_response + time_str

					if ssl_response == status:
						status = "(ok)"
						with open('app/templates/logs.html', 'a') as out:
							out.write('{}{}{}{}{}{}{}{}{}\n'.format(
																	'Source: ',
																	current_url,
																	'    Expected result: ',
																	status,
																	'    Actual result: ',
																	ssl_response,
																	' -- Result: ',
																	'GOOD',
																	'<br/>'))

			with open('url_status.json', 'w') as json_file:
				json.dump(url_list_json, json_file)

			with open('app/templates/logs.html', 'a') as out:
				if ssl_status is True:
					out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked -- OK --', '</p>', '</body>', '</html>'))
					print "--  All Sites Checked -- OK --"
				else:
					out.write('{}\n{}\n{}\n{}\n'.format(
														'--  All Sites Checked -- Bad Redirects Detected --',
														'</p>',
														'</body>',
														'</html>'))

					print "--  All Sites Checked -- Bad Redirects Detected --"

			t1 = time.time()
			total_time = (t1 - t0) * 1000

			if ssl_status is False:
				with open('app/templates/check.xml', 'w') as out:
					out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
					with open('url_status.json') as json_file:
						url_list_json = json.load(json_file)

						for key, value in url_list_json.iteritems():

							if value != '(ok)':
								out.write('{}{}{}\n'.format("<", key.replace('/', '-'), ">"))
								out.write('{}{}{}\n'.format(key, ":  ", value))
								out.write('{}{}{}\n'.format("</", key.replace('/', '-'), ">"))

					out.write('{}\n'.format("</status>"))
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))

			if ssl_status is True:
				with open('app/templates/check.xml', 'w') as out:
					xml_out_3 = "<status>OK</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
			time.sleep(self.interval)
