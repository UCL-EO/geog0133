
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


files=['prc.dat','usa.dat','ind.dat','rus.dat','jap.dat']
getfiles(files=files)

data = {}
population = {}
# get columns 0,1 and 7 of the file
# which are Year, Total Fossil-Fuel Emissions (thousand metric tons of carbon)
# and Per Capita Emission Rate
# but convert '.' in col 7 to nan (see header of file)
# skip the 1st 30 rows as comments
plt.figure(1)
for file in files:
    data[file] = np.loadtxt(file,skiprows=30,comments='*',usecols=[0,1,7],\
		converters={7:lambda x:(x=='.' and np.nan) or float(x)})
    # infer population
    population[file] = 1000.*data[file][:,1]/data[file][:,2]
    plt.plot(data[file][:,0],data[file][:,2],'-',label=file.split('.')[0])
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),\
		ncol=3, fancybox=True, shadow=True)
plt.xlabel('year')
plt.ylabel('per capita C emissions')
plt.savefig('figures/perCapitaEmissions.png')

plt.figure(2)
# plot population
for file in files:
    plt.plot(data[file][:,0],population[file],'-',label=file.split('.')[0])
plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),\
                ncol=3, fancybox=True, shadow=True)
plt.xlabel('year')
plt.ylabel('population')
plt.savefig('figures/population.png')



# now find the trends in population and per capita emissions rates
# since 1995
# and extrapolate to 2020

from scipy import polyval, polyfit
plt.figure(3)

print ('2020 per captia emissions estimates per country (metric tons of carbon per capita)')
print ('estimate based on linear extrapolation for data from 1995 to 2008')


for file in files:
    year = data[file][:,0]
    perCap = data[file][:,2]
    pop = population[file]
    # pick the data for the years we want
    ww = np.where((year >= 1995) * (year <=2008)) 
    # linear interpolation info the 1 can be changed 
    # to provide other orders of polynomial
    (ar,br)=polyfit(year[ww],perCap[ww],1)
    perCapNew = polyval([ar,br],np.arange(1995,2021))
    print (file.split('.')[0],perCapNew[-1])
    plt.plot(data[file][:,0],data[file][:,2],'-',label=file.split('.')[0])
    plt.plot(np.arange(1995,2021),perCapNew,'b.')

plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),\
                ncol=3, fancybox=True, shadow=True)
plt.xlabel('year')
plt.ylabel('per capita C emissions')
plt.savefig('figures/percap2.png')


