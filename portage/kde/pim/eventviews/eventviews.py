import info
from CraftConfig import *
from CraftOS.osutils import OsUtils

class subinfo( info.infoclass ):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

        self.shortDescription = "Evenviews library"
        
    def setDependencies( self ):
        self.runtimeDependencies["virtual/base"] = "default"
        self.buildDependencies["frameworks/extra-cmake-modules"] = "master"
        self.runtimeDependencies["libs/qtbase"] = "default"
        self.runtimeDependencies["frameworks/ki18n"] = "default"
        self.runtimeDependencies["frameworks/kcodecs"] = "default"
        self.runtimeDependencies["kde/kcalutils"] = "default"
        self.runtimeDependencies["kde/kcalcore"] = "default"
        self.runtimeDependencies["kde/akonadi-calendar"] = "default"
        self.runtimeDependencies["kde/kmime"] = "default"
        self.runtimeDependencies["kde/calendarsupport"] = "default"
        self.runtimeDependencies["extragear/kdiagram"] = "default"
        

from Package.CMakePackageBase import *

class Package( CMakePackageBase ):
    def __init__( self ):
        CMakePackageBase.__init__( self )
