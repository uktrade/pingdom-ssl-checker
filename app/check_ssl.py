import threading, os, time, urllib2, json, sys, subprocess


class RunCheck(object):
	def __init__(self):

		self.interval = int(os.environ.get('CHECK_INTERVAL'))

		print "This check will run every %ds" % self.interval
		self.create_url_status()

		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True  # Daemonize thread
		thread.start()

	def create_url_status(self):
		#copy url list to json format list

		first = True
		with open('url_status.json','w') as out:
			out.write ('{}'.format("{"))
			url_contents = [url_content.rstrip('\n') for url_content in open ('url_list')]

			for current_url in url_contents:
				if not current_url.startswith("#"):

					if first:
						out.write('{}{}{}'.format("\"", current_url, "\":\"(ok)\""))

						first = False
					else:
						out.write('{}{}{}'.format(",\"", current_url, "\":\"(ok)\""))

			out.write ('{}'.format("}"))

	def get_ssl_status(self, url):
		#print url
		response_url = subprocess.check_output("echo | openssl s_client -connect " + url + ":443 -tls1 2>/dev/null |grep Verify |awk '{print $5}'", shell=True)


		return response_url[:4]


	def run(self):
		""" Method that runs forever """
		check_log_url = "https://pingdom-ssl-checker.ukti.io/logs.html"

		while True:
			with open('url_status.json') as json_file:
				d = json.load(json_file)
			xml_out_1 = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			xml_out_2 = "<pingdom_http_custom_check>"
			xml_out_5 = "</pingdom_http_custom_check>"

			#url_contents = [url_content.rstrip('\n') for url_content in open('url_list')]
			timestr = time.strftime(" Returned @ Time Of Failure: %d/%m/%Y-%H:%M:%S")
			redirect_status = True
			t0 = time.time()

			with open('app/templates/logs.html', 'w') as out:
				out.write('{}\n{}\n{}\n{}\n'.format('<html>', '<body>', '<h1>Redirect check - logs</h1>', '<p>'))

			for current_url, status in d.iteritems():

					response_url = self.get_ssl_status(current_url)
					#print response_url


					if response_url != '(ok)':
						response_url = "Bad cert please check site!"
					print "Checking URL: %s\tRespose: %s" % (current_url, response_url)

					# with open('app/templates/logs.html', 'a') as out:
					# 	out.write('{}\t\t{}{}{}\n'.format(current_url, ' -- Response: ', response_url, '<br/>'))

					# if response_code != 200:
					# 	redirect_status = False
					if response_url != status:
						redirect_status = False
						#status[1] = response_url + timestr

						with open('app/templates/logs.html', 'a') as out:
							out.write('{}{}{}{}{}{}{}{}{}\n'.format('Source: ',current_url ,'    Expected result: ',status ,'    Actual result: ',response_url ,' -- Result: ', 'BAD', '<br/>'))

						if (status == '(ok)'):
							d[current_url] = response_url + timestr

					if response_url == status:
						status = "(ok)"
						with open('app/templates/logs.html', 'a') as out:
							out.write('{}{}{}{}{}{}{}{}{}\n'.format('Source: ',current_url ,'    Expected result: ',status ,'    Actual result: ',response_url ,' -- Result: ', 'GOOD', '<br/>'))

			with open('url_status.json', 'w') as json_file:
				json.dump(d, json_file)

			with open('app/templates/logs.html', 'a') as out:
				if redirect_status == True:
					out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked -- OK --', '</p>', '</body>', '</html>'))
					print "--  All Sites Checked -- OK --"
				else:
					out.write('{}\n{}\n{}\n{}\n'.format('--  All Sites Checked -- Bad Redirects Detected --', '</p>', '</body>', '</html>'))
					print "--  All Sites Checked -- Bad Redirects Detected --"



			t1 = time.time()
			total_time = (t1 - t0) * 1000

			if redirect_status == False:
				with open('app/templates/check.xml', 'w') as out:
					out.write('{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, "<status>"))
					with open('url_status.json') as json_file:
						d = json.load(json_file)
						# for key, value in xml_list.items():
						for key, value in d.iteritems():
							#print (key)
							#print (value)

							if (value != '(ok)'):
								out.write('{}{}{}\n'.format("<", key.replace('/','-'), ">"))
								#out.write('{}\n'.format("Expected ..."))
								out.write('{}{}{}\n'.format(key, ":  ", value))
								#for x in value:
								#	out.write('{}\n'.format(x))
								#out.write('{}\n'.format("...Actually Returned"))
								out.write('{}{}{}\n'.format("</", key.replace('/','-'), ">"))

					out.write('{}\n'.format("</status>"))
					# xml_out_3 = "<status XML-LINK=\"LINK\" HREF=\"https://pingdom-redirect-checker.ukti.io/logs.html\">Logs Link</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n'.format(xml_out_4, xml_out_5))

			if redirect_status == True:
				with open('app/templates/check.xml', 'w') as out:
					xml_out_3 = "<status>OK</status>"
					xml_out_4 = "<response_time>%.2f</response_time>" % total_time
					out.write('{}\n{}\n{}\n{}\n{}\n'.format(xml_out_1, xml_out_2, xml_out_3, xml_out_4, xml_out_5))
			time.sleep(self.interval)
