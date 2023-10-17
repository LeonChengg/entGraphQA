#!/bin/bash
#fName=../data/news_raw.json
#oName1=predArgs_gen.txt
#oName2=predArgs_NE.txt
#echo "0" > offset.txt
#i=0
#echo $i
#while [ -f offset.txt ]; do
#if [ $i -eq 0 ]
#then
#        java -cp lib/*:bin  entailment.LinesHandler $fName $i $oName1 $oName2 1>tmpo.txt 2>lineNumbers_b.txt
#else
#        java -cp lib/*:bin  entailment.LinesHandler $fName $i $oName1 $oName2 1>>tmpo.txt 2>>lineNumbers_b.txt
#fi
#i=$((i + 1))
#echo $i
#done

#!/bin/bash
fName=news_raw.json
oName1=predArgs_gen.txt
oName2=predArgs_NE.txt
echo "0" > offset.txt
i=0
echo $i
while [ -f offset.txt ]; do
if [ $i -eq 0 ]
then
        java -cp lib/*:bin  entailment.LinesHandler $fName $i $oName1 $oName2 1>tmpo.txt 2>lineNumbers_b.txt
else
        java -cp lib/*:bin  entailment.LinesHandler $fName $i $oName1 $oName2 1>>tmpo.txt 2>>lineNumbers_b.txt
fi
i=$((i + 1))
echo $i
done