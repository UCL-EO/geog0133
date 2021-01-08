import numpy as np
import bethy_fapar  as fapar  

class photosynthesis():

    def __init__(self):
        '''
        Class initialisation and setup of parameters
        '''
        # zero C in K
        self.zeroC = 273.15
        # gas constant J mol-1 K-1
        self.R_gas = 8.314
        #  Minimum of maximum carboxylation rate [10^(-6) mol/(m^2 s)]
        self.minOfMaxCarboxrate = 1e-12
        # Minimum stomatal conductance [mol H2O /(m^2 s)]
        self.minStomaConductance = 0.0

        # oxygen concentration
        self.Ox = 0.21 # mol(O2)mol(air)-1
        # energy content of PAR quanta 
        self.EPAR = 220. # kJmol-1
        # photon capture efficiency
        self.alpha = 0.28
        # maximum Michaelis-Menton values for CO2
        self.KC0 = 460.e-6 # mol(CO2)mol(air)-1
        # maximum Michaelis-Menton values for O2
        self.KO0 = 330.e-3 # mol(O2)mol(air)-1
        # activation energy for KC
        self.EC = 59396. # J mol-1
        # activation energy for KO
        self.EO = 35948. # J mol-1
        # activation energy for VCMAX
        self.EV = 58520. # J mol-1
        # activation energy for dark respiration
        self.ER = 45000. # J mol-1
        #  Q10=2 (Collatz et al. 1992)
        self.EK = 50967.
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

        # LAI limit used in N scaling
        self.LaiLimit = 3.

    def calc_nitrogen_scaling_factors(self,zlai,layer_bounds,declination,latitude):
        '''

        '''
        factors = np.ones((layer_bounds.size,zlai.size))
        cos_zenith_noon = np.cos(declination)*np.cos(latitude) \
                          + np.sin(declination)*np.sin(latitude)
        ww = np.where(cos_zenith_noon < 1e-3)
        cos_zenith_noon[ww] = 1e-3

        #  Extinction factor
        k12 = 0.5 / cos_zenith_noon

        # Condition: LAI>LaiLimit
        ww = np.where(zlai >= self.LaiLimit)
        for i in range(ayer_bounds.size):
            factors[i,:] = np.exp(-k12 * layer_bounds[i] * zlai.flatten())
        return factors
  

    def assimilate(self,delta_time,mask,cos_zenith,declination,latitude,\
                    swdown, par, frac_par_direct, pressure,\
                    canopy_temp, soil_albedo, CO2_concentration_air,\
                    canopy_conductance, lai, waterLimitationFlag):
        '''


        '''
        # Expresse radiation in mol(photons) / (m^2 s)
        swdown_mol = swdown/self.EPAR

        # soil reflectivity is set to soil albedo of the visible range
        soil_reflectivity_par = soil_albedo

        # canopy_boundaries_lai
        canopy_boundaries_lai = np.arange(ncanopy)/float(ncanopy)

        # calculate nitrogen scaling factors
        nitrogen_scaling_factors = self.calc_nitrogen_scaling_factors(lai,\
                                                    canopy_boundaries_lai,\
                                                    declination,\
                                                    latitude)
        (laiPerLayer,fAPAR) = fapar.faparl(mask,ncanopy,lai,soil_reflectivity_par,cos_zenith,frac_par_direct,\
                                  canopy_boundaries_lai)
        # Compute absorbed PAR per leaf area in canopy layer [units: (absorbed photons) / (m^2(leaf area) s)] from
        # par and fraction of absorbed PAR (Epar is needed to convert radiation intensity from W/m^2 to mol/(m^2 s))
        apar_acc = np.zeros_like(faPAR)

        lai_ = laiPerLayer*1.
        ww = np.where(lai_ < 1.e-10)
        lai_[ww] = 1.e-10

        for icanopy in range(ncanopy):
            apar_layer = (par/Epar)*faPAR[icanopy]/lai_[icanopy]
            apar_acc += (par/Epar)*faPAR[icanopy]*delta_time

        # Convert CO2 mass mixing ratio [kg/kg] to volume mixing ratio [mol/mol]
        CO2_concentration_mol = CO2_concentration_air * self.molarMassAir_kg / self.molarMassCO2_kg

        # estimate CO2 leaf conc
        CO2_conc_leaf = self.FCI1C3*CO2_concentration_mol

        self.photosynthesis(C3Flag,waterLimitationFlag,PAR,PIRRIN,P,T,CO2_concentration_mol,\
                            NSCL,ETransport,CarboxRate,Ci,Gs)

    def photosynthesis(self,C3Flag,waterLimitedFlag,PAR,PIRRIN,P,T,Atm_co2_conc,\
                         NSCL,ETransport,CarboxRate,\
                         Ci,Gs):
        '''
        Farquar et al. 1980 C3 photosynthesis
   
        args:

        C3Flag :   True if C3, False for C4

        waterLimited : flags to indicate water limited or not

        PAR :       Absorbed PAR mol(photons) m-2 s-1
        PIRRIN :    Total irridiance at the surface mol m-2 s-1
        P    :      air pressure (Pa)
        T    :      vegetation (leaf) temperature (K)
        Atm_co2_conc : Atmospheric CO2 conc. 

        NSCL :      Nitrogen scaling factor at maximum 
                carboxylation rate and maximum 
                electron transport rate
        ETransport
              : The maximum rate of electron transport 
                at 25 C for each PFT (mol(CO2) m-2 s-1)
        CarboxRate
              : The maximum carboxilation rate at 25 C 
                (micro mol(CO2) m-2 s-1)

        Ci  :       CO2 concentration inside leaf mol(CO2) mol(air)-1 
        Gs  :       Stomatal conductance (use for water-limited)

        Returns:
        
        (A,Diagnostics)   : A = gross assimilation

        '''
        # return None if no data
        if C3Flag.size == 0:
            return None

        # work out which are C3 and C4
        wC3 = np.where(C3Flag)
        wC4 = np.where(not C3Flag)

        # process C3
        if wC3.sum():
            (A3,C3diagnostics) = self.photosynthesisC3(PAR[wC3],PIRRIN[wC3],P[wC3],T[wC3],Atm_co2_conc[wC3],\
                                  NSCL[wC3],ETransport[wC3],CarboxRate[wC3],\
                                  Ci[wC3],Gs[wC3],waterLimited[wC3])
        else:
            A3 = np.array([])
            C3diagnostics = {}

        # process C4
        if wC4.sum():
            (A4,C4diagnostics) = self.photosynthesisC4(PAR[wC4],PIRRIN[wC4],P[wC4],T[wC4],Atm_co2_conc[wC4],\
                                  NSCL[wC4],ETransport[wC4],CarboxRate[wC4],\
                                  Ci[wC4],Gs[wC4],waterLimited[wC4])
        else:
            A4 = np.array([])
            C4diagnostics = {}
        # combine
        A = np.zeros_like(C3Flag).astype(float)
        A[C3Flag] = A3
        A[not C3Flag] = A4

        self.Diagnostics = {}
        keys = np.unique(np.array(C3diagnostics.keys() + C4diagnostics.keys()))

        for k in keys:
           self.Diagnostics[k] = np.zeros_like(A)
           try:
               self.Diagnostics[k][wC3] = C3diagnostics[k]
           except:
               pass
           try:
               self.Diagnostics[k][wC4] = C4diagnostics[k]
           except:
               pass

        self.Diagnostics['C3Flag'] = C3Flag
        self.Diagnostics['waterLimited'] = waterLimited
        return (A,self.Diagnostics)

    def photosynthesisC4(self,PAR,PIRRIN,P,T,Atm_co2_conc,\
                         NSCL,ETransport,CarboxRate,\
                         Ci,Gs,waterLimited):
        '''
        Similar to C3 case, but 
        For C4 plants the Farquhar equations are replaced by the set of equations of
        Collatz et al. 1992:

        args:

        PAR :       Absorbed PAR mol(photons) m-2 s-1
        PIRRIN :    Total irridiance at the surface mol m-2 s-1
        P    :      air pressure (Pa)
        T    :      vegetation (leaf) temperature (K)
        Atm_co2_conc : Atmospheric CO2 conc. 
        NSCL :      Nitrogen scaling factor at maximum 
                carboxylation rate and maximum 
                electron transport rate
        ETransport
              : The maximum rate of electron transport 
                at 25 C for each PFT (mol(CO2) m-2 s-1)
        CarboxRate
              : The maximum carboxilation rate at 25 C 
                (micro mol(CO2) m-2 s-1)

        Ci  :       CO2 concentration inside leaf mol(CO2) mol(air)-1 
        Gs  :       Stomatal conductance

        waterLimited : flags for water limited or not

        Returns:
        
        (A,Diagnostics)   : A = gross assimilation
        '''
        # T1 = 25 C in K
        T1 = 25. + self.zeroC
        # T0 is veg temperature relative tp 25 C
        T0 = T - T1
        # TC is the temperatrure in C
        TC = T - self.zeroC

        # K is the PECase CO2 specifity instead of the electron transport capacity
        # within C3 plants
        K = ETransport * 1.e3 * NSCL \
            * np.exp(self.EK * T0 / T1 / self.R_gas / T)

        # VCMAX : : assume N content, therefore Rubisco is placed
        # where most incoming light is
        # NB .. this is a structural consideration
        VCMAX = CarboxRate  * NSCL * np.exp(self.EV * T0 / T1 / self.R_gas / T)

        # dark respiration (mol(CO2)m-2s-1)
        Rd = self.FRDC4 * CarboxRate * NSCL \
             * np.exp(self.ER * T0 / T1 / self.R_gas / T) \
             * highTInhibit(TC) \
             * darkInhibit(PIRRIN)

        # C4 gross photosynthesis at given Ci
        J0 = (self.ALC4 * PAR + VCMAX) /  2. / self.Theta  
        Je = J0 - np.sqrt(J0*J0 - VCMAX * self.ALC4 * PAR / self.Theta)   

        Jc = np.zeros_like(Rd)
        A  = np.zeros_like(Rd)

        waterLimit = np.where(waterLimited)
        notWaterLimit = np.where(not waterLimited)

        if notWaterLimit.sum() > 0:
            Ci_ = Ci[notWaterLimit]
            TC_ = TC[notWaterLimit]
            Rd_ = Rd[notWaterLimit]
            Atm_co2_conc_ = Atm_co2_conc[notWaterLimit]
            P_ = P[notWaterLimit]
            T_ = T[notwaterLimit]
            K_ = K[notWaterLimit]
            Je_ = Je[notWaterLimit]

            Jc_ = K_ * Ci_

            # assimilation is the minimum of Je and Jc
            # with a high temperature inhibition
            # mol(CO2)m-2s-1
            A_ = Je_
            ww = np.where(Jc_ < Je_)
            A_[ww] = Jc_[ww]
            A_ = A_ * highTInhhibit(TC_)   

            # stomatal conductance
            Gs_ = 1.6 * (A_-Rd_) * self.R_gas * T_/ (Atm_co2_conc_ - Ci_) / P_
            ww = np.where(Gs_ < self.minStomaConductance)
            Gs_[ww] = self.minStomaConductance

            Gs[notWaterLimit] = Gs_
            Jc[notWaterLimit] = Jc_
            A[notWaterLimit] = A_
        else:
            # water limted, so Gs is defined and Ci must be calculated

            Gs_ = Gs[waterLimit]
            TC_ = TC[waterLimit]
            Rd_ = Rd[waterLimit]
            Atm_co2_conc_ = Atm_co2_conc[waterLimit]
            P_ = P[waterLimit]
            T_ = T[waterLimit]
            K_ = K[waterLimit]
            Je_ = Je[waterLimit]

            G0 = Gs_ / 1.6 / self.R_gas / T_ * P_

            Jc_  = (G0 * Atm_co2_conc_ + Rd_)/(1. + G0/K_)
            ww = np.where(Jc_ < 0)
            Jc_[ww] = 0.

            # assimilation is the minimum of Je and Jc
            # with a high temperature inhibition
            # mol(CO2)m-2s-1
            A_ = Je_
            ww = np.where(Jc_ < Je_)
            A_[ww] = Jc_[ww]
            A_ = A_ * highTInhhibit(TC)

            maxer1 = A_ - Rd_
            maxer2 = G0
            ww = np.where(G0<1e-6)
            maxer2[ww] = 1e-6
            maxer = maxer1/maxer2
            ww = np.where(maxer < 0)
            maxer[ww] = 0.
            Ci_ = Atm_co2_conc_ - maxer

            Ci[notWaterLimit] = Ci_
            Jc[notWaterLimit] = Jc_
            A[notWaterLimit] = A_

        Diagnostics =  {'max carboxylation rate':VMAX,\
                             'internal leaf CO2':Ci,\
                             'gross assimilation':A,\
                             'dark respiration':Rd,\
                             'stomatal conductance':Gs,\
                             'max e-transport rate':Jmax,\
                             'carboxylation rate':Jc,\
                             'e-transport rate':Je}
        return (A,Diagnostics)

 
    def photosynthesisC3(self,PAR,PIRRIN,P,T,Atm_co2_conc,\
                         NSCL,ETransport,CarboxRate,\
                         Ci,Gs,waterLimited):
        '''
        Farquar et al. 1980 C3 photosynthesis
   
        args:

        PAR :       Absorbed PAR mol(photons) m-2 s-1
        PIRRIN :    Total irridiance at the surface mol m-2 s-1
        P    :      air pressure (Pa)
        T    :      vegetation (leaf) temperature (K)
        Atm_co2_conc : Atmospheric CO2 conc. 

        NSCL :      Nitrogen scaling factor at maximum 
            	carboxylation rate and maximum 
            	electron transport rate
        ETransport
              :	The maximum rate of electron transport 
            	at 25 C for each PFT (mol(CO2) m-2 s-1)
        CarboxRate
              :	The maximum carboxilation rate at 25 C 
            	(micro mol(CO2) m-2 s-1)

        Ci  :       CO2 concentration inside leaf mol(CO2) mol(air)-1 
        Gs  :       Stomatal conductance

        waterLimited : flags to indicate water limited or not

        Returns:
        
        (A,Diagnostics)   : A = gross assimilation

        '''

        # T1 = 25 C in K
        T1 = 25. + self.zeroC
        # T0 is veg temperature relative tp 25 C
        T0 = T - T1
        # TC is the temperatrure in C
        TC = T - self.zeroC
    
        # Temperature dependent rates and compensation point
        KC = self.KC0 * np.exp(self.EC * T0 / T1 / self.R_gas / T)
        KO = self.KO0 * np.exp(self.EO * T0 / T1 / self.R_gas / T)
    
        # CO2 compensation point without leaf respiration
        # assumed in JSBACH to be a linear fn of temperature (C)
        GammaStar  = self.GammaStarScale * TC
        ww = np.where(GammaStar < 0)
        GammaStar[ww] = 0.
    
        # VCMAX : assume N content, therefore Rubisco is placed
        # where most incoming light is
        # NB .. this is a structural consideration
        VCMAX = CarboxRate  * NSCL * np.exp(self.EV * T0 / T1 / self.R_gas / T)
     
        # Jmax maximum electron transport rate mol(CO2)m-2s-1
        Jmax = ETransport * NSCL * TC/25.
        ww = np.where(Jmax <= self.minOfMaxCarboxrate)
        Jmax[ww] = self.minOfMaxCarboxrate
    
    
        # electron transport rate:
        ww = np.where(Jmax <= self.minOfMaxCarboxrate)
        J = self.alpha * PAR * Jmax \
            / np.sqrt(Jmax * Jmax + self.alpha * self.alpha * PAR * PAR) 
        J[ww] = 0.
    
        # dark respiration (mol(CO2)m-2s-1)
        Rd = self.FRDC3 * CarboxRate * NSCL \
             * np.exp(self.ER * T0 / T1 / self.R_gas / T) \
             * highTInhibit(TC) \
             * darkInhibit(PIRRIN)

        Jc = np.zeros_like(Rd)
        Je = np.zeros_like(Rd)
        A  = np.zeros_like(Rd)

        waterLimit = np.where(waterLimited)
        notWaterLimit = np.where(not waterLimited)
        
        if notWaterLimit.sum() > 0:
            VCMAX_ = VCMAX[notWaterLimit]
            Ci_ = Ci[notWaterLimit]
            GammaStar_ = GammaStar[notWaterLimit]
            Kc_ = Kc[notWaterLimit]
            KO_ = KO[notWaterLimit]
            J_ = J[notWaterLimit]
            TC_ = TC[notWaterLimit]
            Rd_ = Rd[notWaterLimit]
            Atm_co2_conc_ = Atm_co2_conc[notWaterLimit]
            P_ = P[notWaterLimit]
            T_ = T[notWaterLimit]

            # no water limiting
            #  so Ci is defined and Gs is calculated

            # electron transport limited rate Je and
            # carboxylating rate Jc (mol(CO2)m-2s-1 
            Jc_ = VCMAX_ * (Ci_ - GammaStar_)/\
                (Ci_ + Kc_ * (1 + (self.Ox/KO_)))
    
            Je_ = J_ * (Ci_ - GammaStar_)/\
                (4. * (Ci_ + 2. * GammaStar_))
    
            # assimilation is the minimum of Je and Jc
            # with a high temperature inhibition
            # mol(CO2)m-2s-1
            A_ = Je_
            ww = np.where(Jc_ < Je_)
            A_[ww] = Jc_[ww]
            A_ = A_ * highTInhhibit(TC_)
    
            # stomatal conductance
            Gs_ = 1.6 * (A_-Rd_) * self.R_gas * T_/ (Atm_co2_conc_ - Ci_) / P_
            ww = np.where(Gs < self.minStomaConductance)
            Gs_[ww] = self.minStomaConductance

            Gs[notWaterLimit] = Gs_
            A[notWaterLimit] = A_
            Jc[notWaterLimit] = Jc_
            Je[notWaterLimit] = Je_
           
        if waterLimit.sum() > 0:
            VCMAX_ = VCMAX[waterLimit]
            Gs_ = Gs[waterLimit]
            GammaStar_ = GammaStar[waterLimit]
            Kc_ = Kc[waterLimit]
            KO_ = KO[waterLimit]
            J_ = J[waterLimit]
            TC_ = TC[waterLimit]
            Rd_ = Rd[waterLimit]
            Atm_co2_conc_ = Atm_co2_conc[waterLimit]
            P_ = P[waterLimit]
            T_ = T[waterLimit]

            # water limted, so Gs is defined and Ci must be calculated
           
            K1 = 2. * GammaStar_
            W1 = i_ / 4.
            W2 = VCMAX_
            K2 = Kc_ * (1 + Ox/KO_)
            G0 = Gs_ / 1.6 / self.R_gas / T_ * P_
            B = Rd_ + W1 + G0 * (Atm_co2_conc_ + K1)
            C = W1 * G0 * (Atm_co2_conc_ - GammaStar_) + W1 * Rd_

            sqrter = (B*B / 4.) - C
            ww = np.where(sqrter < 0)
            sqrter[ww] = 0.
            Je_ = B / 2. - np.sqrt(sqrter)
            ww = np.where(Je < 0)
            Je_[ww] = 0.

            B = Rd_ + W2 + G0 * (Atm_co2_conc_ + K2)
            C = W2 * G0 * (Atm_co2_conc_ - GammaStar_) + W2 * Rd_ 
            sqrter = (B*B / 4.) - C
            ww = np.where(sqrter < 0)
            sqrter[ww] = 0.
            Jc_ = B / 2. - np.sqrt(sqrter)
            ww = np.where(Jc_ < 0)
            Jc_[ww] = 0.

            # assimilation is the minimum of Je and Jc
            # with a high temperature inhibition
            # mol(CO2)m-2s-1
            A_ = Je_
            ww = np.where(Jc_ < Je_)
            A_[ww] = Jc_[ww]
            A_ = A_ * highTInhhibit(TC_)


            maxer1 = A_ - Rd_
            maxer2 = G0
            ww = np.where(G0<1e-6)
            maxer2[ww] = 1e-6
            maxer = maxer1/maxer2
            ww = np.where(maxer < 0)
            maxer[ww] = 0.

            Ci_ = Atm_co2_conc_ - maxer

            Ci[waterLimit] = Ci_
            A[waterLimit] = A_
            Jc[waterLimit] = Jc_
            Je[waterLimit] = Je_

        Diagnostics =  {'max carboxylation rate':VMAX,\
                             'internal leaf CO2':Ci,\
                             'gross assimilation':A,\
                             'dark respiration':Rd,\
                             'stomatal conductance':Gs,\
                             'max e-transport rate':Jmax,\
                             'carboxylation rate':Jc,\
                             'e-transport rate':Je}
        return (A,Diagnostics)


    def highTInhibit(self,Tc):
        '''
        Inhibit assimilation and respiration at temperatures
        above 55 C 
    
        From:
        Collatz et al., Physiological and environmental regulation
        of stomatal conductance, photosynthesis and transpiration: a model that
        includes a laminar boundary layer,
        Agricultural and Forest Meteorology, 54, pp. 107-136, 1991
    
        Args:
            Tc (np.array or similar) : Leaf temperature in C
    
        Kwargs:
            None
    
        Returns:
            A scaling term to reduce assimilation/respiration
            (same type as input)
        '''
        out = 1./(1. + np.exp(1.3 * (T- 55.)))
        ww = np.where(out > 1.)
        out[ww] = 1.
        return out

    def darkInhibit(self,IRR):
        '''
        Inhibit dark respiration
    
        Brooks and Farquhar, Effect of temperature on the CO2/O2 specifity on RBisCO
        and the rate of respiration in the light, Planta 165, 397-406, 1985
    
        inhibit the dark-respiration to 50% of it's uninhibited value
        up from 50 umol/m^2s
    
        From Bethy model (JSBACH)
    
        Args:
            IRR (np.array or similar) : Total irridiance at the surface [mol/(m^2 s)]
    
        Kwargs:
            None
    
        Returns:
            A scaling term to reduce dark respiration
            (same type as input)
        '''
        out = 0.5 + 0.5*np.exp(-IRR * 1e6 / 10.)
        ww = np.where(IRR == 0.)
        out[ww] = 0.
        ww = np.where(out > 1.)
        out[w] = 1.
        return out

    def error(self,msg):
        '''
        Print error msg and store in self.lastErrorMsg
        '''
        from sys import stderr
        stderr.write(msgi,'\n')
        self.lastErrorMsg = msg
