class bethy_fapar:

 def __init__(self):
  self.omega = 0.12 # single leaf scattering albedo
  self.fcmax = 0.9 # Maximum fractional vegetation cover
  self.fcmin = 1e-3 # Minimum fractional vegetation cover
  self.zenithminpar = 1e-3
  self.zenithmin = 0.0174524
  self.laimin = 1.e-9
  self.lailimit = 3.
  self.laimax = 8.

 def faparl(self,ngrpts, mask, nnl\
       , plai, rhos \
       , coszen, fdir \
       , ddl):
  '''
 !---------------------------------------------------------------------------------
  !
  !  faparl[] computes the leaf area index per canopy layer [lail] and the absorbed
  !  photsynthetic active radiation [apar] from total lai and direct irradiation.
  !
  !---------------------------------------------------------------------------------
  subroutine faparl[ngrpts, mask, nnl &
       , plai, rhos &
       , coszen, fdir &
       , ddl  &
       , lail, apar &
       ]

    use mo_bethy_constants,       only: self.fcmax, self.fcmin, self.zenithminpar, self.laimin, self.lailimit

    !-----------------------------------------------------------------------
    ! on entry:
    !   plai   : total lai
    !   fc     : canopy fraction
    !   fcmax  : maximum canopy fraction [0.9]
    !   rhos   : soil albedo
    !   coszen : cosine of solar zenith angle, mue
    !   fdir   : direct part of total irradiance [e.g. 0.8]
    !   self.omega  : single leaf scattering albedo = 0.12
    !   ddl    : leaf layer borders in units of lai [0, 1/3, 2/3, 1]
    !   zlmin  : minimum lai or lai per layer [1e-6]
    !   nnl    : # of canopy layers
    !   n      : # of longitude, dimension of the in and output fields
    ! on exit:
    !   lail   : lai per canopy layer
    !   apar   : the absorbed par per leaf aera per canopy layer
    !            normalized to incoming radiation = 1
    !------------------------------------------------------------------------
    integer,  intent[in]  ::   ngrpts           ! number of grid points to be handled in this call
    logical,  intent[in]  ::   mask[ngrpts]
    integer,  intent[in]  ::   nnl              ! number of canopy layers
    real[dp], intent[in]  ::   plai[ngrpts]     ! total lai
    real[dp], intent[in]  ::   rhos[ngrpts]     ! soil albedo
    real[dp], intent[in]  ::   coszen[ngrpts]   ! cosine of solar zenith angle, 
    real[dp], intent[in]  ::   fdir[ngrpts]     ! direct part of total irradiance [e.g. 0.8]
    real[dp], intent[in]  ::   ddl[0:nnl]       ! canopy layer borders in units of lai [0, 1/3, 2/3, 1]
    real[dp], intent[out] ::   lail[ngrpts,nnl] ! lai per canopy layer
    real[dp], intent[out] ::   apar[ngrpts,nnl] ! the absorbed par per leaf aera and per canopy layer, ...
                                                ! ... normalized to incoming radiation = 1.
    !---------------------------------------------------------------------
    ! local variables
    !---------------------------------------------------------------------
    real[dp]       :: zh[ngrpts], k0[ngrpts], zp0, zp1[ngrpts]
    real[dp]       :: q0[ngrpts], q1[ngrpts], b0[ngrpts], b1[ngrpts]
    real[dp]       :: ekl[ngrpts], ehl[ngrpts], ekl0, ehl0, b4[ngrpts]
    real[dp]       :: fc[ngrpts] ! fractional vegetation cover
    real[dp]       :: x0, x1, x2, f, fshd[ngrpts]
    integer    :: jl, k
    '''
  lail = 0.
  apar = 0.
  '''
    !----------------------------------------------------------------------------
    ! compute fractional vegetation cover  per grid cell and pft 
    ! [not the same as fractional cover in jsbach!]    
    !----------------------------------------------------------------------------
  '''
  fc = plai*0. + self.fcmax
  fc[plai< self.lailimit] = plai[plai< self.lailimit] / self.lailimit * self.fcmax
  ''' 
  !----------------------------------------------------------------------------
    !     compute absorbed par per leaf area [!] and plai partitioning   
    !----------------------------------------------------------------------------
    ! initialize absorbed par per leaf area,  if coszen[jl]<1e-3
    ! spread lai equally around the three layers
    !----------------------------------------------------------------------------
  '''
  apar = np.zeros(ngrpts,nnl)
  '''
    do k = 1, nnl
       do jl = 1, ngrpts
          if [.not. mask[jl]] cycle
          apar[jl,k] = 0.
          !------------------------------------------------------------
          !             lail[jl,nnl] = [ddl[nnl] - ddl[nnl-1]] * plai[jl]
          !------------------------------------------------------------
          lail[jl,k] = plai[jl] * [ddl[k] - ddl[k-1]]
          lail[jl,k] = max[lail[jl,k], self.laimin]
       enddo
    enddo
  '''
  for k in range(nnl):
   for jl in range(ngrpts):
    lail[jl,k] = plai[jl] * (ddl[k] - ddl[k-1])
  lail[lail < self.laimin] = self.laimin
  '''
    !--------------------------------------------------------------------
    ! the absorbed par per laef area which is used later for the net assimilation,
    ! is calculated via the two stream approximation of sellers [1985]:
    !  muq * d[rdown]/dl + [1-[1-b]*omega]*rdown - omega*b*rup   = omega*muq*k*[1-b0]*r
    ! -muq * d[rup]/dl   + [1-[1-b]*omega]*rup   - omega*b*rdown = omega*muq*k*b0*r
    !  with
    !   rdown - downwards diffusive flux
    !   rup   - upwards diffusive flux
    !   r     - direct flux, with r[0] = dpar * rpar with rpar incoming irridiance in par
    !           and r = r0 * exp[-kl] with r0=r[0] - exponential extinction law of 
    !           monsi and racki [1953]
    !           or similar lambert-beer's law
    !   b     - forward scatter fraction of diffusive flux
    !   b0    - forward scatter fraction of direct flux
    !   k     - extinction coefficient for the direct flux
    !   muq = int[1/k[mu]]dmu|_0^1 - the integral of 1/k over the downward hemisphere
    !   omega - the single leaf albedo
    !
    !  the general solutions are [kl,hl=k*l,h*l]:
    !  rup   = q2*r0*exp[-kl] + p1*b1*exp[hl] + p2*b2*exp[-hl]
    !  rdown =-q1*r0*exp[-kl] +    b1*exp[hl] +    b2*exp[-hl]
    !   with
    !    h  = sqrt[ [1-[1-b]*omega]^2/muq^2 - omega^2*b^2/muq^2 ]
    !    p1 = [ [1-[1-b]*omega] + muq * h ]/omega/b
    !    p2 = [ [1-[1-b]*omega] - muq * h ]/omega/b
    !   -q1 = [omega^2*b*muq*k* [1-b0] + omega*    b0  *muq*k*[1-[1-b]*omega - muq*k]]/
    !         [[1-[1-b]*omega]^2-muq^2*k^2-omega^2*b^2]
    !    q2 = [omega^2*b*muq*k*    b0  + omega* [1-b0] *muq*k*[1-[1-b]*omega + muq*k]]/
    !         [[1-[1-b]*omega]^2-muq^2*k^2-omega^2*b^2]
    !    b1/b2 from boundary conditions
    !-------------------------------------------------------------------
    !  make two assumptions:
    !  1] the distribution of leaf angles is isotropic
    !  2] the leaf reflectivity and transmissivity are equal [the sum = omega]
    !  => b=0.5, b0=0.5, k=0.5/mu with mu=cos[theta] solar zenith angle => muq=1
    !
    !  => k  = 1/2/mu
    !     h  = sqrt[ 1 - omega ]
    !     p1 = [ 1-omega/2 + h ]/omega/2
    !     p2 = [ 1-omega/2 - h ]/omega/2
    !   ! p2 = 1 / p1 !
    !     q1 = [ [1 + 2*mu]*omega/2 ]/[1-4*mu^2*[1-omega]] = [ k*[k + 1]*omega/2 ]/
    !                                                        [k^2-1-omega]
    !     q2 = [ [1 - 2*mu]*omega/2 ]/[1-4*mu^2*[1-omega]] = [ k*[k - 1]*omega/2 ]/
    !                                                        [k^2-1-omega]
    !    
    ! determine b1 and b2 from the boundary conditions:
    !  1] rdown[0] equals the incoming diffuse radiation
    !     rdown[0] = [1-dpar]*rpar
    !  => rdown[0] + r[0] = [1-dpar]*rpar + dpar*rpar = rpar as total incoming par
    !  2] the reflection at the lower boundary of the canopy is given by the soil 
    !     reflectance
    !     rup[lai] = rhospar * [r[lai] + rdown[lai]]
    !  here: faparl gets rhospar as variable rhos, lai is the total canopy lai, plai
    ! 
    !  => b1 = + [ eta*r0 - [rd+q1*r0] * gamma2 ]/[gamma1 - gamma2]
    !     b2 = - [ eta*r0 - [rd+q1*r0] * gamma1 ]/[gamma1 - gamma2]
    !   with
    !     eta    = rhospar * [1-q1]-q2] * exp[-k*lai]
    !     gamma1 = [ p1 - rhospar] * exp[ + h*lai]
    !     gamma2 = [ p2 - rhospar] * exp[ - h*lai]
    !     rd     = rdown[0] = [1-dpar]*rpar
    !------------------------------------------------------------------
    ! that is the complete solution of the two stream approximation under the boundary
    ! conditions and assumptions mentioned above !!!!!!!!!!!!!!!!!!
    !
    ! therefore, the absorbed radiation inside the canopy is:
    !   apar = -d/dl [ r[l] + rdown - rup]
    !        = [1-q1-q2]*k*r0*exp[-kl] - [1-p1]*h*b1*exp[hl] + [1-p2]*h*b2*exp[-hl]
    ! but the absorbed par per canopy layer in discrete steps is:
    !   apar[jl] = 1/[d[jl]-d[jl-1]] * int[-d/dl[r[l] + rdown - rup]]dl|_d[jl]^d[jl-1]
    !            = [r[d[jl-1]] + rdown[d[jl-1]] - rup[d[jl-1]] - r[d[jl]] + rdown[d[jl]]
    !              - rup[d[jl]] / [[d[jl]-d[jl-1]]
    !  and  r[l]+rdown-rup = [1-q1-q2]*  r0*exp[-kl] + [1-p1]*  b1*exp[hl] + [1-p2] * 
    !                        b2*exp[-hl]
    !------------------------------------------------------------------
    ! the clumping of the vegetation is taken into account, defining laic = lai / fc
    ! as an effective lai.
    ! taken this into account, l = l/fc but the solutions stay as they are because 
    ! of the differentiations are take d/dl according to the new l=l/fc
    ! only apar has to be multiplied with fc at the end because d[jl]-d[jl-1] is still
    ! the old l
    !------------------------------------------------------------------
    do jl = 1, ngrpts
       if [.not. mask[jl]] cycle
       if [coszen[jl].ge. self.zenithminpar] then
    '''
  for jl in range(ngrpts):
   if coszen[jl] >= self.zenithminpar:
    '''
          !----------------------------------
          !  h = sqrt[ 1 - omega ]
          !----------------------------------
          zh[jl] = sqrt [1. - self.omega]
          !----------------------------------
          !  p1 = [ 1-omega/2 + h ]/omega/2
          !----------------------------------
          zp1[jl] = [1. - self.omega / 2. + zh[jl]] & 
               / self.omega * 2. 
          !----------------------------------------
          ! p2 = [ 1-omega/2 - h ]/omega/2 = 1 / p1
          !----------------------------------------
          zp0 = 1. / zp1[jl] 
    '''
    zh[jl] = np.sqrt (1. - self.omega)
    zp1[jl] = [1. - self.omega / 2. + zh[jl]] \
               / self.omega * 2. 
    zp0 = 1. / zp1[jl] 
    '''
          !----------------------------------
          ! k = 0.5/mu
          !----------------------------------
         
          k0[jl] = 0.5 / coszen[jl] 
          if [k0[jl].eq.zh[jl]] k0[jl] = k0[jl] + 1e-12
          if [k0[jl].eq.-zh[jl]] k0[jl] = k0[jl] + 1e-12
    '''
    k0[jl] = 0.5 / coszen[jl] 
    if k0[jl] == zh[jl]: k0[jl] = k0[jl] + 1e-12
    if k0[jl] == -zh[jl]: k0[jl] = k0[jl] + 1e-12
    '''
          !--------------------------------------------------------------
          ! denominator of q1 and q2
          !--------------------------------------------------------------
          x0 = [1. - 4. * coszen[jl]**2 * zh[jl]**2]
    '''
    x0 = (1. - 4. * coszen[jl]**2 * zh[jl]**2)
    '''
          !--------------------------------------------------------------
          ! q1 = [ [1 + 2*mu]*omega/2 ]/[1-4*mu^2*[1-omega]]
          !    = [ k*[k + 1]*omega/2 ]/[k^2-1-omega]
          !--------------------------------------------------------------
          q1[jl] = [[1. + 2. * coszen[jl]] &
               * self.omega / 2.] / x0
          !--------------------------------------------------------------
          ! q2 = [ [1 - 2*mu]*omega/2 ]/[1-4*mu^2*[1-omega]]
          !    = [ k*[k - 1]*omega/2 ]/[k^2-1-omega]
          !--------------------------------------------------------------
          q0[jl] = [[1. - 2. * coszen[jl]] &
               * self.omega / 2.] / x0
    '''
    q1[jl] = ((1. + 2. * coszen[jl]) \
               * self.omega / 2.) / x0
    0[jl] = ((1. - 2. * coszen[jl]) \
               * self.omega / 2.) / x0

    '''
          fshd[jl] = max [fc[jl], self.fcmin]
          !-----------------------------------------------------------
          ! exp[-k*lai/fc]
          !-----------------------------------------------------------
          ekl[jl] = exp[-k0[jl] / fshd[jl] * plai[jl]]
          !------------------------------------------------------------
          ! exp[-h*lai/fc]
          !-----------------------------------------------------------
          ehl[jl] = exp[-zh[jl] / fshd[jl] * plai[jl]]
          !-----------------------------------------------------------
          ! gamma1 = [ p1 - rhospar] * exp[ + h*lai]
          !----------------------------------------------------------- 
          x1 = [zp1[jl] - rhos[jl]] / ehl[jl]
          !-----------------------------------------------------------
          ! gamma2 = [ p2 - rhospar] * exp[ - h*lai]
          !-----------------------------------------------------------          
          x0 = [zp0 - rhos[jl]] * ehl[jl]
          !-----------------------------------------------------------
          ! eta = [rhospar * [1-q1]-q2] * exp[-k*lai]
          !-----------------------------------------------------------
          x2 = [rhos[jl] * [1. - q1[jl]] - q0[jl]] * ekl[jl]
    '''
    fshd[jl] = np.max (fc[jl], self.fcmin)
    ekl[jl] = np.exp(-k0[jl] / fshd[jl] * plai[jl])
    ehl[jl] = np.exp(-zh[jl] / fshd[jl] * plai[jl])
    x1 = (zp1[jl] - rhos[jl]) / ehl[jl]
    x0 = (zp0 - rhos[jl]) * ehl[jl]
    x2 = (rhos[jl] * (1. - q1[jl]) - q0[jl]) * ekl[jl]
    '''
          !------------------------------------------------------------
          ! f = 1 - dpar + dpar * q1
          ! => f*rpar = rd + q1*r0
          ! i.e. calculation takes rpar=1
          !-----------------------------------------------------------           
          f = 1. - fdir[jl] + q1[jl] * fdir[jl]
          !-------------------------------------------------------------
          ! b1[jl]*rpar = b1, b2[jl]*rpar = b2, b4[jl]*rpar = r[0] + rdown[0] - rup[0]
          !  b1 = + [ eta*r0 - [rd+q1*r0] * gamma2 ]/[gamma1 - gamma2]
          !------------------------------------------------------------
          b1[jl] = [x2 * fdir[jl] - f * x0] / [x1 - x0]
          !-----------------------------------------------------------
          !  b2 = - [ eta*r0 - [rd+q1*r0] * gamma1 ]/[gamma1 - gamma2]
          !     = eta*r0/[gamma2-gamma1] + [rd+q1*r0] / [1-gamma2/gamma1]
          !  note: the second form is used to avoid compiler-dependent ambiguity in the
          !        result of gamma1/[gamma1-gamma2] if gamma1 = infinity
          !-----------------------------------------------------------
          b0[jl] = x2 * fdir[jl] / [x0 - x1] + f / [1.0 - x0/x1]
          !-----------------------------------------------------------
          !  r[l]+rdown-rup = [1-q1-q2]* r0*exp[-kl] + [1-p1]* b1*exp[hl] + [1-p2]* b2*exp[-hl]
          !----------------------------------------------------------------------------
          b4[jl] = [1. - q0[jl] - q1[jl]] * fdir[jl] &
               + [1. - zp1[jl]] * b1[jl] + [1. - zp0] * b0[jl]
    '''
    f = 1. - fdir[jl] + q1[jl] * fdir[jl]
    b1[jl] = (x2 * fdir[jl] - f * x0) / (x1 - x0)
    b0[jl] = x2 * fdir[jl] / (x0 - x1) + f / (1.0 - x0/x1)
    b4[jl] = (1. - q0[jl] - q1[jl]) * fdir[jl] \
               + (1. - zp1[jl]) * b1[jl] + (1. - zp0) * b0[jl]

    '''
       endif                                                      ! mue>0.001
    end do                                                        !end nproma
    '''
    '''
    !------------------------------------------------------------
    ! only layers-1, i.e. except the lower boundary calculation
    !----------------------------------------------------------------------------
    do k = 1, nnl - 1
       do jl = 1, ngrpts
          if [.not. mask[jl]] cycle
          if [coszen[jl].ge. self.zenithminpar] then
     
    '''
    for k in range(nnl - 1):
     for jl in range(ngrpts):
      '''
             !----------------------------------------------------------------------------
             ! p2=1/p1
             !----------------------------------------------------------------------------
             zp0 = 1. / zp1[jl]
             !----------------------------------------------------------------------------
             ! exp[-k*l/fc]
             ! with l=lai*ddl[k], i.e. l is element of [0,lai], i.e. 0,lai/3,2lai/3,lai
             !----------------------------------------------------------------------------
             ekl0 =  exp[-k0[jl] / fshd[jl] * ddl[k] * plai[jl]]
             !----------------------------------------------------------------------------
             ! exp[-h*l/fc]
             !----------------------------------------------------------------------------
             ehl0 = exp[-zh[jl] / fshd[jl] * ddl[k] * plai[jl]]
             !----------------------------------------------------------------------------
             ! r[d[jl]]+ rdown[d[jl]]- rup[d[jl]]=
             !      [1-q1-q2]*r0*exp[-kl]+[1-p1]*b1*exp[hl]+[1-p2]*b2*exp[-hl]
             !  i.e. x0*rpar = above
             !----------------------------------------------------------------------------
             x0 = [1. - q0[jl] - q1[jl]] * ekl0 * fdir[jl] &
                  + [1. - zp1[jl]] * b1[jl] / ehl0 &
                  + [1. - zp0] * b0[jl] * ehl0
      '''
      zp0 = 1. / zp1[jl]
      ekl0 =  np.exp(k0[jl] / fshd[jl] * ddl[k] * plai[jl])
      ehl0 = np.exp(-zh[jl] / fshd[jl] * ddl[k] * plai[jl])
      x0 = (1. - q0[jl] - q1[jl]) * ekl0 * fdir[jl] \
                  + (1. - zp1[jl])* b1[jl] / ehl0 \
                  + (1. - zp0) * b0[jl] * ehl0
      '''
             !----------------------------------------------------------------
             ! apar[jl] = [r[d[jl-1]]+rdown[d[jl-1]]-rup[d[jl-1]] - r[d[jl]]+
             ! rdown[d[jl]]-rup[d[jl]] / [[d[jl]-d[jl-1]]
             ! here apar only the nominator; the division is made outside faparl
             !---------------------------------------------------------------
             apar[jl,k] = b4[jl] - x0
             !---------------------------------------------------------------
             ! partition evenly lai, lail=lai/3
             !             lail[jl,k] = [ddl[k] - ddl[k-1]] * plai[jl]
             ! r[d[jl-1]]+rdown[d[jl-1]]-rup[d[jl-1] in next step
             !---------------------------------------------------------------
             b4[jl] = x0
      '''
      apar[jl,k] = b4[jl] - x0
      b4[jl] = x0
      '''
          endif ! mue>0.001
       enddo   ! veglist
    enddo     ! # canopy layers - 1   
      '''
    '''
    !---------------------------------------------------------------
    ! now the same for the last layer
    !---------------------------------------------------------------
    do jl = 1, ngrpts
       if [.not. mask[jl]] cycle
       if [coszen[jl].ge. self.zenithminpar] then
    '''
    for jl in range(ngrpts):
     if coszen[jl] >= self.zenithminpar:
      '''
          !-------------------------------------------------------------
          ! r[d[nl]]+ rdown[d[nl]]- rup[d[nl]]=
          !      [1-q1-q2]*r0*exp[-klai]+[1-p1]*b1*exp[hlai]+[1-p2]*b2*exp[-hlai]
          !  i.e. x0*rpar = above for the lower boundary
          !------------------------------------------------------------
          x0 = [1. - q0[jl] - q1[jl]] * ekl[jl] * fdir[jl] &
               + [1. - zp1[jl]] * b1[jl] / ehl[jl] &
               + [1. - zp0] * b0[jl] * ehl[jl]
          !------------------------------------------------------------------
          ! apar[nl] = [r[d[nl-1]]+rdown[d[nl-1]]-rup[d[nl-1]] - r[d[nl]]+
          ! rdown[d[nl]]-rup[d[nl]] / [[d[nl]-d[nl-1]]
          ! here apar only the nominator; the division is made outside faparl
          !------------------------------------------------------------------
          apar[jl,nnl] = b4[jl] - x0
      '''
      x0 = (1. - q0[jl] - q1[jl]) * ekl[jl] * fdir[jl] \
               + (1. - zp1[jl]) * b1[jl] / ehl[jl] \
               + (1. - zp) * b0[jl] * ehl[jl]
      apar[jl,nnl] = b4[jl] - x0
      '''
       endif                                                   ! mue>0.001
    end do                                                     ! nproma
       '''
    '''
    !!------------------------------------------------------------
    ! multiplication of apar with fc because d[jl]-d[jl-1] 
    ! division is made outside faparl and is still the old l ???
    !------------------------------------------------------------
    do k = 1, nnl
       do jl = 1, ngrpts
          if [.not. mask[jl]] cycle
          if [coszen[jl].ge. self.zenithminpar] apar[jl,k]=apar[jl,k]*fshd[jl]
       enddo
    enddo
    '''
    for k in range(nnl):
     for jl in range(ngrpts):
      if coszen[jl] > self.zenithminpar:
       apar[jl,k]=apar[jl,k]*fshd[jl]
'''
    return
  end subroutine faparl

end module mo_bethy_fapar
'''
