"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""

import os
import ssl
import shutil
import urllib2
import xml.dom.minidom
import jinja2

from cct.module import Module

class Run(Module):

    def configure(self):
        """
        Aggregate method that calls all configure_ methods in sequence.
        """
        self.logger.debug("openshift-eap.Run::configure running!")
        self.setup_xml()
        self.inject_jinja_markers()
        self.teardown_xml()

    def setup_xml(self):
        jboss_home = os.getenv("JBOSS_HOME")
        self.config_file = "{}/standalone/configuration/standalone-openshift.xml".format(jboss_home)
        self.config = xml.dom.minidom.parse(self.config_file)

    def teardown_xml(self):
        with open(self.config_file, "w") as fh:
            self.config.writexml(fh)

    def _get_tag_by_attr(self, tag, attr, val):
        """Convenience method for getting a tag via an attribute value"""
        for elem in self.config.getElementsByTagName(tag):
            if elem.getAttribute(attr) == val:
                return elem
        self.logger.error("couldn't find correct {} element".format(tag))
        return

    def inject_jinja_markers(self):
        """
        Inject markers into the standalone-openshift.xml.in file, ready for
        both legacy shell scripts to do substitutions, and for newer Python
        to do substitutions via Jinja templating
        """
        # xml breaker: ##DEFAULT_DATASOURCE## and ##DEFAULT_JMS## were in
        # server/profile/subsystem xmlns urn:jboss:domain:ee:4.0/default-bindings
        # removed so jinja can parse the XML; but this will break datasources

        # SSL marker
        parent = self._get_tag_by_attr('security-realm', 'name', 'ApplicationRealm')
        parent.appendChild(self.config.createComment(" ##SSL## "))
