# Raspberry PI SD clone instructions
---

## Cloning

Power off the RaspberryPi and extract the SD card from it.
Insert the SD card in a Linux machine and verify the SD card is not mounted:

```sh
sudo mount | grep sdx
```

If something is mounted, then unmount all the partitions (usually two, one for `/boot` and one for `/`):

```sh
sudo umount /dev/sdx1 /dev/sdx2
```

Now clone the SD card using `dd`:

```sh
sudo dd if=/dev/sdx of=/path/to/save/backup.img
```

such a command will last many seconds (in my case about 1120 s for a 16GB SD card)
After that it is possible to shrink the image (in fact as it is it occupies the whole SD card size):

```sh
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x ./pishrink.sh
./pishrink.sh -v /path/to/save/backup.img
```

In such a way the image is shrinked to the actual occupied size of the SD card and at the first boot it will be again expanded. 


## Restore

In order to restore the previously saved img file, it is possible to use the following command:

```sh
sudo dd if=/path/to/save/backup.img of=/dev/sdx
```

both in case the image has been shrinked and in case it is left expanded. 	
