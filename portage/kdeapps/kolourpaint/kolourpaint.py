import info
from Package.CMakePackageBase import *
from Packager.NullsoftInstallerPackager import *

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.svnTargets["frameworks"] = "[git]kde:kolourpaint|frameworks"
        self.defaultTarget = "frameworks"
        self.shortDescription = "KolourPaint is an easy-to-use paint program"

    def setDependencies( self ):
        self.buildDependencies["dev-util/extra-cmake-modules"] = "default"
        self.dependencies["libs/qtbase"] = "default"
        self.dependencies["libs/runtime"] = "default" #mingw-based builds need this
        self.dependencies["kdesupport/qimageblitz"] = 'default'
        self.dependencies["frameworks/kconfig"] = "default"
        self.dependencies["frameworks/kguiaddons"] = "default"
        self.dependencies["frameworks/kdelibs4support"] = "default"
        self.dependencies["frameworks/ki18n"] = "default"
        self.dependencies["frameworks/kio"] = "default"
        self.dependencies["frameworks/kparts"] = "default"
        self.dependencies["frameworks/kxmlgui"] = "default"
        self.dependencies["frameworks/breeze-icons"] = 'default'

class Package( CMakePackageBase, NullsoftInstallerPackager ):
    def __init__( self):
        CMakePackageBase.__init__( self )
        blacklists = [
            NSIPackagerLists.runtimeBlacklist,
            os.path.join(os.path.dirname(__file__), "blacklist.txt")
        ]
        NullsoftInstallerPackager.__init__(self, blacklists=blacklists)

    def createPackage(self):
        self.defines[ "productname" ] = "Kolourpaint"
        self.defines[ "executable" ] = "bin\\kolourpaint.exe"
        self.defines[ "icon" ] = os.path.join(os.path.dirname(__file__), "kolourpaint.ico")

        self.ignoredPackages.append("binary/mysql-pkg")
        self.ignoredPackages.append("gnuwin32/sed")
        self.ignoredPackages.append("frameworks/kdesignerplugin")
        self.ignoredPackages.append("frameworks/kemoticons")

        return NullsoftInstallerPackager.createPackage(self)
