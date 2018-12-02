# -------
# Project
# -------

mkvar:
	mkdir -p var/lib

redis-start: mkvar
	echo 'dir ./var/lib\nappendonly yes' | redis-server -
