# Python setup

You need to use Python for several of the practicals. You've verious options for this.

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

If you have got to that point The first time you are using these notes, you should go through the items below. These are needed to set up the notes and various course settings.

1. In the Terminal (shell), type:

        cd ~ && git clone git://github.com/UCL-EO/geog0133
    
   This will clone this repository and set up the Python. 
    
2. Set up anaconda. In the Terminal (shell), type:

        conda init
        conda config --prepend envs_dirs /shared/groups/jrole001/geog0111/envs
        echo "conda activate geog0133" >> ~/.bashrc
        
    Then, type `bash` and in the new shell you enter, type:
    
        conda env list
        
    This should now show:
    
        # conda environments:
        #
        base                     /opt/miniconda-jhub/4.8.3
        jhubcode                 /opt/miniconda-jhub/4.8.3/envs/jhubcode
        geog0133              *  /shared/groups/jrole001/geog0111/envs/geog0133
        
 
     If that isn't the case, try opening a shell again, and/or stop and restart the notebook server (see 5. below)

3. Now, set up notebook extensions by running the following in shell (Terminal):

        cd ~/geog0133/docs && ./postBuild
        
4. Finally, make sure the kernel you need for the notebooks exists:
    
        python -m ipykernel install --name=conda-env-geog0133  --display-name 'conda env:geog0133' --user
        
5. This should all be good to go now, but you should make sure that the new settings have taken place by stopping are restarting the notebook server. To do this:

   * click on the `Control Panel` button at the top right of the notebook page. 
   * then click the big red button to stop the server
   * next, click `start my server` to restart (you may have to also then click `launch my server`)
   * if you are asked to choose an interface, choose `classic`, then click `start`

You should now see the link `geog0133` in the JupyterHub browser. Select that link to enter the course materials, then go to `docs/notebooks` to see the practical notebooks.

Select the first of these, `005_Solar_Practical.ipynb` and run the cell `In [1]`:

    import numpy as np
    import matplotlib.pyplot as plt
    from geog0133.solar import solar_model,radiation
    import scipy.ndimage.filters
    from geog0133.cru import getCRU,splurge
    from datetime import datetime, timedelta
    # import codes we need into the notebook

If that works fine (i.e. doesn't come up with an  error) then you have set things up correctly. 

If the problem you get is that the notebook kernel cannot be found, try the following:

    conda activate geog0133
    python -m ipykernel install --name=conda-env-geog0133  --display-name 'conda env:geog0133' --user

If not, try logging out (of all shells and notebooks) again, log in again and re-check.
    
If you get `ModuleNotFoundError: No module named 'ephem'`, then you have not got the `geog0133` running for some reason. Log out and in again. Then try the solution above for if the notebook kernel cannot be found. If that test doesn't run, the practical won't run, so make sure to fix that first. Once you have it properly configured, it should work all other times you log in.

If other issues, contact the [course convenor](mailto: p.lewis@ucl.ac.uk?subject=[geog0133 setup problem]), sending them exactly what you typed and the response you get when typing these commands.

Another way you can access this directory, should you need, is to use `ssh` to log in from a terminal to the UCL system (`ssh username@socrates.ucl.ac.uk`). 

### Summary for running on UCL JupyterHub

1. Make sure you have the [UCL VPN](https://www.ucl.ac.uk/isd/services/get-connected/ucl-virtual-private-network-vpn) installed and running OR that you are running from [Desktop@UCL](https://www.ucl.ac.uk/isd/services/computers/remote-access/desktopucl-anywhere)
2. Log on the the [UCL JupyterHub](https://jupyter.data-science.rc.ucl.ac.uk/).
3. Navigate to the directory `geog0133/docs/notebooks`
4. Access the notebooks you want directly

## Use Python on your own computer

You can run these practicals locally on your own computer. The only problemn is that it is more copmnplicated for us to support any comnputing iussues you might have, which is why we suggest you use the UCL system.

However, it it is not so hard to set things up and to run  it for yourself.

### Install Python

Whilst you *can* probably use any version of Python, we suggest you install [`Anaconda Python`](https://docs.anaconda.com/anaconda/install/). If you are very short on computer space, you might prefer the cut-down version [`Miniconda`](https://docs.conda.io/projects/continuumio-conda/en/latest/user-guide/install/macos.html).


### Clone the repository

The code repository is on [github](https://github.com/UCL-EO/geog0133), so we need to pull a local copy. 

You can do this in several ways:

* Using `PyCharm` and `Anaconda Navigator` (if you installed Anaconda)
* Using `GitHub Desktop`
* Using `git` in a shell

####  Using `PyCharm` and `Anaconda Navigator`

We do not support this here, but you will find various online notes if you want to follow thbis path.

#### Using `GitHub Desktop`

If you are using MacOS or Windows, you can use the tool [`GitHub Desktop`](https://desktop.github.com) to manage your github repositories. 

Download and install the tool. Then run it.

Use the menu item `File -> Clone Repository` and enter `UCL-EO/geog0133` under the `GitHub.com` tab. So long as you haven't done this before, you should be able to hit the `Clone` buytton for the cloning to take place. Take note of where the repoisitory will be placed on your comnputer, e.g. `/Users/plewis/Documents/GitHub/geog0133`.

Any time we update the repository, you just need to click `Fetch origin` to update.

After this point, just follow the same instructions as for using `git` directly at the section `Setting up the environment`.

#### Using `git`

Make sure you have `git`. If you type:


    which git


and it does not print anything, then you probably haven't got `git` installed. You may be able to install it with:

    conda install git

or alternatively, search on the web for an installation of `git` for your operating system.

Clone  the repository. First, choose a location where you want to put it, and `cd` there:

    mkdir -p ~/Documents/GitHub
    cd ~/Documents/GitHub

Clone:

    git clone git://github.com/UCL-EO/geog0133.git

This will now have set up the directory `geog0133`. If you type:

    ls geog0133

You should see:

    Install.md		bin			requirements.txt
    LICENSE			docs
    README.md		readthedocs.yml


##### Setting up the environment

Assuming you have cloned the repository though, now open a shell (Terminal) and type:

    cd ~plewis/Documents/GitHub/geog0133/docs

replacing `~plewis/Documents/GitHub/geog0133` with the location of your repository.

Then, set up the environment with:

    conda env create  --force -n geog0133 -f environment.yml

This will take a few minutes, but will create the environment `geog0133` which contains all of the libaries you need for this course.

Now, activate it:

    conda activate geog0133

Next, we need to set up the correct kernel for the notes:

    python -m ipykernel install --name=conda-env-geog0133  --display-name 'conda env:geog0133' --user
    
Next run the post-build configuration script (sets up itens for Jupyter notebooks):

    ./postBuild 

Now start Jupyter:

    jupyter notebook

This may open a browser window for you, or might just instruct you to copy and paste a URL, e.g.:

    http://127.0.0.1:8888/?token=4afdc076ec49592ca1059d957f0bccbce86e17ab838f61e0


Make sure you have the Jupyter window running in the browser.

Navigate to `docs/notebooks` and start the notebook `005_Solar_Practical.ipynb` (click on it in the browser).

Now, run the cell `In [1]:` to test that the required codes load correctly.

If there is a problem, go back over the steps above. If you still can't solve the problems, try connecting by a different route, and/or and contact the [course convenor](mailto: p.lewis@ucl.ac.uk?subject=[geog0133 setup problem]), explaining exactly what you did and what the problem was.

## Use Binder

If you only want to run the practicals, and not save the results, you can use the links to the Binder service to run the notebooks. Links are given to the exercises, and to answers.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCL-EO/geog0133/HEAD?filepath=docs%2Fnotebooks_lab%2F005_Solar_Practical.ipynb)
    
    
[![Answers](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCL-EO/geog0133/HEAD?filepath=docs%2Fnotebooks_lab%2F005_Solar_Practical_answers.ipynb)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCL-EO/geog0133/HEAD?filepath=docs%2Fnotebooks_lab%2F011_Photosynthesis_Modelling_Practical.ipynb) 
    
[![Answers](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/UCL-EO/geog0133/HEAD?filepath=docs%2Fnotebooks_lab%2F011_Photosynthesis_Modelling_Practical_answers.ipynb) 
