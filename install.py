"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the MIT license. See the LICENSE file for details.
"""

import os
import shutil

from cct.module import Module

class Install(Module):

    def install(self):
        self.openshift_scripts()
        self.launch()
        self.install_jinja_templates()

    def launch(self):
        added = "/tmp/cct/openshift-eap/os-eap7-launch/added"

        dst = os.path.join(os.getenv('JBOSS_HOME'), "bin", "launch")
        if not os.path.exists(dst):
            os.makedirs(dst)

        src = os.path.join(added, "launch")
        for f in os.listdir(src):
            shutil.move(os.path.join(src,f), dst)

        shutil.move(os.path.join(added, "openshift-launch.sh"), os.path.join(os.getenv("JBOSS_HOME"), "bin"))

    def openshift_scripts(self):
        """
        re-implementation of os-eap7-openshift
        """

        added = "/tmp/cct/openshift-eap/os-eap7-openshift/added"
        jboss_home = os.getenv("JBOSS_HOME")

        with open("{}/bin/standalone.conf".format(jboss_home), "a") as out_fh:
            with open("{}/standalone.conf".format(added), "r") as in_fh:
                out_fh.write(in_fh.read())

        dst = "{}/standalone/configuration/standalone-openshift.xml".format(jboss_home)
        shutil.move("{}/standalone-openshift.xml".format(added), dst)
        os.chown(dst, 185, 185)

    def install_jinja_templates(self):
        """
        Install jinja template snippets into the image
        """
        jboss_home = os.getenv("JBOSS_HOME")
        src = "/tmp/cct/openshift-eap/templates"
        dst = "{}/standalone/configuration/templates".format(jboss_home)
        shutil.move(src,dst)
        for t in (os.listdir(dst)+['']):
            os.chown(os.path.join(dst,t), 185, 185)
