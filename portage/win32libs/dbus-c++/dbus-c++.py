import info


class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['gitHEAD'] = 'git://gitorious.org/dbus-cplusplus/mainline.git'
        self.patchToApply['gitHEAD'] = ( 'works_for_win32.patch', 1 )
        self.targetConfigurePath['gitHEAD'] = 'cmake'

        self.svnTargets['gitFOLLOW'] = 'git://gitorious.org/~matlinuxer2/dbus-cplusplus/matlinuxer2s-mainline.git'
        self.targetConfigurePath['gitFOLLOW'] = 'cmake'

        self.shortDescription = "a C++ binding for dbus"
        self.defaultTarget = 'gitHEAD'
        #self.defaultTarget = 'gitFOLLOW'

    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.buildDependencies['dev-util/msys'] = 'default'
        self.dependencies['testing/pthreads-win32'] = 'default'
        self.dependencies['win32libs/dbus'] = 'default'
        self.dependencies['win32libs/expat'] = 'default'


from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self, **args ):
        CMakePackageBase.__init__( self )
        self.subinfo.options.package.packageName = 'dbus-c++'
        self.subinfo.options.make.slnBaseName = 'dbus-c++'

    def unpack(self):
        if not CMakePackageBase.unpack(self):
            return False
        # Check whether compiler is mingw or not...
        if self.compiler() != "mingw" and self.compiler() != "mingw4":
            utils.die("This package is currently only compiled with mingw.")

        return True


if __name__ == '__main__':
    Package().execute()
