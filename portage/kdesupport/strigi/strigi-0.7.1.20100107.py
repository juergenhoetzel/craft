import info

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.dependencies['libs/qt'] = 'default'
        self.dependencies['win32libs-bin/clucene-core'] = 'default'
        if not emergePlatform.isCrossCompilingEnabled():
            self.dependencies['win32libs-bin/exiv2'] = 'default'
        else:
            #FIXME make strigi svnHEAD compile on Windows
            # This hack is needed to get a different Version of
            # strigi for the Host platform
            self.buildDependencies['enterprise5/strigi-e5'] = 'default'
        self.dependencies['win32libs-bin/win_iconv'] = 'default'
        self.dependencies['win32libs-bin/libbzip2'] = 'default'
        self.dependencies['win32libs-bin/libxml2'] = 'default'
        self.dependencies['win32libs-bin/zlib'] = 'default'

    def setTargets( self ):
        self.svnTargets['0.5.7'] = 'tags/strigi/strigi/0.5.7'
        self.svnTargets['0.5.8'] = 'tags/strigi/strigi/0.5.8'
        self.svnTargets['0.5.9'] = 'tags/strigi/strigi/0.5.9'
        self.svnTargets['0.5.10'] = 'tags/strigi/strigi/0.5.10'
        self.svnTargets['0.5.11'] = 'tags/strigi/strigi/0.5.11'
        self.svnTargets['0.6.3']  = 'tags/strigi/strigi/0.6.3'
        self.svnTargets['0.6.4']  = 'tags/strigi/strigi/strigi-0.6.4'
        self.svnTargets['0.6.5']  = 'tags/strigi/strigi/0.6.5'
        self.svnTargets['0.7.0']  = 'tags/strigi/strigi/0.7.0'
        self.svnTargets['0.7.1']  = 'tags/strigi/strigi/0.7.1'
        self.svnTargets['svnHEAD'] = 'trunk/kdesupport/strigi'
        self.svnTargets['komobranch'] = 'branches/work/komo/strigi'
        for i in ['4.3.0', '4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3']:
            self.svnTargets[ i ] = 'tags/kdesupport-for-4.3/kdesupport/strigi'
        for i in ['4.4.0', '4.4.1', '4.4.2', '4.4.3', '4.4.4', '4.4']:
            self.svnTargets[ i ] = 'tags/kdesupport-for-4.4/strigi'
        if emergePlatform.isCrossCompilingEnabled():
          #FIXME make strigi svnHEAD compile on Windows
          self.defaultTarget = 'komobranch'
        else:
          self.defaultTarget = 'svnHEAD'

    def setBuildOptions( self ):
        self.disableHostBuild = True
        self.disableTargetBuild = False
          
from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = ""
        if emergePlatform.isCrossCompilingEnabled():
            self.subinfo.options.configure.defines = "-DBUILD_DAEMON=OFF "
            self.subinfo.options.configure.defines += "-DBUILD_DEEPTOOLS=OFF "
            self.subinfo.options.configure.defines += "-DBUILD_UTILS=OFF "
            self.subinfo.options.configure.defines += "-DENABLE_CLUECENE=OFF "
            self.subinfo.options.configure.defines += "-DENABLE_CPPUNIT=OFF "

        qmake = os.path.join(self.mergeDestinationDir(), "bin", "qmake.exe")
        if not os.path.exists(qmake):
            utils.warning("could not find qmake in <%s>" % qmake)
        ## \todo a standardized way to check if a package is installed in the image dir would be good.
        self.subinfo.options.configure.defines += "-DQT_QMAKE_EXECUTABLE:FILEPATH=%s " \
            % qmake.replace('\\', '/')

if __name__ == '__main__':
    Package().execute()
