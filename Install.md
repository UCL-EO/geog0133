# Python setup

You need to use Python for several of the practicals. You ve verious options for this.

1. Use the UCL JupyterHub
2. Use Python on your own computer
3. Use binder

We recommend you use the first of these, UCL JupyterHub as we can more easily work out any coding problems you have on that platform. 

However, it is not very difficult to up your own Python installation and to use that, should you so wish.

If you want to just run through the practicals without saving material, then you can just make straight use of the binder facility (online read-only but runnable versions of the practicals).

## Installation of these notes on UCL JupyterHub

This is the recommended option. You need internet access with reasonable reliability to use this, and you need to do a one-time setup of the course notes. After that, it should be easy to use. 

There are two main ways you can access the UCL JupyterHub:

i. through the UCL VPN
ii. through UCL Desktop 

Follow the instructions below to log in to UCL JupyterHub and open a shell. After that, we will set up the notes.

### Login using UCL VPN

First, set up and test the [UCL VPN](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn). This will take you some time to do if you haven't done it before, as it needs current virus definitions and has other requirements. Only proceecd if you have set up and tested the VPN. If you have problems with the VPN, contact [ISD](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn).

1. Make sure you have the [UCL VPN](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn) installed and running
2. Log on the the [UCL JupyterHub](https://jupyter.data-science.rc.ucl.ac.uk/) with your UCL credentials.
3. Open a shell (New->Terminal) on JupyterHub and follow the installation instructions below.


### Login using UCL Desktop

N.B. You do not need the VPN set up for this method.

1. In a browser, log on to UCL [DesktopAnywhere](https://www.ucl.ac.uk/isd/services/computers/remote-access/desktopucl-anywhere). Note, if you haven't done this before, it will take some time as it needs to download some software (or you can use the ['light' version](https://my.desktop.ucl.ac.uk/Citrix/StoreWeb/#)).
2. Open Desktop@UCL Anywhere and log in with your UCL credentialsi (this will take a few minutres to achieve). 
3. Open a browser in Desktop@UCL and log on the the [UCL JupyterHub](https://jupyter.data-science.rc.ucl.ac.uk/) with your UCL credentials. 
4. You may need to click on 'Launch Server' to start
5. You may need to 'choose your interface' before you can start (if so, select 'classic'), then click start
6. Open a shell (New->Terminal) on JupyterHub and follow the installation instructions below.

### Initial setup on UCL JupyterHub 

The first time you want to use these coursenotes on UCL JupyterHub, you need to do some setup 
f the materials and codes. You should have a terminal (shell) open on UCL JupyterHub at this point. You should see a still cursor at a prompt, probably on a blqack background shell. This is a unix (linux) shell where you can type unix commands. To execute a command, you hit the <return> key. Try that first, with the command:

    whoami

It should show you username (e.g. `ucfalew`)

Next check to see where you are on the system:

    pwd

It will show something like `/nfs/.../home3/Uucfa6/ucfalew` and should end with your username. This is you *home* directory. 

If you have got to that point (in your home directory in a shell):

To install and initialise the course, type:

    /shared/groups/jrole001/geog0111/init/init0133.sh

This will clone this repository and set up all files and links you need. Note that you only need to do this the one time. 

This will take a few minutes to run. If it runs sucessfully, it should tell you to close all shells and logout for the changes to take effect.

You can close the shell by typing 

    exit

or got to `Control Panel -> My Server`, select the `Running` tab, and shut down and terminals (or notebooks) from there.

Then logout (`Logout` button), and sign in again.

You should now see the link `geog0133` in the JupyterHub browser. Select that link to enter the course materials, then go to `docs/notebooks` to see the practical notebooks.

Select the first of these, `005_Solar_Practical.ipynb` and run the cell `In [1]`:

    import numpy as np
    import matplotlib.pyplot as plt
    from geog0133.solar import solar_model,radiation
    import scipy.ndimage.filters
    from geog0133.cru import getCRU,splurge
    from datetime import datetime, timedelta
    # import codes we need into the notebook

If that works fine (i.e. doen't come up with an  error) then you have set things up correctly. 

If not, try logging out (of all shells and notebooks) again, log in again and re-check.
If that still doesn't work, open a shell again on JupyterHub, and type:

    cd ~
    /shared/groups/jrole001/geog0111/init/init0133.sh

and contact the [course convenor](mailto: p.lewis@ucl.ac.uk?subject=[geog0133 setup problem]), sending them the response you get when running `init0133.sh`. 

Another way you can access this directory, should you need, is to use `ssh` to log in from a terminal to the UCL system (`ssh username@socrates.ucl.ac.uk`). 

### Summary for running on UCL JupyterHub

1. Make sure you have the [UCL VPN](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn) installed and running OR that you are running from [Desktop@UCL](https://www.ucl.ac.uk/isd/services/computers/remote-access/desktopucl-anywhere)
2. Log on the the [UCL JupyterHub](https://jupyter.data-science.rc.ucl.ac.uk/).
3. Navigate to the directory `geog0133/docs/notebooks`
4. Access the notebooks you want directly


