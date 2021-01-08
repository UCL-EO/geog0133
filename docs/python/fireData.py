#! /usr/bin/env python
import numpy as np
import gdal
import gdalnumeric

def getModis(data,options):
    xoff=options.col
    yoff=options.row
    xsize=options.ncols
    ysize=options.nrows
    verbose=options.verbose
    datadir=options.datadir
    data['mask'] = []
    data['vza'] = []
    data['sza'] = []
    data['raa'] = []
    data['reflectance'] = []
    data['doy'] = []
    for t in range(len(data['date'])):
        print (t,'/',len(data['date']),data['date'][t],':')
        try:
            qamaskFull,vzaFull,szaFull,raaFull,refl = getModist(data,t,datadir=datadir,\
                                                           xsize=xsize,ysize=ysize,\
                                                           xoff=xoff,yoff=yoff)
            if verbose:
                print (t,data['date'][t],qamaskFull,refl[0,0])

            data['doy'].append(data['date'][t])
            data['mask'].append(qamaskFull)
            data['vza'].append(vzaFull)
            data['sza'].append(szaFull)
            data['raa'].append(raaFull)
            data['reflectance'].append(refl)
        except:
            if verbose:
                print (t,data['date'][t],'No files')
    print (' ')
    data['doy'] = np.array(data['doy'])
    data['mask'] = np.array(data['mask'])
    data['vza'] = np.array(data['vza'])
    data['sza'] = np.array(data['sza'])
    data['raa'] = np.array(data['raa'])
    data['reflectance'] = np.array(data['reflectance'])
    data['wavebands'] = np.array([ float(i) for i in "659 865 470  555 1240 1640 2130".split()])    
    return data

def getModist(data,t,xoff=0,yoff=0,xsize=2400,ysize=2400,datadir='data'):
    qcstr = '8 72 136 200 1032 1288 2056 2120 2184 2248'
    qc = np.array([int(i) for i in qcstr.split()])

    # angle data
    bad = -32767
    ds = gdal.Open(data['angles'][t])
    sds_md = ds.GetMetadata('SUBDATASETS')
    xsize2 = int(np.max([xsize/2,1]))
    xoff = int(xoff)
    yoff = int(yoff)
    ysize2 = int(np.max([ysize/2,1]))
    saz = gdalnumeric.LoadFile(sds_md['SUBDATASET_1_NAME'],\
                               xoff=xoff/2,yoff=yoff/2,xsize=xsize2,ysize=ysize2)
    szen = gdalnumeric.LoadFile(sds_md['SUBDATASET_2_NAME'],\
                               xoff=xoff/2,yoff=yoff/2,xsize=xsize2,ysize=ysize2)
    vaz = gdalnumeric.LoadFile(sds_md['SUBDATASET_3_NAME'],\
                               xoff=xoff/2,yoff=yoff/2,xsize=xsize2,ysize=ysize2)
    vzen = gdalnumeric.LoadFile(sds_md['SUBDATASET_4_NAME'],\
                               xoff=xoff/2,yoff=yoff/2,xsize=xsize2,ysize=ysize2)
    anglemask = ~((saz == bad) * (szen == bad) * (vaz == bad) * (vzen==bad))
    # qa data
    del ds
    ds = gdal.Open(data['qa'][t])
    sds_md = ds.GetMetadata('SUBDATASETS')
    qa = gdalnumeric.LoadFile(sds_md['SUBDATASET_1_NAME'],\
                               xoff=xoff/2,yoff=yoff/2,xsize=xsize2,ysize=ysize2)
    qamask = anglemask*0
    for i in range(len(qc)): qamask = qamask | (qa == qc[i])
    qamask = qamask * anglemask
    #if qamask.sum(): 
    #    import pdb
    #    pdb.set_trace()
    # expand 
    qamaskFull = np.zeros([xsize,ysize]).astype(bool)
    vzaFull = np.zeros_like(qamaskFull).astype(float)
    szaFull = np.zeros_like(qamaskFull).astype(float)
    raaFull = np.zeros_like(qamaskFull).astype(float)
    del ds
    del qa
    for i in [0,1]: 
        for j in [0,1]: 
            qamaskFull[i::2,j::2] = qamask
            vzaFull[i::2,j::2] = 0.01*vzen
            szaFull[i::2,j::2] = 0.01*szen
            raaFull[i::2,j::2] = 0.01*(saz - vaz)
    # refl data
    bad = -28672
    ds = gdal.Open(data['refl'][t])
    sds_md = ds.GetMetadata('SUBDATASETS')
    refl = []
    for i in range(1,8):
        r = gdalnumeric.LoadFile(sds_md['SUBDATASET_%d_NAME'%i],\
                               xoff=xoff,yoff=yoff,xsize=xsize,ysize=ysize)
        qamaskFull = qamaskFull * (r != bad) * (r > 0)
        refl.append(r/10000.)
    del ds
    for i in range(7):
        r = refl[i]
        r[~qamaskFull] = 0.
        refl[i] = r
    return np.array(qamaskFull),np.array(vzaFull),np.array(szaFull),\
                                np.array(raaFull),np.array(refl)


def getrefl():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-r", "--row", dest="row",\
            action="store",type='int',help="starting row (y)",default=100)
    parser.add_option("-c", "--col", dest="col",\
            action="store",type='int',help="starting column (x)",default=100)
    parser.add_option("--nrow", "--nrows", dest="nrows",\
            action="store",type='int',help="number of rows (y)",default=1)
    parser.add_option("--ncol","--ncols", dest="ncols",\
            action="store",type='int',help="number of columns (x)",default=1)
    parser.add_option("-f", "--file", dest="file",\
            action="store",type='string',help="Name for output data file",default=None)
    parser.add_option("-p","--plot",action="store_true", dest="plot")
    parser.add_option("--plotfile",dest="plotfile",\
            action="store",type='string',help="Name for plotfile",default=None)
    parser.add_option("-v","--verbose",action="store_true", dest="verbose")
    parser.add_option("-d", "--datadir", dest="datadir",\
            action="store",type='string',help="Name for input data directory",default=None)


    (options, args) = parser.parse_args()
    # directory for data files
    base = '/data/geospatial_20/plewis/geogg124'
    # list of filenames
    if options.datadir == None:
        options.datadir = base + '/data'
    # get all of the files & work out the dates
    import glob
    Rdata = glob.glob(options.datadir + '/*GHK*hdf')
    Adata = glob.glob(options.datadir + '/*GGAD*hdf')
    Qdata = glob.glob(options.datadir + '/*GST*hdf')
    Rdates = np.array([(i.split('/')[-1]).split('.')[1][-3:] for i in Rdata])
    Adates = np.array([(i.split('/')[-1]).split('.')[1][-3:] for i in Adata])
    Qdates = np.array([(i.split('/')[-1]).split('.')[1][-3:] for i in Qdata])
    alldates = np.append(Rdates,Adates)
    alldates = np.append(alldates,Qdates)
    alldates = np.unique(alldates)
    alldates.sort()
    # now for each date, get all 3 files
    date = []
    angles = []
    qa = []
    refl = []
    for d in alldates:
        all = glob.glob(options.datadir+ '/MOD*.A????%s.*hdf'%d)
        all.sort()
        if len(all) ==3:
            date.append(int(d))
            refl.append(all[0])
            qa.append(all[1])
            angles.append(all[2])        

    data = {'date':np.array(date),\
        'angles':np.array(angles),\
        'qa':np.array(qa),\
        'refl':np.array(refl)}

    data = getModis(data,options)
   
    ds = gdal.Open(options.datadir + '/MODIS-LC')
    landCover = ds.GetRasterBand(1).ReadAsArray(options.col,options.row,\
                                              options.ncols,options.nrows)

    lcovers = \
    "Water,Evergreen Needleleaf forest,Evergreen Broadleaf forest," + \
    "Deciduous needleleaf forest,Deciduous broadleaf forest,Mixed Forests," + \
    "Closed shrublands,Open shrublands,Woody Savannas,Savannas,Grasslands," + \
    "Permanent wetlands,Croplands,Urban and built-up," + \
    "Cropland/natural vegetation mosaic,Permanent snow and ice," + \
    "Barren or sparsely vegetated"
    landCoverLUT = lcovers.split(',')
   
    ds = gdal.Open(options.datadir + '/activeFire_2003') 
    activeFire = ds.GetRasterBand(1).ReadAsArray(options.col,options.row,\
                                              options.ncols,options.nrows)
     
    # PLOT
    if options.plot:
        if options.verbose:
            print ('plotting ...')
        ds = data['reflectance'].shape
        nt = ds[0]
        nbands = ds[1]
        npixels = ds[2] * ds[3]
        import pylab as plt
        mask = data['mask'][:,0,0]
        f = plt.figure() 
        size = f.get_size_inches()
        f.set_figheight(size[1]*2.)
        if mask.sum():
            for i in range(nbands):
                this = data['reflectance'][:,i,0,0]
                doy = data['doy']
                plt.subplot(nbands,1,i+1)
                plt.plot(doy[mask],this[mask],'o')
                plt.ylabel('r %d'%(int(data['wavebands'][i])))
        plt.xlabel('doy')
        try:
            plt.subplot(nbands,1,1)
            plt.title('(%d,%d) %s (fire %d)'%(options.col,options.row,\
                                      landCoverLUT[landCover[0,0]],\
                                      activeFire[0,0]))
        except:
            pass
        if options.plotfile:
           if options.verbose:
               print (' ... to',options.plotfile)
           plt.savefig(options.plotfile)
        else:
           plt.show()
    # output pickle file
    if options.file != None:
        if options.verbose:
            print ('saving data to',options.file)
        np.savez(options.file,doy=data['doy'],\
                             angles=data['angles'],\
                             qa=data['qa'],\
                             landcover=landCover,\
                             landCoverLUT=landCoverLUT,\
                             activeFire=activeFire,\
                             wavebands=data['wavebands'],\
                             mask=data['mask'],\
                             vza=data['vza'],\
                             sza=data['sza'],\
                             raa=data['raa'],\
                             refl=data['refl'],\
                             reflectance=data['reflectance'])

def main():
    getrefl()

if __name__ == "__main__":
    main()

