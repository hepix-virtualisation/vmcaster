class uploaderDcap:
    def __init__(self):
        self.remotePrefix = None
    def upload(self,localpath,remotepath):
        print "prefix = %s" %( self.remotePrefix)
        print (self,localpath,remotepath)

def runpreloadcommand(cmd,timeout,preload):
    newenv = dict(os.environ)
    newenv["LD_PRELOAD"] = preload
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=newenv)
    processRc = None
    handleprocess = True
    counter = 0
    stdout = ''
    stderr = ''
    while handleprocess:
        counter += 1
        time.sleep(1)
        cout,cerr = process.communicate()
        stdout += cout
        stderr += cerr
        process.poll()
        processRc = process.returncode
        if processRc != None:
            break
        if counter == timeout:
            os.kill(process.pid, signal.SIGQUIT)
        if counter > timeout:
            os.kill(process.pid, signal.SIGKILL)
            processRc = -9
            break
    
    return (processRc,stdout,stderr)

def gsiDcapCopy(src,dest,timeout = 60):
    cmd = "dccp -C 3000 -d 2 -A %s %s" % (src,dest)
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    processRc = None
    handleprocess = True
    counter = 0
    stdout = ''
    stderr = ''
    while handleprocess:
        counter += 1
        time.sleep(1)
        cout,cerr = process.communicate()
        stdout += cout
        stderr += cerr
        process.poll()
        processRc = process.returncode
        if processRc != None:
            break
        if counter == timeout:
            os.kill(process.pid, signal.SIGQUIT)
        if counter > timeout:
            os.kill(process.pid, signal.SIGKILL)
            processRc = -9
            break
    if processRc != 0:
        print cmd
    return (processRc,stdout,stderr)
