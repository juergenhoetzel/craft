import base
import os
import sys
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['svnHEAD'] = '[git]kde:kiten|4.7|'
        for ver in ['0', '1', '2', '3', '4']:
            self.targets['4.7.' + ver] = "ftp://ftp.kde.org/pub/kde/stable/4.7." + ver + "/src/kiten-4.7." + ver + ".tar.bz2"
            self.targetInstSrc['4.7.' + ver] = 'kiten-4.7.' + ver
        self.targetDigests['4.7.0'] = '7caa8c13f6431d54eabc3a88f874f279134181c3'
        self.patchToApply['4.7.0'] = ("kiten-4.7.0-20110819.diff", 1)
        self.shortDescription = 'a Japanese reference/study tool'
        self.defaultTarget = 'svnHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kde-runtime'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = "-DBUILD_doc=OFF"

if __name__ == '__main__':
    Package().execute()
