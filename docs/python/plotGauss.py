def plotGauss(mean_0,mean_1,sd_0,sd_1,rho,vminmax=None,\
                file=None,title=None):
   # Import some libraries, in case you haven't yet imported them
   import matplotlib.pyplot as plt
   import numpy as np

   # size of grid
   N = 1000
   # generate grid (NB -1 to 1 here)
   coords = 2. * (np.arange(N+1)/float(N) - 0.5)
   x0, x1 = np.meshgrid(coords,coords)
   x = np.array([x0, x1])
   dx = np.array([x0[0,1] - x0[0,0], x1[1,0] - x1[0,0]])
   grid = dx[0] * dx[1]

   # set B
   b01 = b10 = rho * sd_0 * sd_1
   b00 = sd_0**2
   b11 = sd_1**2
   B = np.matrix([[b00,b01],[b10,b11]])
   # set xb: the mean
   xb = np.array([mean_0,mean_1])

   xxb = np.zeros_like(x)
   for i in range(xb.shape[0]): xxb[i,...] = xb[i]
   e = x - xxb

   n = np.shape(B)[0]
   # inverse of B
   BI = B.I
   # scaling term
   scale_1 = (2.*np.pi)**(n/2) * np.sqrt(np.linalg.det(B))
   gauss = np.exp(-0.5 * ((e[0,...] * BI[0,0] + e[1,...] * BI[0,1])* e[0,...]     \
                          + (e[0,...] * BI[1,0] + e[1,...] * BI[1,1])* e[1,...])) \
                          / scale_1

   # check integral
   print ('integral of Gaussian:',gauss.sum() * grid)

   # plot
   plt.clf()
   if title:
       plt.title(title)
   #if len(list(vminmax)):
   #    plt.imshow(gauss,origin='lower',interpolation='nearest', \
   #                    vmin=vminmax[0],vmax=vminmax[1],\
   #                    extent=[x0.min(),x0.max(),x1.min(),x1.max()])
   #else:
   plt.imshow(gauss,origin='lower',interpolation='nearest', \
                       extent=[x0.min(),x0.max(),x1.min(),x1.max()])
   plt.colorbar()
   if file == None:
       plt.show()
   else:
       plt.savefig(file)

