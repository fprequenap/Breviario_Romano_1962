#!/bin/bash
# Regenera los datos del Breviario para un rango de fechas.
# Requisitos: Linux/WSL con git, perl (con CGI.pm y URI) y python3.
# Uso: ./generar.sh 2029-01-01 2029-12-31
set -e
DESDE=${1:?fecha inicial AAAA-MM-DD}; HASTA=${2:?fecha final AAAA-MM-DD}
[ -d /root/do ] || git clone --depth 1 https://github.com/DivinumOfficium/divinum-officium.git /root/do
python3 -c "
import datetime,sys
d=datetime.date.fromisoformat('$DESDE');h=datetime.date.fromisoformat('$HASTA')
while d<=h: print(d.strftime('%m-%d-%Y')); d+=datetime.timedelta(1)" | xargs -P 4 -n 1 ./render1.sh
python3 parse.py && python3 package.py
# Después, con los datos copiados en la app: aplicar_traduccion.py, titulos.py y publicar.py (en ese orden).
