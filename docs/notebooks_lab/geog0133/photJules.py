import numpy as np
import pylab as plt
#import bethy_fapar  as fapar  

class photosynthesis():

    def __init__(self,datashape=None):
        '''
        Class initialisation and setup of parameters
        '''
        if datashape == None:
            self.data = np.zeros([100])
            self.Tc = np.ones([100])*25
            self.C3 = np.ones([100]).astype(bool)
            self.Ipar = (np.arange(100)/100.) * 2000. * 1e-6
            self.Lcarbon = np.ones([100]) * 1
            self.Rcarbon = np.ones([100]) * 1
            self.Scarbon = np.ones([100]) * 1
            self.pft = np.array(['C3 grass']*100)

        # zero C in K
        self.zeroC = 273.15
        # gas constant J mol-1 K-1
        self.R_gas = 8.314

        # oxygen concentration
        self.Ox = 0.21 # mol(O2)mol(air)-1
        self.O2 = 0.23 # Atmospheric concentration of oxygen (kg O2/kg air)
        # energy content of PAR quanta 
        self.EPAR = 220. # kJmol-1
        # ratio of dark respiration to PVM at 25 C
        self.FRDC3 = 0.011
        self.FRDC4 = 0.042
        # scaling for GammaStar 
        self.GammaStarScale = 1.7e-6

        #  Effective quantum efficiency C4
        self.ALC4 = 0.04
        # Curvature parameter (C4)
        self.Theta = 0.83

        self.molarMassAir_kg = 28.97e-3
        self.molarMassCO2_kg = 44.011e-3

        self.co2SpecificGravity = self.molarMassCO2_kg/self.molarMassAir_kg

        self.variables()
        self.defaults()
        self.initialise()

    def test1(self):
        '''
        low light, span a temperature range, normal CO2
        '''
        self.Ipar = np.ones_like(self.data) * 200. * 1e-6
        self.co2_ppmv = 390.
        self.Tc = np.arange(100) - 30.
        self.initialise()
        self.defaults()

        self.photosynthesis()
        
        plt.clf()
        plt.plot(self.Tc,self.Wc * 1e6,label='Wc')
        plt.plot(self.Tc,self.Ws * 1e6,label='Ws')
        plt.plot(self.Tc,self.We * 1e6,label='We')
        plt.plot(self.Tc,self.W * 1e6,label='W')
        plt.legend()

    def photosynthesis(self):
        '''
        Uses:
            self.Tc      : canopy (leaf) temperature (C)
            self.C3      : array of True ('C3') or False ('C4')
            self.Ipar    : incident PAR (mol m-2 s-1)

            self.Lcarbon   : leaf C pool (kg C m-2)
            self.Rcarbon   : root C pool (kg C m-2)
            self.Scarbon   : respiring stem C pool (kg C m-2)

        '''
        self.leafPhotosynthesis() 
        self.canopyPhotosynthesis()
 
    def variables(self):
        '''
        Set some items that might be driven from a control file

        Generates:
            self.theta   : mean soil moisture concentration in the root zone,
            self.thetac  : Critical volumetric SMC (cubic m per cubic m of soil)
            self.thetaw  : Volumetric wilting point (cubic m per cubic m of soil)
        '''
        self.thetaw = 0.136328
        self.thetac = 0.242433
        self.theta = np.ones_like(self.data)
        self.m_air = 28.966
        self.co2_ppmv = 383.

    def initialise(self):
        '''
        Initialise some items that might be driven from a control file

        Uses:
            self.data  : data sizing array

        Generates:
            self.theta   : mean soil moisture concentration in the root zone,
            self.co2c    : Canopy level CO2 concentration (kg CO2/kg air).
            self.pstar   : Surface pressure (Pa)
            self.m_co2   : molecular weight of CO2
            self.m_air   : molecular weight of dry air
        '''
        self.m_co2 = self.m_air * self.epco2
        self.co2_mmr = self.co2_ppmv * self.m_co2 / self.m_air * 1.0e-6
        self.co2c = self.co2_mmr*1.

    def defaults(self):
        '''
        Uses:
            self.C3    : array of True ('C3') or False ('C4')
            self.Tc    : canopy (leaf) temperature (C)

        Generates:
            self.data  : data sizing array

            self.epco2   : Ratio of molecular weights of CO2 and dry air.
            self.epo2    : Ratio of molecular weights of O2 and dry air.
            self.Oa      : Partial pressume of O2 in the atmosphere

            self.ne      : constant for Vcmax (mol CO2 m-2 s-1 kg C (kg N)-1)
            self.Q10_leaf: Q10 dependence leaf
            self.Q10_rs  : Q10 dependence rs
            self.Q10_Kc  : Q10 dependence Kc: CO2
            self.Q10_Ko  : Q10 dependence Ko: O2
            self.Kc      : Michaelis-Menten paramemeter for CO2
            self.Ko      : Michaelis-Menten paramemeter for O2
            self.beta1   : colimitation coefficients
            self.beta2   : colimitation coefficients

            self.nl      : leaf nitrogen
            self.Gamma   : CO2 compensation point in the absence of mitochindrial
                           respiration (Pa)
            self.tau     : Rubisco specificity for CO2 relative to O2
            self.kappao3 : ratio of leaf resistance for O3 to leaf resistance to water vapour

            self.Tupp    : PFT-specific parameter ranges: upper (C)
            self.Tlow    : PFT-specific parameter ranges: lower (C)
            self.Fo3_crit: critical value of Ozone stress limitation
            self.a       : Ozone factor
            self.k       : PAR extinction coefficient
            self.alpha   : quantum efficiency mol CO2 [mol PAR photons]-1
            self.omega   : leaf PAR scattering coefficient
            self.fdr     : dark respiration coefficient
            self.rg      : growth respiration coefficient
            self.n0      : top leaf N concentration (kg N [kg C]-1)
            self.nrl     : ratio of N conc in roots and leaves
            self.nsl     : ratio of N conc in stems and leaves
            
            self.Vcmax25 : maximum rate of carboxylation of Rubisco (mol CO2 m-2 s-1)
                           at 25 C
            self.Vcmax   : maximum rate of carboxylation of Rubisco (mol CO2 m-2 s-1)
            self.fc      : temperature factors for Vcmax
            self.aws     : ratio of total stem C to respiring stem C

            self.gamma0  : minimum leaf turnover rate (360 days-1)
            self.dm      : rate of change of turnover with soil moisture
                           stress (360 days-1)
            self.dt      : rate of change of turnover with T (360 days K)-1
            self.moff    : threshold soil mositure stress
            self.toff    : threshold temperature (K)
            self.gammap  : rate of leaf growth (360 days)-1

            self.gammav  : disturbance rate (360 days-1)
            self.gammar  : root biomass turnover rate (360 days-1)
            self.gammaw  : woody biomass turnover rate (360 days-1)
            self.Lmax    : maximum LAI
            self.Lmin    : minimum LAI

            self.sigmal  : specific leaf density (kg C m-2 per unit LAI)
            self.awl     : allometric coefficient
            self.bwl     : allometric exponent

            self.etasl   : ratio of live stemwood to LAI * height
            self.dt      : time interval
            self.ratio   : Ratio of leaf resistance for CO2 to leaf resistance for H2O.
            self.glmin   : minimum stomatal conductance
        '''
        self.dt = 1.0
        self.data = np.zeros_like(self.C3).astype(float)
        self.glmin =  1.0e-10
        self.pstar  = 101e3

        self.epco2 = 1.5194  
        self.epo2  = 1.106
        self.ratio=1.6       

        #==============Jules/ triffid parameters
        # default self.Q10_leaf, self.Q10_rs etc.
        self.Q10_leaf = 2.0
        self.Q10_rs = 0.57
        self.Q10_Kc = 2.1
        self.Q10_Ko = 1.2


        # leaf nitrogen/Vcmax terms
        # default for self.ne mol CO2 m-2 s-1 kg C (kg N)-1
        self.n0 = np.zeros_like(self.data) + 0.060
        self.n0[self.pft == 'Broadleaf tree'] = 0.046
        self.n0[self.pft == 'Needleleaf tree'] = 0.033
        self.n0[self.pft == 'C3 grass'] = 0.073

        self.ne = 0.0008*np.ones_like(self.data)
        self.ne[~self.C3] = 0.0004
        self.nl = self.n0*np.ones_like(self.data)

        # CO2 compensation point
        self.Oa = 0.21 * self.pstar # assuming 21% of atmosphere is O2

        self.tau = 2600.*self.Q10_rs**(0.1*(self.Tc-25.))
        self.Gamma = (self.Oa/(2.*self.tau))*np.ones_like(self.data)
        self.Gamma[~self.C3] = 0.

        # colimitation coefficients: 
        self.beta1 = 0.83
        self.beta2 = 0.93
        # use larger values here
        self.beta1 = 0.999
        self.beta2 = 0.999

        # ratio of leaf resistance for O3 to leaf resistance to water vapour
        self.kappao3 = 1.67

        # leaf T limits (C)
        self.Tupp = np.zeros_like(self.data) + 36.0
        self.Tlow = np.zeros_like(self.data)
        self.Tlow[self.pft == 'Needleleaf tree'] = -10.0
        self.Tlow[self.pft == 'C4 grass'] = 13.0
        self.Tupp[self.pft == 'Needleleaf tree'] = 26.0
        self.Tupp[self.pft == 'C4 grass'] = 45.0


        self.Vcmax25 = self.ne * self.nl
        self.ft = self.Q10_leaf ** (0.1 * (self.Tc-25.))
        self.Vcmax = self.Vcmax25 * self.ft / ((1.0+np.exp(0.3*(self.Tc-self.Tupp)))\
                                              *(1.0+np.exp(0.3*(self.Tlow-self.Tc))))

        # O3 terms
        self.Fo3_crit = np.zeros_like(self.data) + 1.6
        self.Fo3_crit[self.pft == 'C3 grass'] = 5.0
        self.Fo3_crit[self.pft == 'C4 grass'] = 5.0
        self.a = np.zeros_like(self.data) + 0.04
        self.a[self.pft == 'Needleleaf tree'] = 0.02
        self.a[self.pft == 'C3 grass'] = 0.25
        self.a[self.pft == 'C4 grass'] = 0.13
        self.a[self.pft == 'Shrub'] = 0.03
     
        self.k = np.zeros_like(self.data) + 0.5

        self.alpha = np.zeros_like(self.data) + 0.08
        self.alpha[self.pft == 'C3 grass'] = 0.12
        self.alpha[self.pft == 'C4 grass'] = 0.06

        self.omega = np.zeros_like(self.data) + 0.15
        self.omega[self.pft == 'C4 grass'] = 0.17

        self.fdr = np.zeros_like(self.data) + 0.015
        self.fdr[self.pft == 'C4 grass'] = 0.025

        self.rg = np.zeros_like(self.data) + 0.25

        self.nrl = np.zeros_like(self.data) + 1.00

        self.nsl = np.zeros_like(self.data) + 1.00
        self.nsl[self.pft == 'Broadleaf tree'] = 0.10
        self.nsl[self.pft == 'Needleleaf tree'] = 0.10

        self.aws = np.zeros_like(self.data) + 10.0
        self.aws[self.pft == 'C3 grass'] = 1.0
        self.aws[self.pft == 'C4 grass'] = 1.0

        self.gamma0 = np.zeros_like(self.data) + 0.25

        self.dm = np.zeros_like(self.data) + 0.0

        self.dt = np.zeros_like(self.data) + 9.0

        self.moff = np.zeros_like(self.data) + 0.0

        self.toff = np.zeros_like(self.data) + 278.15
        self.toff[self.pft == 'Needleleaf tree'] = 233.15
        self.toff[self.pft == 'Shrub'] = 233.15

        self.gammap = np.zeros_like(self.data) + 20.
        self.gammap[self.pft == 'Broadleaf tree'] = 15.0

        self.gammav = np.zeros_like(self.data) + 0.2
        self.gammav[self.pft == 'Broadleaf tree'] = 0.005
        self.gammav[self.pft == 'Needleleaf tree'] = 0.007
        self.gammav[self.pft == 'Shrub'] = 0.05

        self.gammar = np.zeros_like(self.data) + 0.25
        self.gammar[self.pft == 'Needleleaf tree'] = 0.15

        self.gammaw = np.zeros_like(self.data) + 0.20
        self.gammaw[self.pft == 'Broadleaf tree'] = 0.005
        self.gammaw[self.pft == 'Needleleaf tree'] = 0.005
        self.gammaw[self.pft == 'Shrub'] = 0.05

        self.Lmax  = np.zeros_like(self.data) + 4.0
        self.Lmax[self.pft == 'Broadleaf tree'] = 9.00
        self.Lmax[self.pft == 'Needleleaf tree'] = 5.00
        self.Lmax[self.pft == 'Shrub'] = 3.00

        self.Lmin  = np.zeros_like(self.data) + 1.0

        self.awl = np.zeros_like(self.data) + 0.65
        self.awl[self.pft == 'C3 grass'] = 0.005
        self.awl[self.pft == 'C4 grass'] = 0.005
        self.awl[self.pft == 'Shrub'] = 0.10

        self.bwl = np.zeros_like(self.data) + 1.667

        self.sigmal = np.zeros_like(self.data) + 0.05
        self.sigmal[self.pft == 'C3 grass'] = 0.025
        self.sigmal[self.pft == 'Needleleaf tree'] = 0.10
        self.sigmal[self.pft == 'Broadleaf tree'] = 0.0375

        self.etasl = np.zeros_like(self.data) + 0.01


    def leafPhotosynthesis(self):
        '''

        NB:
            O3 treatment requires:
            self.ra, self.Fo3_crit, self.a, self.kappao3, self.gl, self.O3
            which are starred * below. Safe failure if not present

        Uses:
            self.Tc      : canopy (leaf) temperature (C)
            self.C3      : array of True ('C3') or False ('C4')
            self.Ipar    : incident PAR (mol m-2 s-1)

            *self.O3      : molar conc. of O3 at reference level (nmol m-3)
            *self.ra      : aerodynamic and boundary layer resistance between leaf surface 
                           and reference level (s m-1)
            *self.gl      : leaf conductance for H20 (m s-1)

            [set in self.initialise()]
            self.thetac  : soil moisture critical concentration
            self.thetaw  : soil moisture critical concentration

            [set in self.variables()]
            self.theta   : mean soil moisture concentration in the root zone,
            self.pstar   : Surface pressure (Pa)
            self.co2c    : Canopy level CO2 concentration (kg CO2/kg air).

            [set in initialiser]
            self.zeroC   : 0 C in K
            self.R_gas   : J mol-1 K-1
            self.o2      : Canopy level O2 concentration (kg O2/kg air).

            [set in self.defaults()]
            self.Oa      : Partial pressure of atmos Oxygen (Pa)
            self.epco2   : Ratio of molecular weights of CO2 and dry air.
            self.epo2    : Ratio of molecular weights of O2 and dry air.
            self.Vcmax   : maximum rate of carboxylation of Rubisco (mol CO2 m-2 s-1)
            self.Gamma   : CO2 compensation point in the absence of mitochindrial
                           respiration (Pa)
            self.beta1   : colimitation coefficients
            self.beta2   : colimitation coefficients
            self.alpha   : quantum efficiency of photosynthesis (mol CO2 mol-1 PAR)
            self.omega   : leaf scattering coefficient for PAR
            *self.kappao3 : ratio of leaf resistance for O3 to leaf resistance to water vapour
            *self.Fo3_crit: critical value of Ozone stress limitation
            *self.a       : Ozone factor
            self.ratio   : Ratio of leaf resistance for CO2 to leaf resistance for H2O.

        Generates:
            self.Kc      : Michaelis-Menten paramemeter for CO2
            self.Ko      : Michaelis-Menten paramemeter for O2
            self.ci      : leaf internal CO2 partial pressure (Pa)
            self.Wc      : Rubisco-limited rate
            self.We      : Light-limited rate
            self.Ws      : Rate of transport of photosynthetic products

            self.Wp      : Wc/We smoothed term

            self.W       : combined limiting rate
            self.Rd      : leaf dark respiration
            *self.Fo3     : leaf O3 flux

            self.Ap      : (unstressed) leaf photosynthetic carbon uptake
            self.beta    : water stress limitation
            *self.F       : Ozone stress limitation
            self.Al      : leaf photosynthetic carbon uptake

        Updated:
            self.gl      : leaf stomatal conductance

        '''
        c3 = np.where(self.C3) 
        c4 = np.where(~self.C3)

        self.ca = np.ones_like(self.data) * self.co2c / self.epco2 * self.pstar
        self.oa = np.ones_like(self.data) * self.O2 / self.epo2 * self.pstar

        # we need ci here
        # we will estimate that here after Knorr, 1988
        # for simplicity
        self.ci = np.where ( self.C3, self.ca*0.87, self.ca*0.67 )

        self.Kc = 30. * self.Q10_Kc ** (0.1*(self.Tc - 25.))
        self.Ko = 3e4 * self.Q10_Ko ** (0.1*(self.Tc - 25.))
        self.Wc = self.Vcmax*1.
        self.Wc[c3] = self.Vcmax[c3] * ((self.ci-self.Gamma)/(self.ci+self.Kc*(1+self.Oa/self.Ko)))[c3]
        self.Wc[self.Wc<0] = 0.

        self.We = self.alpha*(1-self.omega)*self.Ipar
        self.We[c3]  = (self.alpha*(1-self.omega)*self.Ipar\
                       * ((self.ci-self.Gamma)/(self.ci+2.*self.Gamma)))[c3]
        self.We[self.We<0] = 0.

        self.Ws = 0.5 * self.Vcmax
        self.Ws[c4] = (2.e4 * self.Vcmax * self.ci/self.pstar)[c4]
        self.Ws[self.Ws<0] = 0.

        b1 = self.beta1*np.ones_like(self.data)
        b2 = -(self.Wc+self.We)
        b3 = self.Wc*self.We
        self.Wp = (-b2/(2.*b1) - np.sqrt(b2*b2/(4*b1*b1) - b3/b1))/self.beta1

        b1 = self.beta2*np.ones_like(self.data)
        b2 = -(self.Wp+self.Ws)
        b3 = self.Wp*self.Ws
        self.W = -b2/(2.*b1) - np.sqrt(b2*b2/(4*b1*b1) - b3/b1)

        self.Rd = self.fdr * self.Vcmax

        # Calculate the net rate of photosynthesis
        self.Ap = self.W - self.Rd

        self.beta = 1.0+(self.W*0.)
        w = np.where(self.theta <= self.thetac)
        self.beta[w] = ((self.theta-self.thetaw)/(self.thetac-self.thetaw))[w]
        w = np.where(self.theta <= self.thetaw)
        self.beta[w] = 0.0

       # water limited net rate of photosynthesis
        self.Al = self.Ap * self.beta 

        # Calculate the factor for converting mol/m3 into Pa (J/m3).
        conv = self.R_gas * (self.Tc + self.zeroC)
        # Diagnose the leaf conductance
        # Leaf conductance for CO2 (m/s)
        glco2 = (self.Al * conv) / (self.ca - self.ci)
        self.gl = self.ratio * glco2
        # Close stomata at points with negative or zero net photosynthesis
        # or where the leaf resistance exceeds its maximum value.
        w = np.where( ( self.gl <= self.glmin ) * (self.Al <= 0))
        self.gl[w] = self.glmin
        glco2 = self.gl/self.ratio
        self.gl = self.ratio * glco2

        self.Al[w] = -self.Rd[w] * self.beta[w] 

        # quadratic for O3
        # requires:
        # self.ra, self.Fo3_crit, self.a, self.kappao3, self.gl, self.O3
        try:
            a = self.gl * self.ra
            b = self.a * self.Fo3_crit * self.O3 - self.kappao3 \
                - self.gl * self.ra * (self.a * self.Fo3_crit + 1)
            c = self.a * self.Fo3_crit * self.kappao3 + self.kappao3
            coefs = [a,b,c]
            roots = np.roots(coeff)
            self.F = np.min(roots)

            gl = self.gl * self.F
            self.Fo3 = self.O3/(self.ra - self.kappao3 / gl)
            self.F = (self.Fo3-self.Fo3_crit)
            self.F[self.F<0.] = 0.
            self.F = 1. - self.a * self.F
        except:
            self.F = 1.0
            self.Fo3 = 0.0

        self.Al = self.Al * self.F
        self.gl = self.gl * self.F
        return

    def canopyPhotosynthesis(self):
        '''
        Big leaf (Sellers equivalent)

        Uses:
        self.Lcarbon   : leaf C pool (kg C m-2)
        self.Rcarbon   : root C pool (kg C m-2)
        self.Scarbon   : respiring stem C pool (kg C m-2)

        [set in self.defaults()]
        self.k         : canopy geometry term (G function)
        self.rg        : growth respiration coefficient
        self.n0        : top leaf N concentration (kg N (kg C)-1)
        self.sigmal    : specific leaf density (kg C m-2 per unit of LAI)
        self.nrl       : proportion of root N to leaf N
        self.nsl       : proportion of stem N to leaf N
        self.aws       : ratio of total stem C to respiring stem C
        self.etasl     : ratio of live stemwood to LAI * height

        [set in self.leafPhotosynthesis()]
        self.Al        : leaf assimilation
        self.Rd        : leaf dark respiration
        self.beta      : water limioting factor

        Generates:
        self.nm        : mean leaf N concentration (kg N (kg C)-1)
        self.Ac        : canopy assimilation
        self.Rdc       : canopy dark respiration
        self.PiG       : GPP
        self.Pi        : NPP
        self.Rp        : plant respiration
        self.Rpg       : growth respiration
        self.Rpm       : maintenance respiration
        self.Nl        : leaf N conc.
        self.Nr        : root N conc.
        self.Nw        : wood N conc.
        self.Lc        : leaf area index
        '''

        self.Lc = self.Lcarbon / self.sigmal

        self.Ac = self.Al * (1. - np.exp(-self.k * self.Lc))/self.k
        self.Rdc = self.Rd * (1. - np.exp(-self.k * self.Lc))/self.k
        self.PiG = self.Ac + self.beta * self.Rdc
        self.nm = self.n0*1.

        #self.Scarbon = self.etasl * self.h * self.Lc

        self.Nl = self.nm * self.sigmal * self.Lc
        self.Nr = self.nrl * self.nm * self.Rcarbon
        self.Ns = self.nsl * self.nm * self.Scarbon
        self.Rpm = 0.012 * self.Rdc * (self.beta + (self.Nr + self.Ns)/(self.Nl))
        self.Rpg = self.rg * (self.PiG - self.Rpm)
        self.Rp = self.Rpm + self.Rpg
        self.Pi = self.PiG - self.Rp

    def phenology(self):
        '''
        Uses:
            self.gamma0  : minimum leaf turnover rate (360 days-1)
            self.dm      : rate of change of turnover with soil moisture
                           stress (360 days-1)
            self.dt      : rate of change of turnover with T (360 days K)-1
            self.moff    : threshold soil mositure stress
            self.toff    : threshold temperature (K)
            self.gammap  : rate of leaf growth (360 days)-1
            self.Tc      : canopy (leaf) temperature (C)
            self.Lb      : seasonal maximum LAI
            self.L       : actual LAI
            self.dt      : time interval(days)

        Generates:
            self.gammalm : leaf mortality rate

        Updates:
            self.p       : phenological status
        '''

        self.gammalm = self.gamma0 * (1. + self.dt*(self.toff-self.Tc))
        self.gammalm[self.Tc > self.toff] = self.gamma0

        #self.p = self.L / self.Lb
        self.dp_dt = np.zeros_like(self.Tc) +  -self.gammap
        w = np.where(self.gammalm <= 2.*self.gammap)
        self.dp_dt[w] = (self.gammap*(1-self.p))[w]

        self.p += self.dp_dt * self.dt

        self.gammal = -self.dp_dt
        self.gammal[w] = (self.p*self.gammalm)[w]

    def dynamics(self):
        '''
        Uses:

        Generates:

        '''
        self.nustar = self.nu*1.
        self.nustar[self.nustar < 0.01] = 0.01
        self.lambda_ = (self.Lb - self.Lmin)/(self.Lmax-self.Lmin)
        self.lambda_[self.Lb > self.Lmax] = 1.0
        self.lambda_[self.Lb < self.Lmin] = 0.0
 
 
        self.dCv_dt = (1. - self.lambda_)*self.Pi - self.Lambdal
        self.dnu_dt = (self.lambda_ * self.Pi * self.nustar)/self.Cv - self.gammav*self.nustar


