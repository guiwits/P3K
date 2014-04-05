import os
import sys
import re
import cookielib
import mechanize
import optparse

class main ():
    def __init__(self):

        ### Main portal to the JPL Mission Ephemeride files ###
        sps_url = "http://spsweb.fltops.jpl.nasa.gov/"

        ### Labels of each spacecraft to allow a way to create the correct URL for each ephemeride file ###
        labels = "ACE".split()
        #labels = "ACE CAS CHDR CLU1 CLU2 CLU3 CLU4 DIF GRLA GRLB GTL INTG JNO KEPL M01O MAP MER1 MER2 \
        #          MEX MGS MRO MSGR MSL MVN NHPC PHX PLC ROSE SDU SOHO STA STB STF TD10 TDR3 TDR4 \
        #          TDR5 TDR6 TDR7 TDR8 TDR9 TERR THB THC ULYS VEX VGR1 VGR2 WIND".split()

        ### Dawn has a strange url format so I separated it out ###
        dawn_url = 'http://spsweb.fltops.jpl.nasa.gov/portalappsops/FileBrowse.do?sfd=packages/Project/DAWN&ft=spa'

	#############################################################################
	### Start of main script. This will login to the sps website based on the ###
	### username and password input at runtime. After authentication, it will ###
	### visit each spacecraft page (based on the labels list) and download    ###
	### the spice files for each spacecraft and put them on blackhawk for use ###
	### by the explorer program. 			- Stephen Guiwits April 26, 2011  ###
	#############################################################################
        if len (sys.argv) != 5:  # the program name and the two arguments
  	    # stop the program and print an error message
            sys.exit ("Please provide a username and password.")

	### Default username and passwords don't have any real meaning and won't allow site access ###
        parser = optparse.OptionParser("usage: %prog [options] arg1 arg2")
        parser.add_option("-u", "--username", dest="username", default="eotss", type="string", help="specify username")
        parser.add_option("-p", "--password", dest="password", default="john", type="string", help="specify password")

        (options, args) = parser.parse_args()
        if len (sys.argv) != 5:
	    parser.error ("Incorrect number of arguments")
	    sys.exit ()

        login_username = options.username
        login_password = options.password

        ### Set up login to the SPS page ###
        browser = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        browser.set_cookiejar(cj)

        try:
	    browser.open (sps_url+"/portalappsops/Main.do")
        except Exception, e:
	    print ("Cannot open url: '%s', because: %s" % (sps_url+"/portalappsops/Main.do", e))
	    sys.exit()
	
        browser.select_form (name = "logonForm")
        browser["username"] = login_username
        browser["password"] = login_password
        browser.new_control ("HIDDEN", "action", {})
        control = browser.form.find_control ("action")
        control.readonly = False
        browser["action"] = "/portalappsops/Login.do"
        browser.method = "POST"
        browser.action = sps_url
        response = browser.submit()


	### Navigate to the main customer page ###
	### This will get us to: http://spsweb.fltops.jpl.nasa.gov/portalappsops/Main.do?ft=mos ###
        for link in browser.links():
	    print (link)
	    print (link.url)
	    if link.url == "Main.do?ft=mos":
                print ('match found')
                break

	### Link will have the last entry ###
        browser.follow_link (link)
        print (browser.geturl())

	### Continue to navigate further into the site ###
	### This will get us to: http://spsweb.fltops.jpl.nasa.gov/portalappsops/Ephemeris.do?ft=mos ###
        for link in browser.links():
	    print (link)
	    print (link.url)
	    if link.url == "Ephemeris.do?ft=mos":
                print ('match found')
                break

	### Link will have the last entry ###
        browser.follow_link (link)
        print (browser.geturl())

	### We are now at the page that has all the SPICE file directorys. We need to loop through ###
	### each directory and download each spice file within a given directory.		   ###
        for i in labels:
            spsdir = sps_url + "portalappsops/FileBrowse.do?fd=ephemerides/%s&ft=mos" % i
            #print dir
            ret_code = self.GetSpiceKernels (spsdir, browser)
	
    def GetSpiceKernels (self, url, browser):
        self.url = url
        self.browser = browser
	print "Downloading spice kernels for ", self.url

	### Need to get to each spacecraft directory that the labels make up 	###
	### and navigate to each one											###
	#bsp_links = list (self.browser.links (url_regex = re.compile ("https.*bsp_")))
	#print bsp_links
	#number_of_links = len (bsp_links)
	#print "Number of bps files in ", self.browser.geturl(), "is ", number_of_links
	### bsp_links[N].url will give you the link.url to download. Once this is known	###
	### it is easy to make the mechanize call to download the file. Code soon.    	###
	print self.browser.geturl()
	self.browser.follow_link (self.url)
	for link in self.browser.links (url_regex=re.compile ("http*bsp*")):
            print "File: " , link.url
												
	### Now that we're in the directory, find the BSP files ###
	#for link in browser.links (url_regex=re.compile ("https.*bsp_*")):
	#    print (link.url)
	#    break
	
        return 0	
'''
	### Navigate to the Customer Support Page ###
	bsp_list = list (self.browser.links (text_regex=re.compile ("Customer")))
	
	# Find the link for "bsp" so we get all the kernels
	try:
	    browser.follow_link (text_regex = re.compile ("bsp"))
	except HTTPError, e:
	    sys.exit ("post failed: %d: %s" % (e.code, e.msg))
	pass
	
	# Get all the bsp files
	bsps = [link.absolute_url for link in
	        browser.links (bsp_regex = re.compile (r"\.bsp$"))]
	print "Found", len (bsps), "spice kernels to download"

	for bsp in bsps:
	    filename = os.path.basename (bsp)
	    f = open (filename, "wb")
	    print "%s -->" % filename,
	    r = browser.open (bsp)
	    while 1:
	        data = r.read (1024)
	        if not data: break
	        f.write (data)
	    f.close()
	    print os.stat (filename).st_size, "bytes"
'''

if __name__ == "__main__":
    main()
