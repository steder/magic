#!/usr/bin/env python
"""
Nosy - Script to monitor changes to *.py files and rerun tests
"""

import glob,os,stat,time,sys

COMMAND= "nosetests"

EXTENSION_GLOBS = ["*.py",
              "*.kid",
              "*.psp",
              ]
EXTENSIONS=[".py",
            ".kid",
            ".psp",
            ]

def getPythonPath():
    """
    Function that returns a PYTHONPATH extended to include
    the directory from which this script is run.  The assumption
    being that you run nosy.py from within your SVN checkout.
    """
    python_path = os.environ.get("PYTHONPATH","")
    
    if os.path.basename(os.path.abspath(os.curdir)) == "Test":
        new_python_path = os.path.pathsep.join([
            python_path,os.path.normpath("../Lib/external/SQLObject-compat"),
            os.path.normpath("../Lib/external"),
            os.path.normpath("../Lib"),
            ])
    else:
        new_python_path = os.path.pathsep.join([
            python_path,os.path.normpath("./Lib/external/SQLObject-compat"),
            os.path.normpath("./Lib/external"),
            os.path.normpath("./Lib"),
            ])
        
    return new_python_path

def checkSum():
    """
    Return a long which can be used to know if any files with
    the given extensions have changed.

    Only looks in the current directory.
    """
    val = 0
    for ext in EXTENSION_GLOBS:
        for f in glob.glob (ext):
            stats = os.stat(f)
            val += stats[stat.ST_SIZE] + stats[stat.ST_MTIME]
    return val

def checkSumHelper(arg, dirname, fnames):
    """
    Called at each level of the checkSumWalk

    Simply filters the list of files at that level to
    only the set of files with extensions matching the
    defined EXTENSIONS global and then evaluates the
    a simple checksum at each level.

    Arg is a simple accumulator.
    """
    val = 0
    files = [name for name in fnames if os.path.splitext(name)[1] in EXTENSIONS]
    for file in files:
        absFile = os.path.join(dirname,file)
        try:
            stats = os.stat(absFile)
        except OSError,e:
            # This is to skip over temporary files or files
            # nosy doesn't have permission to access
            # print "Nosy: skipping file %s with error %s"%(absFile,e)
            continue
        val += stats[stat.ST_SIZE] + stats[stat.ST_MTIME]
    arg.append(val)
    return

def checkSumWalk(top=".", func=checkSumHelper):
    """
    Recursive walk of a directory structure

    Computes checksum at each level using a helper function
    """
    values = []
    os.path.walk( top, checkSumHelper, values )
    return sum(values)

def getCommand(path="", args=""):
    command = COMMAND
    if path:
        command = " ".join(["PYTHONPATH=$PYTHONPATH%s"%(path), command])
    if args:
        command = " ".join([command, "--exe", "--nologcapture",args])
    return """bash -c '%s'""" % command

def main():
    """
    The Nosy mainloop
    """
    path = getPythonPath()
    args = " ".join( sys.argv[1:] )
    command = getCommand(path, args)
    
    val=checkSumWalk()
    print "Nosy starting with: %s"%(command)
    print command
    os.system(command)
    try:
        while (True):
            check_sum = checkSumWalk()
            if check_sum != val:
                print "Nosy detected a change and is rerunning tests with: %s"%(command)
                val=check_sum
                os.system(command)
            time.sleep(1)
    except KeyboardInterrupt:
        print "Exiting Nosy..."
        
if __name__=="__main__":
    main()
