import info


class subinfo(info.infoclass):
    def setTargets( self ):
        if emergePlatform.buildArchitecture() == "x86":
            self.targets[ "base" ] = "http://downloads.sourceforge.net/sourceforge/msys2/msys2-base-i686-20131208.tar.xz"
        else:
            self.targets[ "base" ] = "http://downloads.sourceforge.net/sourceforge/msys2/msys2-base-x86_64-20131208.tar.xz"
        self.defaultTarget = "base"


    def setDependencies( self ):
        self.buildDependencies['virtual/bin-base'] = 'default'

    def setBuildOptions( self ):
        self.disableHostBuild = False
        self.disableTargetBuild = True

from Package.BinaryPackageBase import *

class Package(BinaryPackageBase):
    def __init__( self):
        self.subinfo = subinfo()
        self.subinfo.options.merge.ignoreBuildType = True
        BinaryPackageBase.__init__(self)        
        self.shell = MSysShell()

    def unpack(self):
        if not BinaryPackageBase.unpack(self):
          return False
        if emergePlatform.buildArchitecture() == "x64":
           shutil.move(os.path.join( self.imageDir(), "msys64"), os.path.join( self.imageDir(), "msys"))
        else:
           shutil.move(os.path.join( self.imageDir(), "msys32"), os.path.join( self.imageDir(), "msys"))
        utils.copyFile(os.path.join(self.packageDir(),"msys.bat"),os.path.join(self.rootdir,"dev-utils","bin","msys.bat"))
        return True
    
    def qmerge(self):
        if not BinaryPackageBase.qmerge(self):
           return False
        msysDir = os.path.join(os.getenv("KDEROOT"),"msys")
        self.shell.execute(".","echo Firstrun")#start and restart msys before first use
        self.shell.execute(".","pacman -Syu --noconfirm")        
        utils.system("autorebase.bat", cwd = msysDir)
        self.shell.execute(".","pacman -Sy --noconfirm")   
        self.shell.execute(".","pacman -S base-devel --noconfirm")
        utils.system("autorebase.bat", cwd = msysDir)
        return True
       
if __name__ == '__main__':
    Package().execute()
