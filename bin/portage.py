## @package portage
#  @brief contains portage tree related functions
#  @note this file should replace all other related portage related files
import builtins
import importlib
from collections import OrderedDict

from EmergePackageObject import PackageObjectBase
from EmergeConfig import *
import InstallDB
import utils

#a import to portageSearch infront of def getPackagesCategories to prevent the circular import with installdb

class PortageException(Exception):
    def __init__(self, message, category, package ):
        Exception.__init__(self, message)
        self.category = category
        self.package = package


class DependencyPackage(object):
    """ This class wraps each package and constructs the dependency tree
        original code is from dependencies.py, integration will come later...
        """
    #cache for dependency packages, to prevent loop imports
    _dependencyPackageDict = OrderedDict()

    def __init__( self, category, name, version , autoExpand = True ):
        self.category = category
        self.name = name
        self.version = version
        self.runtimeChildren = []
        self.buildChildren = []
        if autoExpand:
            self.__readChildren()

    def __hash__(self):
        return str( self.category + "/" +  self.name).__hash__()
        
    def __eq__( self, other ):
        return self.category == other.category and self.name == other.name and self.version == other.version

    def __ne__( self, other ):
        return self.category != other.category or self.name != other.name or self.version != other.version

    def ident( self ):
        return [ self.category, self.name, self.version, PortageInstance.getDefaultTarget( self.category, self.name ) ]

    def __readChildren( self ):
        runtimeDependencies, buildDependencies = readChildren( self.category, self.name )
        self.runtimeChildren = self.__readDependenciesForChildren( list(runtimeDependencies.keys()) )
        self.buildChildren = self.__readDependenciesForChildren( list(buildDependencies.keys()) )

    def __readDependenciesForChildren( self, deps ):
        children = []
        if deps:
            for line in deps:
                ( category, package ) = line.split( "/" )
                utils.debug( "category: %s, name: %s" % ( category, package ), 1 )
                try:
                    version = PortageInstance.getNewestVersion( category, package )
                except PortageException as e:
                    utils.warning("%s for %s/%s as a dependency of %s/%s" %(e, e.category, e.package, self.category , self.name))
                    continue

                if not line in self._dependencyPackageDict.keys():
                    p = DependencyPackage( category, package, version, False )
                    utils.debug( "adding package p %s/%s-%s" % ( category, package, version ), 1 )
                    self._dependencyPackageDict[ line ] = p
                    p.__readChildren()
                else:
                    p = self._dependencyPackageDict[ line ]
                children.append( p )
        return children

    def getDependencies( self, depList=None, dep_type="both", single = set(), maxDetpth = -1, depth = 0):
        """ returns all dependencies """
        if depList is None:
            depList = []
        if dep_type == "runtime":
            children = self.runtimeChildren
        elif dep_type == "buildtime":
            children = self.buildChildren
        else:
            children = self.runtimeChildren + self.buildChildren
            
        single.add(self)
        for p in children:
            if not p in single and not p in depList\
            and not ("%s/%s" % (p.category, p.name)) in PortageInstance.ignores:
                if maxDetpth == -1:
                    p.getDependencies( depList, dep_type, single )
                elif depth < maxDetpth:
                    p.getDependencies( depList, dep_type, single, maxDetpth = maxDetpth, depth = depth + 1 )
                    
        #if self.category != internalCategory:
        if not self in depList and not ("%s/%s" % (self.category, self.name)) in PortageInstance.ignores:
            depList.append( self )



        return depList

def buildType():
    """return currently selected build type"""
    return emergeSettings.get("General","EMERGE_BUILDTYPE")

def rootDirectories():
    # this function should return all currently set portage directories
    if ("General", "EMERGE_PORTAGE_ROOT" ) in emergeSettings:
        rootDirs = emergeSettings.get("General", "EMERGE_PORTAGE_ROOT" ).split( ";" )
    else:
        rootDirs = []
    if len( rootDirs ) == 0:
        rootDirs = [ os.path.join( EmergeStandardDirs.emergeRoot(), "emerge", "portage" ) ]
    return rootDirs

def rootDir():
    # this function should return the portage directory, either the first set
    # via the environment, or the default one
    # keep this function for compat reasons
    return rootDirectories()[0]

def rootDirForCategory( category ):
    # this function should return the portage directory where it finds the
    # first occurance of a category or the default value
    for i in rootDirectories():
        if category and os.path.exists( os.path.join( i, category ) ):
            return i
    # as a fall back return the default even if it might be wrong
    return os.path.join( EmergeStandardDirs.emergeRoot(), "emerge", "portage" )

def rootDirForPackage( category, package ):
    # this function should return the portage directory where it finds the
    # first occurance of a package or the default value
    package, subpackage = getSubPackage( category, package )
    if category and package:
        if subpackage:
            for i in rootDirectories():
                if os.path.exists( os.path.join( i, category, package, subpackage ) ):
                    return i
        else:
            for i in rootDirectories():
                if os.path.exists( os.path.join( i, category, package ) ):
                    return i
    # as a fall back return the default even if it might be wrong
    return os.path.join( EmergeStandardDirs.emergeRoot(), "emerge", "portage" )

def getDirname( category, package ):
    """ return absolute pathname for a given category and package """
    _package, _subpackage = getSubPackage( category, package )
    if category and _package:
        if _subpackage:
            return os.path.join( rootDirForPackage( category, package ), category, _package, _subpackage )
        else:
            return os.path.join( rootDirForPackage( category, package ), category, package )
    else:
        return ""

def getFilename( category, package ):
    """ return absolute filename for a given category, package  """
    return os.path.join( getDirname( category, package ), "%s.py" % package  )

def getCategoryPackageVersion( path ):
    utils.debug( "getCategoryPackageVersion: %s" % path, 2 )
    head, fullFileName = os.path.split( path )
    for rd in rootDirectories():
        if head.startswith(rd):
            head = head.replace(rd + os.sep, "")
            break

    if len( head.split( os.sep ) )  == 3:
        category, _dummy, package = head.split( os.sep )
    else:
        head, package = os.path.split( head )
        head, category = os.path.split( head )

    package = os.path.splitext( fullFileName )[0]
    utils.debug( "category: %s, package: %s" % ( category, package ), 1 )
    return [ category, package ] # TODO: why a list and not a tuple?

def VCSDirs():
    return [ '.svn', 'CVS', '.hg', '.git' ]

class Portage(object):
    #cache for pacages
    _packageDict = OrderedDict()

    def __init__( self ):
        """ """
        self.categories = {}
        self.subpackages = {}
        self.portages = {}
        self._CURRENT_MODULE = ()#todo refactor package constructor
        self.ignores = set()
        if ("Portage", "PACKAGE_IGNORES") in emergeSettings:
            for p in emergeSettings.get("Portage","PACKAGE_IGNORES").split(";"):
                self.ignores.add(p)
            

    def addPortageDir( self, directory ):
        """ adds the categories and packages of a portage directory """
        if not os.path.exists( directory ):
            return

        categoryList = os.listdir( directory )

        # remove vcs directories
        for vcsdir in VCSDirs():
            if vcsdir in categoryList:
                categoryList.remove( vcsdir )
        if "__pycache__" in categoryList:
            categoryList.remove( "__pycache__" )

        dontBuildCategoryList = self.getDontBuildPackagesList( os.path.join( directory ) )

        self.portages[ directory ] = []
        for category in categoryList:
            if not os.path.isdir( os.path.join( directory, category ) ):
                continue

            self.portages[ directory ].append( category )

            packageList = os.listdir( os.path.join( directory, category ) )

            # remove vcs directories
            for vcsdir in VCSDirs():
                if vcsdir in packageList:
                    packageList.remove( vcsdir )
            if "__pycache__" in packageList:
                packageList.remove( "__pycache__" )

            dontBuildPackageList = self.getDontBuildPackagesList( os.path.join( directory, category ) )

            if not category in list(self.categories.keys()):
                self.categories[ category ] = []

            for package in packageList:
                if not os.path.isdir( os.path.join( directory, category, package ) ):
                    continue
                if not package in self.categories[ category ]:
                    _enabled = not category in dontBuildCategoryList and not package in dontBuildPackageList
                    self.categories[ category ].append( PackageObjectBase( category=category, package=package, enabled=_enabled ) )

                subPackageList = os.listdir( os.path.join( directory, category, package ) )

                # remove vcs directories
                for vcsdir in VCSDirs():
                    if vcsdir in subPackageList:
                        subPackageList.remove( vcsdir )
                if "__pycache__" in subPackageList:
                    subPackageList.remove( "__pycache__" )

                for subPackage in subPackageList:
                    if not os.path.isdir( os.path.join( directory, category, package, subPackage ) ) or subPackage in VCSDirs():
                        continue

                    dontBuildSubPackageList = self.getDontBuildPackagesList( os.path.join( directory, category, package ) )

                    if not subPackage in list(self.subpackages.keys()):
                        self.subpackages[ subPackage ] = []
                    if not subPackage in self.categories[ category ]:
                        _enabled = not category in dontBuildCategoryList and not package in dontBuildPackageList and not subPackage in dontBuildSubPackageList
                        self.categories[ category ].append( PackageObjectBase( category=category, subpackage=package, package=subPackage, enabled=_enabled ) )
                    self.subpackages[ subPackage ].append( category + "/" + package )


    def getCategory( self, package ):
        """ returns the category of this package """
        utils.debug( "getCategory: %s" % package, 2 )

        for cat in list(self.categories.keys()):
            if package in self.categories[ cat ]:
                utils.debug( "found: category %s for package %s" % ( cat, package ), 1 )
                return cat
        return False

    def isCategory( self, category ):
        """ returns whether a certain category exists """
        return category in list(self.categories.keys())

    def isPackage( self, category, package ):
        """ returns whether a certain package exists within a category """
        return package in self.categories[ category ]

    def isVirtualPackage( self, category, package ):
        """ check if that package is of VirtualPackageBase """
        if not self.isPackage( category, package ):
            return False
        mod = getPackageInstance(category,package)
        for baseClassObject in mod.__class__.__bases__:
            if baseClassObject.__name__ == 'VirtualPackageBase': return True
        return False

    def getDontBuildPackagesList( self, path ):
        """ get a list of packages from a dont_build file"""
        plist = []
        if os.path.exists( os.path.join( path, "dont_build.txt" ) ):
            with open( os.path.join( path, "dont_build.txt" ), "r" ) as f:
                for line in f:
                    if line.strip().startswith('#'): continue
                    if not line.strip() == "":
                        plist.append(line.strip())
        return plist

    def getAllPackages( self, category ):
        """returns all packages of a category except those that are listed in a file 'dont_build.txt' in the category directory
        in case the category doesn't exist, nothing is returned"""
        if self.isCategory( category ):
            plist = []
            for _p in self.categories[ category ]:
                if _p:
                    plist.append(_p.package)
            return plist
        else:
            return

    def getPackageInstance(self, category, package, buildtarget=None):
        """return instance of class Package from package file"""
        fileName =  getFilename( category, package )
        pack = None
        mod = None
        if fileName.endswith(".py") and os.path.isfile(fileName):
            if not fileName in self._packageDict:
                utils.debug( "module to import: %s" % fileName, 2 )
                if not os.path.isfile( fileName ):
                    try:
                        mod = builtins.__import__( fileName )
                    except ImportError as e:
                        utils.warning( 'import failed for module %s: %s' % (fileName, str(e)) )
                        mod =  None
                else:
                    modulename = os.path.basename( fileName )[:-3].replace('.', '_')
                    loader = importlib.machinery.SourceFileLoader(modulename, fileName)
                    mod = loader.load_module(modulename)
                if not mod is None:
                    self._CURRENT_MODULE  = ( fileName, category, package, mod )
                    pack = mod.Package( )
                    self._packageDict[ fileName ] = pack
                else:
                    raise PortageException("Failed to find package", category, package)
            else:
                pack = self._packageDict[ fileName ]
            return pack

    def getDefaultTarget( self, category, package ):
        """ returns the default package of a specified package """
        utils.debug( "getDefaultTarget: importing file %s" % getFilename( category, package ), 1 )
        if not ( category and package ):
            return dict()

        info = _getSubinfo( category, package )
        if not info is None:
            return info.defaultTarget
        else:
            return None

    def getMetaData( self, category, package ):
        """ returns all targets of a specified package """
        utils.debug( "getMetaData: importing file %s" % getFilename( category, package ), 1 )
        if not ( category and package ):
            return dict()
        info = _getSubinfo(  category, package  )
        if not info is None:
            tmpdict = dict()
            tmpdict['categoryName'] = info.category
            if not info.shortDescription == "":
                tmpdict['shortDescription'] = info.shortDescription
            if not info.description == "":
                tmpdict['description'] = info.description
            if not info.homepage == "":
                tmpdict['homepage'] = info.homepage
            tmpdict['withCompiler'] = info.options.package.withCompiler
            utils.debug( tmpdict, 2 )
            return tmpdict
        else:
            return {'withCompiler': True}

    def getAllTargets( self, category, package ):
        """ returns all targets of a specified package """
        utils.debug( "getAllTargets: importing file %s" % getFilename( category, package ), 1 )
        if not ( category and package ):
            return dict()
        info = _getSubinfo( category, package )
        if not info is None:
            tagDict = info.svnTargets
            tagDict.update( info.targets )
            utils.debug( tagDict, 2 )
            return tagDict
        else:
            return dict()

    def getAllVCSTargets( self, category, package ):
        """ returns all version control system targets of a specified package,
            excluding those which do contain tags """
        utils.debug( "getAllVCSTargets: importing file %s" % getFilename( category, package ), 1 )
        info = _getSubinfo(  category, package )
        if not info is None:
            tagDict = info.svnTargets
            for key in tagDict:
                utils.debug( '%s: %s' % ( key, tagDict[key] ), 2 )
            return tagDict
        else:
            return dict()

    def getUpdatableVCSTargets( self, category, package ):
        """ check if the targets are tags or not """
        targetDict = PortageInstance.getAllVCSTargets( category, package )
        retList = []
        for key in targetDict:
            url = targetDict[ key ]
            if url:
                sourceType = utils.getVCSType( url )
                if sourceType == "svn":
                    # for svn, ignore tags
                    if not url.startswith( "tags/" ) and not "/tags/" in url:
                        retList.append( key )
                elif sourceType == "git":
                    _, branch, tag = utils.splitVCSUrl( url )
                    if tag == "" and not branch.endswith("-patched"):
                        retList.append( key )
                elif not sourceType == "":
                    # for all other vcs types, simply rebuild everything for now
                    retList.append( key )
        return retList

    def getNewestVersion( self, category, package ):
        """ returns the newest version of this category/package """
        if( category == None ):
            raise PortageException( "Empty category", category, package )
        if not self.isCategory( category ):
            raise PortageException( "Could not find category", category, package )
        if not self.isPackage( category, package ):
            raise PortageException( "Could not find package", category, package )

        installed = InstallDB.installdb.getInstalledPackages(category, package )
        newest = PortageInstance.getDefaultTarget( category, package )

        for pack in installed:
            version = pack.getVersion()
            if utils.parse_version(newest) < utils.parse_version(version):
                newest = version
        return newest

    def getInstallables( self ):
        """ get all the packages that are within the portage directory """
        instList = list()
        for category in list(self.categories.keys()):
            for package in self.categories[ category ]:
                version = PortageInstance.getDefaultTarget( category, package.package )
                if version:
                    instList.append([category, package.package, version])
        return instList

# when importing this, this static Object should get added
PortageInstance = Portage()
for _dir in rootDirectories():
    PortageInstance.addPortageDir( _dir )

def getSubPackage( category, package ):
    """ returns package and subpackage names """
    """ in case no subpackage could be found, None is returned """
    if package in list(PortageInstance.subpackages.keys()):
        for entry in PortageInstance.subpackages[ package ]:
            cat, pac = entry.split("/")
            if cat == category: return pac, package
    return package, None



def getPackageInstance(category, package, buildtarget=None):
    """return instance of class Package from package file"""
    return PortageInstance.getPackageInstance(category, package, buildtarget)

def getDependencies( category, package, runtimeOnly = False ):
    """returns the dependencies of this package as list of strings:
    category/package"""

    package, subpackage = getSubPackage( category, package )
    if subpackage:
        utils.debug( "solving package %s/%s/%s %s" % ( category, subpackage, package,
                                                          getFilename( category, package ) ), 0 )
    else:
        utils.debug( "solving package %s/%s %s" % ( category, package, getFilename( category, package ) ), 0 )
        subpackage = package

    deps = []
    for pkg in [ subpackage ]:
        info = _getSubinfo(category, pkg)
        if not info is None:
            depDict = info.dependencies
            depDict.update( info.runtimeDependencies )
            if not runtimeOnly:
                depDict.update( info.buildDependencies )

            for line in list(depDict.keys()):
                (category, package) = line.split( "/" )
                version = PortageInstance.getNewestVersion( category, package )
                deps.append( [ category, package, version, depDict[ line ] ] )
    return deps

def parseListFile( filename ):
    """parses a csv file used for building a list of specific packages"""
    categoryList = []
    packageList = []
    infoDict = {}
    listFileObject = open( filename, 'r' )
    for line in listFileObject:
        if line.strip().startswith('#'): continue
        try:
            cat, pac, tar, plvl = line.split( ',' )
        except:
            continue
        categoryList.append( cat )
        packageList.append( pac )
        infoDict[ cat + "/" + pac ] = (tar, plvl)
    return categoryList, packageList, infoDict


def solveDependencies( category, package, version, depList, dep_type='both' , maxDetpth = -1 ):
    depList.reverse()
    if ( category == "" ):
        category = PortageInstance.getCategory( package )
        utils.debug( "found package in category %s" % category, 2 )
    if ( version == "" ):
        version = PortageInstance.getNewestVersion( category, package )
        utils.debug( "found package with newest version %s" % version, 2 )

    pac = DependencyPackage( category, package, version )
    depList = pac.getDependencies( depList, dep_type=dep_type, maxDetpth = maxDetpth )

    depList.reverse()
    return depList

def printTargets( category, package ):
    targetsDict = PortageInstance.getAllTargets( category, package )
    defaultTarget = PortageInstance.getDefaultTarget( category, package )
    if 'svnHEAD' in targetsDict and not targetsDict['svnHEAD']:
        del targetsDict['svnHEAD']
    targetsDictKeys = list(targetsDict.keys())
    targetsDictKeys.sort()
    for i in targetsDictKeys:
        if defaultTarget == i:
            print('*', end=' ')
        else:
            print(' ', end=' ')
        print(i)

def _getSubinfo( category, package  ):
    pack = getPackageInstance( category, package  )
    if pack:
        return pack.subinfo
    return None


def readChildren( category, package ):
    package, subpackage = getSubPackage( category, package )
    if subpackage:
        utils.debug( "solving package %s/%s/%s %s" % ( category,  package, subpackage, getFilename( category, subpackage ) ), 2 )
        subinfo = _getSubinfo( category, subpackage  )
    else:
        utils.debug( "solving package %s/%s %s" % ( category, package, getFilename( category, package ) ), 2 )
        subinfo = _getSubinfo( category, package  )

    if subinfo is None:
        return OrderedDict(), OrderedDict()

    runtimeDependencies = subinfo.runtimeDependencies
    buildDependencies = subinfo.buildDependencies

    commonDependencies = subinfo.dependencies
    runtimeDependencies.update(commonDependencies)
    buildDependencies.update(commonDependencies)

    return runtimeDependencies, buildDependencies

def isPackageUpdateable( category, package ):
    utils.debug( "isPackageUpdateable: importing file %s" % getFilename( category, package ), 2 )
    subinfo = _getSubinfo( category, package )
    if not subinfo is None:
        if len( subinfo.svnTargets ) == 1 and not subinfo.svnTargets[ list(subinfo.svnTargets.keys())[0] ]:
            return False
        return len( subinfo.svnTargets ) > 0
    else:
        return False

def alwaysTrue( *dummyArgs):
    """we sometimes need a function that always returns True"""
    return True

def getHostAndTarget( hostEnabled, targetEnabled ):
    """used for messages"""
    msg = ""
    if hostEnabled or targetEnabled:
        msg += "("
        if hostEnabled:
            msg += "H"
        if hostEnabled and targetEnabled:
            msg += "/"
        if targetEnabled:
            msg += "T"
        msg += ")"
    return msg

def printCategoriesPackagesAndVersions( lines, condition, hostEnabled=alwaysTrue, targetEnabled=alwaysTrue ):
    """prints a number of 'lines', each consisting of category, package and version field"""
    def printLine( cat, pack, ver, hnt="" ):
        catlen = 25
        packlen = 25
        print(cat + " " * ( catlen - len( cat ) ) + pack + " " * ( packlen - len( pack ) ) + ver, hnt)

    printLine( 'Category', 'Package', 'Version' )
    printLine( '--------', '-------', '-------' )
    for category, package, version in lines:
        if condition( category, package, version ):
            printLine( category, package, version )

def printInstallables():
    """get all the packages that can be installed"""
    printCategoriesPackagesAndVersions( PortageInstance.getInstallables(), alwaysTrue )


def getPackagesCategories(packageName, defaultCategory = None):
    utils.debug( "getPackagesCategories for package name %s" % packageName, 1 )
    if defaultCategory is None:
        defaultCategory = emergeSettings.get("General","EMERGE_DEFAULTCATEGORY","kde")

    packageList, categoryList = [], []
    if len( packageName.split( "/" ) ) == 1:
        if PortageInstance.isCategory( packageName ):
            utils.debug( "isCategory=True", 2 )
            packageList = PortageInstance.getAllPackages( packageName )
            categoryList = [ packageName ] * len(packageList)
        else:
            utils.debug( "isCategory=False", 2 )
            if PortageInstance.isCategory( defaultCategory ) and PortageInstance.isPackage( defaultCategory, packageName ):
                # prefer the default category
                packageList = [ packageName ]
                categoryList = [ defaultCategory ]
            else:
                if PortageInstance.getCategory( packageName ):
                    packageList = [ packageName ]
                    categoryList = [ PortageInstance.getCategory( packageName ) ]
    elif len( packageName.split( "/" ) ) == 2:
        [ cat, pac ] = packageName.split( "/" )
        if PortageInstance.isCategory( cat ):
            categoryList = [ cat ]
        else:
            return packageList, categoryList
        if len( categoryList ) > 0 and PortageInstance.isPackage( categoryList[0], pac ):
            packageList = [ pac ]
        if len( categoryList ) and len( packageList ):
            utils.debug( "added package %s/%s" % ( categoryList[0], pac ), 2 )
    else:
        utils.error( "unknown packageName" )

    return packageList, categoryList


