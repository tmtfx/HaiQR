#!/bin/bash
echo "This will download and install pip_python to your system, continue? (type y or n)"
read text
if [ $text == "y" ]
then
echo
pkgman install pip_python
ret3=$?
echo
else
	echo "Proceeding..."
	ret3=1
fi
echo "Now we will install Bethon 0.5.4.1 if present..."
if [ -e Bethon-0.5.4.1.tar.gz ]
then
	tar -xf Bethon-0.5.4.1.tar.gz
	cd Bethon-0.5.4.1
	make && make install
	ret2=$?
	cd ..
else
	echo "Bethon 0.5.4.1 not present in this folder... "
	echo "Do you wish to git clone Bethon to your system? (type y or n)"
	read text
	if [ $text == "y" ]
	then
	git clone https://github.com/tmtfx/Bethon-0.5.4.1
	cd Bethon-0.5.4.1
	make && make install
	ret2=$?
	cd ..
	else
	echo "Proceeding..."
	ret2=1
	fi
fi
if [ -e /bin/pip ]
then
	echo "Install qrcode module for python2? (type y or n)"
	read text
	if [ $text == "y" ]
	then
	pip install qrcode
	ret4=$?
	else
	ret4=1
	fi
	echo "Install Pillow module for python2? (type y or n)"
	read text
	if [ $text == "y" ]
	then
	pip install pillow
	ret5=$?
	else
	ret5=1
	fi
	echo "Install backports.tempfile module for python2? (type y or n)"
	read text
	if [ $text == "y" ]
	then
	pip install backports.tempfile
	ret6=$?
	else
	ret6=1
	fi
else
	ret4=1
	ret5=1
	ret6=1
fi
echo
if [ -e HaiQR.py ]
then
	mkdir /boot/home/config/non-packaged/data/HaiQR
	cp HaiQR.py /boot/home/config/non-packaged/data/HaiQR
	ret7=$?
	ln -s /boot/home/config/non-packaged/data/HaiQR/HaiQR.py /boot/home/config/non-packaged/bin/HaiQR
	mkdir /boot/home/config/settings/deskbar/menu/Applications/
	ln -s /boot/home/config/non-packaged/bin/HaiQR /boot/home/config/settings/deskbar/menu/Applications/HaiQR
	ret8=$?
else
	echo "Main program missing"
	ret7=1
	ret8=1
fi
echo
DIRECTORY=`pwd`/data
if [ -d $DIRECTORY  ]
then
	cp -R data /boot/home/config/non-packaged/data/HaiQR
	ret9=$?
else
	echo Missing data directory and images
	ret9=1
fi
echo

if [ $ret2 -lt 1 ]
then
	echo Installation of Bethon OK
else
	echo Installation of Bethon FAILED
fi
if [ $ret3 -lt 1 ]
then
	echo Installation of pip_python OK
else
	echo Installation of pip_python FAILED
fi
if [ $ret4 -lt 1 ] 
then
        echo Installation of qrcode module OK
else
        echo Installation of qrcode module FAILED
fi
if [ $ret5 -lt 1 ]
then
        echo Installation of pillow module OK
else
        echo Installation of pillow module FAILED
fi
if [ $ret6 -lt 1 ]
then
        echo Installation of backports.tempfile OK
else
        echo Installation of backports.tempfile FAILED
fi
if [ $ret7 -lt 1 ]
then
        echo Installation of main program OK
else
        echo Installation of main program FAILED
fi
if [ $ret8 -lt 1 ]
then
        echo Installation of menu entry OK
else
        echo Installation of menu entry FAILED
fi
if [ $ret9 -lt 1 ]
then
        echo Installation of data files OK
else
        echo Installation of data files FAILED
fi
