# Mount storage to instance -------------------------------------------------------

# Make sure that you have attached the EBS volume to your EC2 already
# In addition, make sure that it has been formatted to ext4  filesystem already
# I recommend, that the formatting is done either in a different instance or prior to running script

# Creating directory and then mounting EBS in that directory
# Note if you reboot the instance, then you will have to remount manually if script is not rerun
sudo mkdir storage
sudo mount dev/xvdf storage