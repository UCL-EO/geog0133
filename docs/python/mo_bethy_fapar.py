class mo_bethy_fapar:

 def __init(self): 
  self.OMEGA = 0.12 # single leaf scattering albedo
  self.FcMax = 
  self.FcMin =
  self.ZenithMinPar = 
  self.LaiMin = 
  self.LaiLimit = 

 def FAPARL(self,ngrpts, mask, nnl \
       , PLAI, RHOS \
       , COSZEN, FDIR \
       , DDL \
       )

  '''
  !---------------------------------------------------------------------------------
  !
  !  FAPARL() computes the leaf area index per canopy layer (LAIL) and the absorbed
  !  photsynthetic active radiation (APAR) from total LAI and direct irradiation.
  !
  !---------------------------------------------------------------------------------
  SUBROUTINE FAPARL(ngrpts, mask, nnl &
       , PLAI, RHOS &
       , COSZEN, FDIR &
       , DDL  &
       , LAIL, APAR &
       )
    USE mo_bethy_constants,       ONLY: FcMax, FcMin, ZenithMinPar, LaiMin, LaiLimit

    !-----------------------------------------------------------------------
    ! ON ENTRY:
    !   PLAI   : Total LAI
    !   FC     : Canopy fraction
    !   FCMAX  : Maximum canopy fraction (0.9)
    !   RHOS   : soil albedo
    !   COSZEN : cosine of solar zenith angle, mue
    !   FDIR   : direct part of total Irradiance (e.g. 0.8)
    !   OMEGA  : single leaf scattering albedo = 0.12
    !   DDL    : leaf layer borders in units of LAI (0, 1/3, 2/3, 1)
    !   ZLMIN  : minimum LAI or LAI per layer (1e-6)
    !   NNL    : # of canopy layers
    !   N      : # of Longitude, DIMENSION OF THE IN AND OUTPUT FIELDS
    ! ON EXIT:
    !   LAIL   : LAI per canopy layer
    !   APAR   : THE ABSORBED PAR PER LEAF AERA PER CANOPY LAYER
    !            NORMALIZED TO INCOMING RADIATION = 1
    !------------------------------------------------------------------------
    INTEGER,  intent(in)  ::   ngrpts           ! number of grid points to be handled in this call
    LOGICAL,  INTENT(in)  ::   mask(ngrpts)
    INTEGER,  intent(in)  ::   nnl              ! number of canopy layers
    REAL(dp), intent(in)  ::   PLAI(ngrpts)     ! Total LAI
    REAL(dp), intent(in)  ::   RHOS(ngrpts)     ! soil albedo
    REAL(dp), intent(in)  ::   COSZEN(ngrpts)   ! cosine of solar zenith angle, 
    REAL(dp), intent(in)  ::   FDIR(ngrpts)     ! direct part of total Irradiance (e.g. 0.8)
    REAL(dp), intent(in)  ::   DDL(0:NNL)       ! canopy layer borders in units of LAI (0, 1/3, 2/3, 1)
    REAL(dp), intent(out) ::   LAIL(ngrpts,NNL) ! LAI per canopy layer
    REAL(dp), intent(out) ::   APAR(ngrpts,NNL) ! THE ABSORBED PAR PER LEAF AERA and PER CANOPY LAYER, ...
                                                ! ... NORMALIZED TO INCOMING RADIATION = 1.
    !---------------------------------------------------------------------
    ! Local Variables
    !---------------------------------------------------------------------
    REAL(dp)       :: ZH(ngrpts), K0(ngrpts), ZP0, ZP1(ngrpts)
    REAL(dp)       :: Q0(ngrpts), Q1(ngrpts), B0(ngrpts), B1(ngrpts)
    REAL(dp)       :: EKL(ngrpts), EHL(ngrpts), EKL0, EHL0, B4(ngrpts)
    REAL(dp)       :: FC(ngrpts) ! fractional vegetation cover
    REAL(dp)       :: X0, X1, X2, F, FSHD(ngrpts)
    INTEGER    :: JL, K
    '''
    lail = 0.
    apar = 0.
    '''
    !----------------------------------------------------------------------------
    ! Compute fractional vegetation cover  per grid cell and PFT 
    ! (not the same as fractional cover in JSBACH!)    
    !----------------------------------------------------------------------------

       WHERE (PLAI(:)< LaiLimit)
          FC(:) = PLAI(:) / LaiLimit * FcMax
       ELSEWHERE
          FC(:) = FcMax
       END WHERE
       FC(:) = MERGE(MAX(FC, FcMin),0._dp,mask)
    '''
    FC = PLAI*0.+self.FcMax
    ww  = np.where(PLAI <self.LaiLimit)
    FC[ww] = PLAI[ww] / self.LaiLimit * self.FcMax
    '''
    !----------------------------------------------------------------------------
    !     COMPUTE ABSORBED PAR PER LEAF AREA (!) AND PLAI PARTITIONING   
    !----------------------------------------------------------------------------
    ! Initialize ABSORBED PAR PER LEAF AREA,  IF COSZEN(JL)<1e-3
    ! Spread LAI equally around the three layers
    !----------------------------------------------------------------------------
    DO K = 1, NNL
       DO JL = 1, ngrpts
          IF (.NOT. mask(jl)) CYCLE
          APAR(JL,K) = 0._dp
          !------------------------------------------------------------
          !             LAIL(JL,NNL) = (DDL(NNL) - DDL(NNL-1)) * PLAI(JL)
          !------------------------------------------------------------
          LAIL(JL,K) = PLAI(JL) * (DDL(K) - DDL(K-1))
          LAIL(JL,K) = Max(LAIL(JL,K), LaiMin)
       ENDDO
    ENDDO
    '''
    for K in range(NNL):
        for JL in arange(ngrpts):
            APAR[JL,K] = 0.
            LAIL[JL,K] = PLAI[JL] * (DDL[K] - DDL[K-1])
    ww = np.where(LAIL<self.LaiMin)
    LAIL[ww] = self.LaiMin
    '''
    !--------------------------------------------------------------------
    ! The Absorbed Par per laef Area which is used later for the Net Assimilation,
    ! is calculated via the two stream approximation of Sellers (1985):
    !  muq * d(Rdown)/dl + (1-(1-b)*omega)*Rdown - omega*b*Rup   = omega*muq*k*(1-b0)*R
    ! -muq * d(Rup)/dl   + (1-(1-b)*omega)*Rup   - omega*b*Rdown = omega*muq*k*b0*R
    !  with
    !   Rdown - downwards diffusive flux
    !   Rup   - upwards diffusive Flux
    !   R     - direct flux, with R(0) = dPAR * RPAR with RPAR incoming irridiance in PAR
    !           and R = R0 * EXP(-kl) with R0=R(0) - exponential extinction law of 
    !           Monsi and Racki (1953)
    !           or similar Lambert-Beer's law
    !   b     - forward scatter fraction of diffusive flux
    !   b0    - forward scatter fraction of direct flux
    !   k     - extinction coefficient for the direct flux
    !   muq = int(1/K(mu))dmu|_0^1 - the integral of 1/K over the downward hemisphere
    !   omega - the single leaf albedo
    !
    !  The general solutions are (kl,hl=k*l,h*l):
    !  Rup   = q2*R0*EXP(-kl) + p1*B1*EXP(hl) + p2*B2*EXP(-hl)
    !  Rdown =-q1*R0*EXP(-kl) +    B1*EXP(hl) +    B2*EXP(-hl)
    !   with
    !    h  = sqrt( (1-(1-b)*omega)^2/muq^2 - omega^2*b^2/muq^2 )
    !    p1 = ( (1-(1-b)*omega) + muq * h )/omega/b
    !    p2 = ( (1-(1-b)*omega) - muq * h )/omega/b
    !   -q1 = (omega^2*b*muq*k* (1-b0) + omega*    b0  *muq*k*(1-(1-b)*omega - muq*k))/
    !         ((1-(1-b)*omega)^2-muq^2*k^2-omega^2*b^2)
    !    q2 = (omega^2*b*muq*k*    b0  + omega* (1-b0) *muq*k*(1-(1-b)*omega + muq*k))/
    !         ((1-(1-b)*omega)^2-muq^2*k^2-omega^2*b^2)
    !    B1/B2 from boundary conditions
    !-------------------------------------------------------------------
    !  Make two assumptions:
    !  1) the distribution of leaf angles is isotropic
    !  2) the leaf reflectivity and transmissivity are equal (the sum = omega)
    !  => b=0.5, b0=0.5, k=0.5/mu with mu=cos(theta) solar zenith angle => muq=1
    !
    !  => k  = 1/2/mu
    !     h  = sqrt( 1 - omega )
    !     p1 = ( 1-omega/2 + h )/omega/2
    !     p2 = ( 1-omega/2 - h )/omega/2
    !   ! p2 = 1 / p1 !
    !     q1 = ( (1 + 2*mu)*omega/2 )/(1-4*mu^2*(1-omega)) = ( k*(k + 1)*omega/2 )/
    !                                                        (k^2-1-omega)
    !     q2 = ( (1 - 2*mu)*omega/2 )/(1-4*mu^2*(1-omega)) = ( k*(k - 1)*omega/2 )/
    !                                                        (k^2-1-omega)
    !    
    ! Determine B1 and B2 from the boundary conditions:
    !  1) Rdown(0) equals the incoming diffuse radiation
    !     Rdown(0) = (1-dPAR)*RPAR
    !  => Rdown(0) + R(0) = (1-dPAR)*RPAR + dPAR*RPAR = RPAR as total incoming PAR
    !  2) the reflection at the lower boundary of the canopy is given by the soil 
    !     reflectance
    !     Rup(LAI) = RhosPAR * (R(LAI) + Rdown(LAI))
    !  Here: FAPARL gets RhosPAR as Variable RHOS, LAI is the total canopy LAI, PLAI
    ! 
    !  => B1 = + ( eta*R0 - (Rd+q1*R0) * gamma2 )/(gamma1 - gamma2)
    !     B2 = - ( eta*R0 - (Rd+q1*R0) * gamma1 )/(gamma1 - gamma2)
    !   with
    !     eta    = RhosPAR * (1-q1)-q2) * EXP(-k*LAI)
    !     gamma1 = ( p1 - RhosPAR) * EXP( + h*LAI)
    !     gamma2 = ( p2 - RhosPAR) * EXP( - h*LAI)
    !     Rd     = Rdown(0) = (1-dPAR)*RPAR
    !------------------------------------------------------------------
    ! THAT IS THE COMPLETE SOLUTION OF THE TWO STREAM APPROXIMATION UNDER THE BOUNDARY
    ! CONDITIONS AND ASSUMPTIONS MENTIONED ABOVE !!!!!!!!!!!!!!!!!!
    !
    ! Therefore, the absorbed Radiation inside the canopy is:
    !   APAR = -d/dl ( R(l) + Rdown - Rup)
    !        = (1-q1-q2)*k*R0*EXP(-kl) - (1-p1)*h*B1*EXP(hl) + (1-p2)*h*B2*EXP(-hl)
    ! But the absorbed PAR per canopy layer in discrete steps is:
    !   APAR(JL) = 1/(D(JL)-D(JL-1)) * int(-d/dl(R(l) + Rdown - Rup))dl|_D(JL)^D(JL-1)
    !            = (R(D(JL-1)) + Rdown(D(JL-1)) - Rup(D(JL-1)) - R(D(JL)) + Rdown(D(JL))
    !              - Rup(D(JL)) / ((D(JL)-D(JL-1))
    !  and  R(l)+Rdown-Rup = (1-q1-q2)*  R0*EXP(-kl) + (1-p1)*  B1*EXP(hl) + (1-p2) * 
    !                        B2*EXP(-hl)
    !------------------------------------------------------------------
    ! The clumping of the vegetation is taken into account, defining LAIc = LAI / fc
    ! as an effective LAI.
    ! Taken this into account, l = l/fc but the solutions stay as they are because 
    ! of the differentiations are take d/dl according to the NEW l=l/fc
    ! Only APAR has to be multiplied with fc at the END because D(JL)-D(JL-1) is still
    ! the old l
    !------------------------------------------------------------------
    '''
    '''
    DO JL = 1, ngrpts
       IF (.NOT. mask(jl)) CYCLE
       IF (COSZEN(JL).GE. ZenithMinPar) THEN
    '''
    for JL in range(ngrpts):
       if COSZEN[JL] >= ZenithMinPar:
          '''
          !----------------------------------
          !  h = sqrt( 1 - omega )
          !----------------------------------
          ZH(JL) = SQRT (1._dp - OMEGA)
          '''
          ZH(JL) = np.sqrt(1. - self.OMEGA)
          !----------------------------------
          !  p1 = ( 1-omega/2 + h )/omega/2
          !----------------------------------
          ZP1(JL) = (1._dp - OMEGA / 2._dp + ZH(JL)) & 
               / OMEGA * 2._dp 
          !----------------------------------------
          ! p2 = ( 1-omega/2 - h )/omega/2 = 1 / p1
          !----------------------------------------
          ZP0 = 1._dp / ZP1(JL) 
          !----------------------------------
          ! k = 0.5/mu
          !----------------------------------
          K0(JL) = 0.5_dp / COSZEN(JL) 
          IF (K0(JL).EQ.ZH(JL)) K0(JL) = K0(JL) + 1E-12_dp
          IF (K0(JL).EQ.-ZH(JL)) K0(JL) = K0(JL) + 1E-12_dp
          !--------------------------------------------------------------
          ! denominator of q1 and q2
          !--------------------------------------------------------------
          X0 = (1._dp - 4._dp * COSZEN(JL)**2 * ZH(JL)**2)
          !--------------------------------------------------------------
          ! q1 = ( (1 + 2*mu)*omega/2 )/(1-4*mu^2*(1-omega))
          !    = ( k*(k + 1)*omega/2 )/(k^2-1-omega)
          !--------------------------------------------------------------
          Q1(JL) = ((1._dp + 2._dp * COSZEN(JL)) &
               * OMEGA / 2._dp) / X0
          !--------------------------------------------------------------
          ! q2 = ( (1 - 2*mu)*omega/2 )/(1-4*mu^2*(1-omega))
          !    = ( k*(k - 1)*omega/2 )/(k^2-1-omega)
          !--------------------------------------------------------------
          Q0(JL) = ((1._dp - 2._dp * COSZEN(JL)) &
               * OMEGA / 2._dp) / X0

          FSHD(JL) = MAX (FC(JL), FcMin)
          !-----------------------------------------------------------
          ! EXP(-k*LAI/fc)
          !-----------------------------------------------------------
          EKL(JL) = EXP(-K0(JL) / FSHD(JL) * PLAI(JL))
          !------------------------------------------------------------
          ! EXP(-h*LAI/fc)
          !-----------------------------------------------------------
          EHL(JL) = EXP(-ZH(JL) / FSHD(JL) * PLAI(JL))
          !-----------------------------------------------------------
          ! gamma1 = ( p1 - RhosPAR) * EXP( + h*LAI)
          !----------------------------------------------------------- 
          X1 = (ZP1(JL) - RHOS(JL)) / EHL(JL)
          !-----------------------------------------------------------
          ! gamma2 = ( p2 - RhosPAR) * EXP( - h*LAI)
          !-----------------------------------------------------------          
          X0 = (ZP0 - RHOS(JL)) * EHL(JL)
          !-----------------------------------------------------------
          ! eta = (RhosPAR * (1-q1)-q2) * EXP(-k*LAI)
          !-----------------------------------------------------------
          X2 = (RHOS(JL) * (1._dp - Q1(JL)) - Q0(JL)) * EKL(JL)
          !------------------------------------------------------------
          ! F = 1 - dPAR + dPAR * q1
          ! => F*RPAR = Rd + q1*R0
          ! i.e. calculation takes RPAR=1
          !-----------------------------------------------------------           
          F = 1._dp - FDIR(JL) + Q1(JL) * FDIR(JL)
          !-------------------------------------------------------------
          ! B1(JL)*RPAR = B1, B2(JL)*RPAR = B2, B4(JL)*RPAR = R(0) + Rdown(0) - Rup(0)
          !  B1 = + ( eta*R0 - (Rd+q1*R0) * gamma2 )/(gamma1 - gamma2)
          !------------------------------------------------------------
          B1(JL) = (X2 * FDIR(JL) - F * X0) / (X1 - X0)
          !-----------------------------------------------------------
          !  B2 = - ( eta*R0 - (Rd+q1*R0) * gamma1 )/(gamma1 - gamma2)
          !     = eta*R0/(gamma2-gamma1) + (Rd+q1*R0) / (1-gamma2/gamma1)
          !  Note: the second form is used to avoid compiler-dependent ambiguity in the
          !        result of gamma1/(gamma1-gamma2) if gamma1 = infinity
          !-----------------------------------------------------------
          B0(JL) = X2 * FDIR(JL) / (X0 - X1) + F / (1.0_dp - X0/X1)
          !-----------------------------------------------------------
          !  R(l)+Rdown-Rup = (1-q1-q2)* R0*EXP(-kl) + (1-p1)* B1*EXP(hl) + (1-p2)* B2*EXP(-hl)
          !----------------------------------------------------------------------------
          B4(JL) = (1._dp - Q0(JL) - Q1(JL)) * FDIR(JL) &
               + (1._dp - ZP1(JL)) * B1(JL) + (1._dp - ZP0) * B0(JL)
       ENDIF                                                      ! mue>0.001
    END DO                                                        !end nproma

    !------------------------------------------------------------
    ! Only Layers-1, i.e. except the lower boundary calculation
    !----------------------------------------------------------------------------
    DO K = 1, NNL - 1
       DO JL = 1, ngrpts
          IF (.NOT. mask(jl)) CYCLE
          IF (COSZEN(JL).GE. ZenithMinPar) THEN
             !----------------------------------------------------------------------------
             ! p2=1/p1
             !----------------------------------------------------------------------------
             ZP0 = 1._dp / ZP1(JL)
             !----------------------------------------------------------------------------
             ! EXP(-k*l/fc)
             ! with l=LAI*DDL(K), i.e. l is element of [0,LAI], i.e. 0,LAI/3,2LAI/3,LAI
             !----------------------------------------------------------------------------
             EKL0 =  EXP(-K0(JL) / FSHD(JL) * DDL(K) * PLAI(JL))
             !----------------------------------------------------------------------------
             ! EXP(-h*l/fc)
             !----------------------------------------------------------------------------
             EHL0 = EXP(-ZH(JL) / FSHD(JL) * DDL(K) * PLAI(JL))
             !----------------------------------------------------------------------------
             ! R(D(JL))+ Rdown(D(JL))- Rup(D(JL))=
             !      (1-q1-q2)*R0*EXP(-kl)+(1-p1)*B1*EXP(hl)+(1-p2)*B2*EXP(-hl)
             !  i.e. X0*RPAR = above
             !----------------------------------------------------------------------------
             X0 = (1._dp - Q0(JL) - Q1(JL)) * EKL0 * FDIR(JL) &
                  + (1._dp - ZP1(JL)) * B1(JL) / EHL0 &
                  + (1._dp - ZP0) * B0(JL) * EHL0
             !----------------------------------------------------------------
             ! APAR(JL) = (R(D(JL-1))+Rdown(D(JL-1))-Rup(D(JL-1)) - R(D(JL))+
             ! Rdown(D(JL))-Rup(D(JL)) / ((D(JL)-D(JL-1))
             ! Here APAR only the nominator; the division is made outside FAPARL
             !---------------------------------------------------------------
             APAR(JL,K) = B4(JL) - X0
             !---------------------------------------------------------------
             ! Partition evenly LAI, LAIL=LAI/3
             !             LAIL(JL,K) = (DDL(K) - DDL(K-1)) * PLAI(JL)
             ! R(D(JL-1))+Rdown(D(JL-1))-Rup(D(JL-1) in next step
             !---------------------------------------------------------------
             B4(JL) = X0
          ENDIF ! mue>0.001
       ENDDO   ! VEGLIST
    ENDDO     ! # canopy layers - 1

    !---------------------------------------------------------------
    ! Now the same for the last layer
    !---------------------------------------------------------------
    DO jl = 1, ngrpts
       IF (.NOT. mask(jl)) CYCLE
       IF (COSZEN(JL).GE. ZenithMinPar) THEN
          !-------------------------------------------------------------
          ! R(D(NL))+ Rdown(D(NL))- Rup(D(NL))=
          !      (1-q1-q2)*R0*EXP(-kLAI)+(1-p1)*B1*EXP(hLAI)+(1-p2)*B2*EXP(-hLAI)
          !  i.e. X0*RPAR = above for the lower boundary
          !------------------------------------------------------------
          X0 = (1._dp - Q0(JL) - Q1(JL)) * EKL(JL) * FDIR(JL) &
               + (1._dp - ZP1(JL)) * B1(JL) / EHL(JL) &
               + (1._dp - ZP0) * B0(JL) * EHL(JL)
          !------------------------------------------------------------------
          ! APAR(NL) = (R(D(NL-1))+Rdown(D(NL-1))-Rup(D(NL-1)) - R(D(NL))+
          ! Rdown(D(NL))-Rup(D(NL)) / ((D(NL)-D(NL-1))
          ! Here APAR only the nominator; the division is made outside FAPARL
          !------------------------------------------------------------------
          APAR(JL,NNL) = B4(JL) - X0
       ENDIF                                                   ! mue>0.001
    END DO                                                     ! nproma

    !!------------------------------------------------------------
    ! Multiplication of APAR with fc because D(JL)-D(JL-1) 
    ! division is made outside FAPARL and is still the old l ???
    !------------------------------------------------------------
    DO K = 1, NNL
       DO JL = 1, ngrpts
          IF (.NOT. mask(jl)) CYCLE
          IF (COSZEN(JL).GE. ZenithMinPar) APAR(JL,K)=APAR(JL,K)*FSHD(JL)
       ENDDO
    ENDDO
    RETURN
  END SUBROUTINE FAPARL

end module mo_bethy_fapar
