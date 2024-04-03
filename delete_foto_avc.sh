#!/bin/bash
day_delete=24;
day_keep=21;
path_foto="/home/avc/Project/cuavc/image";

while [ $day_keep -lt $day_delete ]
do
    gol="0 1 2 3 4 5"; #Golongan
    for i in $gol
    do
        day=$(date "+%d%m%Y" -d "$day_keep days ago");
        del_foto=$path_foto/$i/$day;
        echo "$del_foto";
        rm -rf $del_foto
    done
let day_keep++
done
exit 
