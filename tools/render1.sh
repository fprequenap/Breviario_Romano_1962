#!/bin/bash
# $1 = MM-DD-YYYY  ; renders 7 diurnal hours
export PERL5LIB=/root/cgipm/lib:/root/URI/lib
cd /root/do/standalone/tools/epubgen2
d=$1
for h in Laudes Prima Tertia Sexta Nona Vespera Completorium; do
  out=/root/render/$d-$h.html
  [ -s "$out" ] && continue
  perl EofficiumXhtml.pl "date1=$d&command=pray$h&version=Rubrics 1960 - 1960&testmode=regular&lang1=Latin&lang2=Espanol&votive=&linkmissa=&nofancychars=0" > $out 2>/dev/null
done
