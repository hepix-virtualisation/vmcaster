Vmcaster is a simple tool for managing and updating your published 
virtual machines image lists. Following the Hepix image list format.

Users of this application should read "security-related policy requirements for 
the generation and endorsement of trusted virtual machine (VM) images for use on 
the Grid". The URL is shown below.

   https://edms.cern.ch/document/1080777

This tool is designed to aid "endorsers" as defined in the security policy, 
and anyone who wants to publish virtual machine images in a way where 
tampering will be detected.

vmcaster was designed with the realisation that users typically create new 
virtual machines images rarely but update them frequently. Vmcaster attempts 
to be the first of a new generation of image list publishers the minimise the 
data entry for updating images, with imagelists.

The tasks of updating an image and uploading a fresh signed image is now just 
two quiet short command line operations away. The aim is to make image and 
imagelist updates as painless as possible as these are the most common 
tasks.

Internally the application uses a simple sql database, sqlight for storing 
image lists and multiple back ends managing uploading of images / images lists 
using a facade pattern. This allows transfer protocol to be derived from the 
meta data of the image list and a configuration file, updates need much less 
effort.


Quick Start
===========


Please note this application has online help.

     $ vmcaster --help

This will always have an up to date list of command line options and state if they take parameters.

Background
----------

An image list contains an array of images and an array of endorsers. Imagelists 
Images and Endorsers can all have key value pair attributes. Some of these attributes are 
required in every imagelist. Similarly Endorsers and Images have a set of required meta data. Every 
Imagelists must have an endorser, but no images is allowed.

The easiest way to start playing with image list publishing is to copy some one else's hard work.

    $ wget https://cernvm.cern.ch/releases/image.list \
        --no-check-certificate -o CernVM.list.smime

This is a large image list from the CernVm project. I provides a lot of images in a lot of formats 
so as many customers as possible benefit from the CernVM project. We should now import the 
image list.

    $ vmcaster  \
         --import-imagelist-smime CernVM.list.smime

To check the image has been imported correctly we can use the command:

    $ vmcaster  --list-imagelist
   
To list the endorsers,

    $ vmcaster  --list-endorser

to list images:

    $ vmcaster  --list-image

To display the imagelist:

    $ vmcaster  \
       --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
       --show-imagelist 

Imagelist Object's "dc:identifier" is a special property of an imagelist, this 
is the object identifier and can be used to select items for creation, deletion 
or modification. Each Object has an Identifier, the Endorser object identifier 
is the value corresponding with "hv:dn". Image Objects identifier is the same as 
an that of Imagelist "dc:identifier". 

UUID's are used for the imagelist "dc:identifier" and also
images "dc:identifier". These UUID's should be globally unique and consequently 
the UUID should be generated using a UUID generator using suitable seeds. With 
Debian I use the following UUID generator.

    $ uuidgen 
    70d9816a-2f6b-4aea-9412-16716b7539b7

To show image meta data:

    $ vmcaster  \
        --select-image b36d8b24-c63c-4fd1-ba13-bda6877207e8 \
        --show-image

To show endorser meta data:

    $ vmcaster  \
        --select-endorser "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic" \
        --show-endorser

To create an Endorser:

    $vmcaster  \
        --select-endorser "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge" \
        --add-endorser

To create an image:

    $ vmcaster  \
        --select-image  e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
        --add-imagelist

To create an image:

    $ vmcaster  \
        --select-image  e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
        --add-image

To delete and Endorser:

    $ vmcaster  \
        --select-endorser "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge" \
        --del-endorser

To delete an image:

    $ vmcaster  \
        --select-image  e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
        --del-image

To delete an image:

    $ vmcaster  \
        --select-image  e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
        --del-image


To add an image to a image list:

    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2  \
        --imagelist-add-image \
        --select-image 3a1df02c-121a-461d-b720-521903ef99f0

To remove an image from the image list:

    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2  \
        --imagelist-del-image \
        --select-image 3a1df02c-121a-461d-b720-521903ef99f0

To add an endorser to a image list:

    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2  \
        --imagelist-add-endorser \
        --select-endorser "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge"

To remove an image from the image list:

    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2  \
        --imagelist-del-endorser \
        --select-endorser "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge"

To change or add meta data to an :endorser

    $ vmcaster  \
        --select-endorser  "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge" \
        --key-set-imagelist "hv:ca"    \
        --key-value-imagelist "/DC=ch/DC=cern/CN=CERN Trusted Certification Authority" 

To change or add meta data to an imagelist:

    $ vmcaster  \
        --select-imagelist e38a3fd2-0ed8-11e2-873a-001cc0beb420  \
        --key-set-imagelist "dc:description"        --key-value-imagelist "DESY Image List SHaring service" 

To change or add meta data to an image:

    $ vmcaster   \
        --select-image "2934ec2b-7a67-4b96-ba16-6775d66898d0"    \
        --key-set-image "hv:uri" \
        --key-value-image "https://cernvm.cern.ch/releases/17/cernvm-desktop-2.6.0-4-1-x86.vpc.gz" 


To delete meta date from :endorser

    $ vmcaster  \
        --select-endorser  "/C=DE/O=GermanGrid/OU=DESY/CN=Owen Synge" \
        --key-del-endorser "hv:ca"    

To delete meta date from imagelist:

    $ vmcaster  \
        --select-imagelist e38a3fd2-0ed8-11e2-873a-001cc0beb420  \
        --key-del-imagelist "dc:description" 

To delete meta date from image:

    $ vmcaster   \
        --select-image "2934ec2b-7a67-4b96-ba16-6775d66898d0"    \
        --key-del-image "hv:uri" 


Object identifiers cannot be modified with vmcaster, they can only be created 
and destroyed,. This is intentional to prevent accidental errors.

Imagelists with clashing  "dc:identifier" value is considered disruptive at 
best and hostile at worst, and it will be noticed by imagelist subscribers. 
Similarly not having your endorser details correctly is stated in the endorser.

To change "dc:identifier" this we need to dump the imagelist to file, change 
the imagelist UUID, all images we wish to keep 

    
    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
        --show-imagelist > output.json
    $ OLD_LIST_UUID=e55c1afe-0a62-4d31-a8d7-fb8c825f92a2
    $ NEW_LIST_UUID=`uuidgen`
    $ sed -e "s/${OLD_LIST_UUID}/${NEW_LIST_UUID}/" \
        output.json  > input.json
    $ vmcaster --import-imagelist-json input.json

It might be easiest to edit the JSON with a conventional text editor. As you 
also want to change many other variables. Note that the new UUID is generated 
using a UUID generator.

It is recommended that only experienced users with good reason share images 
between  imagelists (primarily disk space and as part of automation). For this 
reason while editing the  JSON. So it is probably wise to change all Image object 
identifiers ("dc:identifier" for each image.).

All changes to the original imagelist can be reverted by re - importing an 
imagelist previously stored as a JSON file.

    $ vmcaster --import-imagelist-json input.json

To Add an image to a image list:

    $ vmcaster  \
        --select-imagelist e55c1afe-0a62-4d31-a8d7-fb8c825f92a2  \
        --imagelist-add-image \
        --select-image 3a1df02c-121a-461d-b720-521903ef99f0
       
The final setting up task is now to set up the configuration file.

Configuration file.
-------------------

The configuration file for vmcaster is used to define the hosts and parameters 
needed to update images and imagelists on the servers publishing the image list.

The configuration file is expected system wide at "/etc/vmcaster/vmcaster.cfg" or per 
user at "~/.vmcaster.cfg". The image list is in ini/cfg format with all values being 
stored as json. Each section will map to one or more image lists and provides the 
necessary information to "vmcaster" to update and upload image lists.

The following section is taken from my image list management configuration.

    [dish.desy.de]
    server = "dish.desy.de"
    writeprotocol = "gsidcap"
    uriMatch = "https://dish.desy.de:2880/"
    uriReplace = "gsidcap://dcache-desy-gsidcap.desy.de:22128/pnfs/desy.de/desy/vmimages/"

This states that all image lists to be published on the server "dish.desy.de",
should be updated using the "gsidcap" protocol, and that all writes corresponding 
with a prefix of "https://dish.desy.de:2880/" should be updated using a prefix of
"gsidcap://dcache-desy-gsidcap.desy.de:22128/pnfs/desy.de/desy/vmimages/". The 
section name is not significant and is just to group the attributes.

The following write protocols are currently supported: "scp" this is the standard 
file transfer tool from the openssh project. 

"gsidcap" for a long time this was the standard POSIX like write protocol for a file 
storage server called dCache which specialises in storing very large quantities of 
data at the lowest price possible. The following example is working but publishes 
files locally.

    [foo]
    server = "gridvirt.desy.de"
    writeprotocol = "local"
    uriMatch = "https://gridvirt.desy.de/"
    uriReplace = "/tmp/"

Note: Publishing an Imagelist without any images is the best way to decommission an
imagelist when no images are expected to be requested ever again.

To update an Image:
-------------------

Now we can select an image to and update it.

    $ vmcaster \
        --upload-image /var/lib/libvirt/images/hudson-slave-vm06.desy.de.img \
        --select-image 7b1aea46-8776-4447-9450-00e720fc042c
   
Shows the image list as it would be made.

    $ vmcaster \
        --select-imagelist 9b6fad19-d913-4cca-b77d-c4b4fcd9dc36  \
        --imagelist-show
      
which should now have the "hv:uri" set to the correct path to download the image
that was just updated, including the "sl:sha512" is now set and the value of 
"hv:version" has incremented the version number. 
Once you are happy with the new image list, it is time to publish this.


To update an ImageList:
-----------------------

First check the image list is as you expect:

    $ vmcaster \
        --select-imagelist 9b6fad19-d913-4cca-b77d-c4b4fcd9dc36  \
        --imagelist-show


To update and sign image list.

    $ vmcaster \
        --select-imagelist 9b6fad19-d913-4cca-b77d-c4b4fcd9dc36 \
        --upload-imagelist

To list stored imagelists.

    $ vmcaster  --imagelist-list    

Environment Variables.
----------------------

* HOME

Used as a prefix for configuration files and certificates.

* DISH_KEY

Path to the private key for the signing of image lists.

* DISH_CERT

Path to the certificate for the signing of image lists.

* DISH_CFG

Path to the configuration file for vmcaster.

* DISH_RDBMS

Sqllight based connection string, Typically defaulting to 'sqlite:///dish.db'.
This URL refers to the current working directory, to use an absolute path with 
Sqlight, add an extra slash to the URL like syntax.

* DISH_LOG_CONF

vmcaster uses pythosn standard logging module, this sets the configuration file 
to be used for logging. For specifications on how to set this up see the python
logging documentation.

* DISH_X509_DIR

Sets the default directory for the users x.509 certificates. If not set this 
value is defaulted to "$HOME/.globus".

* DISH_X509_KEY

Sets the default path for the users x.509 user key. If not set this 
value is defaulted to "$HOME/.globus/userkey.pem".

* DISH_X509_CERT

Sets the default path for the users x.509 user key. If not set this 
value is defaulted to "$HOME/.globus/usercert.pem".


Road map
--------

The code should also be publishable into a message Queue service provided by a 
cloud provider allowing unpublished images to be shared. This work has not been 
started.

Appendix
--------

If this application is not suitable for your use case it should not be forgotten that 
SMIME and json are common standards and can be created in many ways. Below is an 
example of how to sign a message using SMIME.

    $ openssl smime her-cert.pem -encrypt -in my-message.txt
   
This may prove useful in the long term.
