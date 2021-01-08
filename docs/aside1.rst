A simple Earth model
====================

Here, we develop a simple 'zero-dimensional' model of the climate system. Whilst this clearly lack many of the processes we know are important for understanding climate, it does demonstrate some fundamental principles, based on concepts of radiative equilibrium.

Some interesting additional reading to this exercise would be the `AIP essay on Simple Models of Climate Change <http://www.aip.org/history/climate/simple.htm>`_

* Assume the incoming solar radiation (radiative flux) is 342 Wm-2.
* Assume that 31% of this is reflected back to space.
* Assume the temperature T (K) of the Earth is constant over its surface and that it radiates as a blackbody.
* We can then use the Stefan-Boltzmann law to give the radiative flux emitted by the Earth to balance the incoming radiation:
    J = sigma T^4, where J is the emitted radiative flux (Wm-2) from the blackbody and sigma is the Stefan-Boltzmann constant, 5.670400 x 10-8 Js-1m-2T-4.
    We can then calculate the effective temperature of the Earth (in python) as:

::

    albedo = 0.31
    Jin = 342.0
    
    def earthModel(albedo,Jin):
        '''
        A simple earth system model to give the effective 
        planetary temperature (C)
        '''
        # stefan-boltzmann constant
        sigma = 5.670400e-8
        Jout = Jin*(1-albedo)
        T = (Jout/sigma)**(1/4.)
        # return temperature in C
        return T-273.15
    
    print earthModel(albedo,Jin)
    

::

    -19.1607268563
    



**Exercise 1**

* Use this model to show what the sensitivity of the temperature is to albedo and the incoming solar radiation.
* what factors would cause variations in these terms?

**Exercise 2**

A grey body radiator is less efficient at emitting radiation than a blackbody. Such a concept is easily incorporated into the Stefan-Boltzmann law using an emissivity term epsilon, so J = epsilon sigma T^4.

* Assuming the actual average surface temperature is around 14 C, modify the code above to return the *effective emissivity* of the Earth.
* We assumed above that the effective (broadband) shortwave albedo was 0.31, so the effective (broadband) shortwave absorptance is 1-0.31=0.69. The effective (broadband) longwave absorptance is equal to the effective (broadband) longwave emissivity through `Kirchoff's law (of thermal radiation) <http://en.wikipedia.org/wiki/Kirchhoff%27s_law_of_thermal_radiation>`_, assuming thermal equilibrium. What then is the effective (broadband) longwave albedo?
* Why do we use the words *effective* and *broadband* above?
* What impact would increasing the concentrations of greenhouse gases have on the effective (broadband) longwave albedo?
