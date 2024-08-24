#!/bin/bash
echo "This will download and install qrcode for python into your system, continue? (type y or n)"
read text
if [ $text == "y" ]
then
echo
pkgman install qrcode_python310
ret3=$?
echo
else
	echo "Proceeding..."
	ret3=1
fi
echo "Do you wish to git clone & compile Haiku-PyAPI to your system? (type y or n)"
read text
if [ $text == "y" ]
then
git clone --recourse-submodules https://github.com/coolcoder613eb/Haiku-PyAPI.git
cd Haiku-PyAPI
jam -j$(nproc)
ret2=$?
if [ $ret2 -lt 1 ]
then
	if ! [[ -e /boot/system/non-packaged/lib/python3.10/site-packages/Be ]]; then
		mkdir /boot/system/non-packaged/lib/python3.10/site-packages/Be
	fi
	echo "copying compiled data to system folder..."
	#cd bin/x86_64/python3.10 && cp -v * /boot/system/non-packaged/lib/python3.10/site-packages/Be
	cd build/python3.10_release && cp -v * /boot/system/non-packaged/lib/python3.10/site-packages/Be
	ret7=$?
	cd ../../..
fi
cd ..
else
echo "Proceeding..."
ret2=1
ret7=1
fi
echo
if [ -e HaiQR.py ]
then
	if ! [[ -e /boot/home/config/non-packaged/data/HaiQR2 ]]; then
		mkdir /boot/home/config/non-packaged/data/HaiQR2
	fi
	cp HaiQR.py /boot/home/config/non-packaged/data/HaiQR2
	ret4=$?
	if [ -e /boot/home/config/non-packaged/bin/HaiQR ]; then
		rm -f /boot/home/config/non-packaged/bin/HaiQR
	fi
	ln -s /boot/home/config/non-packaged/data/HaiQR2/HaiQR.py /boot/home/config/non-packaged/bin/HaiQR
	if ! [[ -e /boot/home/config/settings/deskbar/menu/Applications/ ]]; then
		mkdir /boot/home/config/settings/deskbar/menu/Applications/
	fi
	if [ -e /boot/home/config/settings/deskbar/menu/Applications/HaiQR ]; then
		rm -f /boot/home/config/settings/deskbar/menu/Applications/HaiQR
	fi
	ln -s /boot/home/config/non-packaged/bin/HaiQR /boot/home/config/settings/deskbar/menu/Applications/HaiQR
	ret5=$?
else
	echo Main program missing
	ret4=1
	ret5=1
fi
echo
DIRECTORY=`pwd`/data
if [ -d $DIRECTORY  ]
then
	cp -R data /boot/home/config/non-packaged/data/HaiQR2
	ret6=$?
else
	echo Missing Data directory and images
	ret6=1
fi
echo


if [ $ret2 -lt 1 ]
then
	echo Compilation of Haiku-PyAPI OK
else
	echo Compilation of Haiku-PyAPI FAILED
fi
if [ $ret7 -lt 1 ]
then
	echo Installation of Haiku-PyAPI OK
else
	echo Installation of Haiku-PyAPI FAILED
fi
if [ $ret3 -lt 1 ]
then
	echo Installation of qrcode OK
else
	echo Installation of qrcode FAILED
fi
if [ $ret4 -lt 1 ] 
then
        echo Installation of HaiQR OK
else
        echo Installation of HaiQR FAILED
fi
if [ $ret5 -lt 1 ]
then
        echo Installation of menu entry OK
else
        echo Installation of menu entry FAILED
fi

if [ $ret6 -lt 1 ]
then
        echo Installation of Data files and images OK
else
        echo Installation of Data files and images FAILED
fi
