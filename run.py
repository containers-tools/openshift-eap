"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""

import os
import shutil
import xml.dom.minidom
import jinja2

from cct.module import Module

class Run(Module):

    def configure(self):
        """
        Aggregate method that calls all configure_ methods in sequence.
        """
        self.initialize_templates()
        self.inject_jinja_markers()
        self.process_jinja_template()

    def initialize_templates(self):
        """
        Open and initialize jinja template objects
        """
        self.templates = {}
        jboss_home = os.getenv("JBOSS_HOME")
        template_path = "{}/standalone/configuration/templates".format(jboss_home)
        for t in os.listdir(template_path):
            with open(os.path.join(template_path,t)) as fh:
                self.templates[t] = jinja2.Template(fh.read())

    def inject_jinja_markers(self):
        """
        Inject markers into the standalone-openshift.xml file, ready for other
        scripts to do insertions via Jinja templating
        """

        jboss_home = os.getenv("JBOSS_HOME")
        self.config_file = "{}/standalone/configuration/standalone-openshift.xml".format(jboss_home)
        self.config = xml.dom.minidom.parse(self.config_file)

        # xml breaker: ##DEFAULT_DATASOURCE## and ##DEFAULT_JMS## were in
        # server/profile/subsystem xmlns urn:jboss:domain:ee:4.0/default-bindings
        # removed so jinja can parse the XML; but this will break datasources

        # A datasources marker, will be handle by jinja (us)
        parent = self._get_tag_by_attr('subsystem', 'xmlns', 'urn:jboss:domain:ee:4.0')
        parent.appendChild(self.config.createTextNode("{{ default_bindings }}"))

        with open(self.config_file, "w") as fh:
            self.config.writexml(fh)

    def process_jinja_template(self):
        """
        Processes the Jinja template standalone-openshift.xml to generate the real
        deal.
        """
        # XXX: this will end up in another routine. Substitutions here are just what
        # is needed for the older shell scripts to work.
        default_bindings = self.templates['default-bindings.jinja'].render(
            default_datasource='##DEFAULT_DATASOURCE##',
            default_jms='##DEFAULT_JMS##'
        )
        self.logger.debug("process_jinja_template: chunk = {}".format(default_bindings))

        with open(self.config_file,"r+") as fh:
            template = jinja2.Template(fh.read())
            fh.seek(0)
            fh.write(template.render(default_bindings=default_bindings))

    def _get_tag_by_attr(self, tag, attr, val):
        """Convenience method for getting a tag via an attribute value"""
        for elem in self.config.getElementsByTagName(tag):
            if elem.getAttribute(attr) == val:
                return elem
        self.logger.error("couldn't find correct {} element".format(tag))
        return
