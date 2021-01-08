import numpy as np
import pylab as plt

def getfiles(files=['usa.dat','prc.dat'],server='cdiac.ornl.gov',dir='pub/trends/emissions'):
    '''
    Retrieve some files (list) from the directory dir on the ftp server
    '''
    from ftplib import FTP

    # get some files from the server
    ftp = FTP(server)
    ftp.login()
    ftp.cwd(dir)

    for file in files:
        ftp.retrbinary('RETR '+file,open(file, 'wb').write)
    ftp.quit()





def cropGrowth()
