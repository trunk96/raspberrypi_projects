#!/bin/bash
cd "$(dirname "$0")"

# sudo ./proxy/env/bin/python ./proxy/proxy.py &
# ./home_automation/env/bin/python ./home_automation/turn_all_off.py &
for D in `find . -maxdepth 1 -type d`
do
	#echo $D
	if [ $D != "." ]
	then
		if [ $D != "./.git" ]
		then
			echo $D
			cd $D
			if [ $D = "./proxy" ]
			then
				sudo ./run.sh
			else
				./run.sh
			fi
			cd ..
		fi
	fi
	#cd $D
	#./run.sh
	#cd ..
done	
