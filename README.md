<a name="readme-top"></a>


<h1 align="center">Moku:Lab Phasemeter Remote DAQ</h1>

  <p align="center">
    Python script for Moku phasemeter readout and data logging.
    <!--
    <br />
    <a href=""><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="">View Demo</a>
    ·
    <a href="">Report Bug</a>
    ·
    <a href="">Request Feature</a> -->
  </p>
</div>


<!--
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- GETTING STARTED -->
## Getting Started

Here we describe how to set up the environment and interface with the Moku. The main requirement is ```pymoku```, so this readme follows closely with their documentation which you can see <a href='https://github.com/liquidinstruments/pymoku'>HERE</a> to write your own scripts.

### Installation
How to setup the environment, although ```pymoku``` is the main requirement.

 - Download and unzip the repo.
 - ```cd``` into the app directory and install its dependencies from the ```mokuPython.yml``` in a virtual environment (here named ```mokuenv```) with e.g. conda and activate:
 
_With Anaconda (recommended):_

 ```
 conda env create -n mokuenv -f mokuPython.yml
 conda activate mokuenv
  ```
  The main requirement is the ```pymoku==2.8.3```.
  
 ### Moku Setup
 
 Installing Bonjour Libraries
To automatically discover Moku:Lab on your network (i.e. by name or serial) you must have Bonjour installed. Without Bonjour, your Moku:Lab will still be accessible by IP address, you just won't be able to automatically connect by name or serial number, or find it using moku list. To install Bonjour:

Windows install the <a href='https://support.apple.com/kb/DL999?locale=en_US'>Bonjour Printer Services</a>. 

  - Ethernet-wire the Moku to PC or local network.
  - Update your Moku:Lab with the latest firmware by typing the following in your terminal

    ```moku --serial=123456 update install```

The serial number is the middle six digits found on the underside of the Moku:Lab. For example: XXX-123456-X.

You can also update the Moku:Lab using its IP address with

    moku --ip=192.168.0.1 update install


The IP address of your Moku:Lab device can be found with

    moku list

**NOTE:** The update process is indicated by alternating orange and white lights, or a pulsing orange light. This process can take up to 30 minutes.

  - Use the IP address in the argument ```Moku(<address>)``` of the remote_acquire_moku_full_ds.py script. For us, these addresses were hard-coded and simply commented/uncommented when users wanted to switch Mokus:
```
# m = Moku('10.244.25.46') #-- Initialise connection to Moku. Blue moku 000661
m = Moku('10.244.25.34') #-- Black moku 000311
i=m.discover_instrument()
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Run the python script with:

 ```
 python remote_acquire_moku_full_ds.py <arg1> <arg2> <optional arg3> <optional arg4>
 ```
 
 The arguments here are:
  * arg1 : measurement time CH1
  * arg2 : comment
  * arg3 : anything... literally anything, it just initializes two-channel input if another arg follows...
  * arg4 : measurement time CH2
 
 Instrument selection and initialization happens via the following:
 ```
i = inst.Phasemeter()
m.deploy_instrument(i, set_default = True, use_external=True) 
m.take_ownership()

#-- Setting up PM parameters.
i.set_samplerate('veryslow') #-- PM sampling rate for data acquisition
fs = 30.5176
# i.set_samplerate('fast') #-- PM sampling rate for data acquisition
# fs = 500
i.set_bandwidth(1, 10000) 
i.set_frontend(1, fiftyr=True, atten = False, ac = True)
i.set_initfreq(1,10e6)
```
Again, you can write your own following the ```pymoku``` documentation.

## Data Logging
Will write this up later...

- Data is logged to a CSV by date, and in two files (one at 30Hz sample rate, and one decimated as "ReducedPhasemeterData" - example included):

```writepath = os.path.join(genpath,date)```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING 
## Contributing-->


<!-- LICENSE 
## License-->


<!-- CONTACT -->
## Contact

Paul Edwards - paul.edwards@ufl.edu

Project Link: [https://github.com/paul-edwards-UF/Lab-Dash](https://github.com/paul-edwards-UF/moku-python)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


