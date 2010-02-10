#/bin/sh
COUNT=1
while echo Looper Script Count $COUNT
do
$@
sleep 30s
COUNT=`echo "$COUNT + 1" | bc`
done
