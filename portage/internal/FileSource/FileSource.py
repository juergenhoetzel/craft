import info

class subinfo(info.infoclass):
    def setDependencies(self):
        self.buildDependencies['gnuwin32/wget'] = 'default'

from Package.InternalPackageBase import *

class Package(InternalPackageBase):
    def __init__( self ):
        InternalPackageBase.__init__(self)

if __name__ == '__main__':
    Package().execute()
