
import numpy as np
import pylab as plt

def CO2InternalLeaf(atmosphericCO2,\
	airTemperatureK_0 = 25.+273.15,\
	airPressure_0 = 1.01325e5,\
	atmosphericCO2_0 = 355.,\
	C3Type=True):
    '''
    Calculate internal leaf CO2 concentration (ppm) Ci 
    from knowledge of atmosphericCO2 (ppm)
    assuming that Ci/atmosphericCO2 is constant.

    This follows  Knorr (1997) (Ch2, p49-50) but
    NB 1.6*8.3145*1000*(25+273.15)/(1.*10^5)/0.883
    = 44.92 ~= 45 which is what Knorr states
    but that is for std pressure, not 1 atm
    which is what we prefer to use

    parameters:

    atmosphericCO2 : ppm
        Actual atmospheric CO2 conc. 

    optional parameters:

    airTemperatureK_0 : K
	fixed air temperature for assumed relationship

    airPressure_0 : Pa (STP = 1e5 Pa, but 1 atm = 1.01325e5 Pa)
	fixed air pressure for assumed relationship

    C3Type : True (C3); False (C4)

    atmosphericCO2_0 : ppm
        fixed atmospheric CO2 conc. for assumed relationship
    
    '''
    R = 8.3145 # gas constant, J/mol K
    if C3Type == True:
        scaling = 0.883
    else:
        scaling = 333.

    deltaCO2 = 1.6 *1e3 *  R * airTemperatureK_0 \
                / airPressure_0 / scaling
    CO2ratio = 1 - deltaCO2/atmosphericCO2_0
    Ci0 = atmosphericCO2_0 * CO2ratio
    return Ci0



def canopyConductance(maxPhotosytheticRate,\
        airTemperatureC=25.,\
        airPressure=1.01325e5,\
        C3Type=True,\
        atmosphericCO2=355.):
    '''
    maxPhotosytheticRate : mol(CO2)m-2s-1
    airTemperatureC : C
    airPressure : Pa (STP = 1e5 Pa, but 1 atm = 1.01325e5 Pa)
    C3Type : True (C3); False (C4);
    atmosphericCO2 : ppm

    '''
    R = 8.3145 # gas constant, J/mol K
    airTemperatureK = airTemperatureC + 273.15

    Ci0 = CO2InternalLeaf(atmosphericCO2)

    Gc0 = maxPhotosytheticRate * 1.6 *1e3 *  R * airTemperatureK \
                /((atmosphericCO2 - Ci0)*airPressure)
    return Gc0



airTemperatureC = np.arange(10,40).astype(float)
ratio = canopyConductance(1.0,airTemperatureC=airTemperatureC)

plt.plot(airTemperatureC,ratio)
plt.xlabel('air temperature (C)')
plt.ylabel('ratio of Gc0 to Ac0')
plt.savefig('figures/stomatalAssimRat.png')





atmosphericCO2 = np.arange(330,500,10)
ratio = canopyConductance(1.0,atmosphericCO2=atmosphericCO2)

plt.plot(atmosphericCO2,ratio)
plt.xlabel('Atmospheric CO2 conc (ppm)')
plt.ylabel('ratio of Gc0 to Ac0')
plt.savefig('figures/stomatalAssimRat2.png')

