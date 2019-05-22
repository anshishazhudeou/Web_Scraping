#!/bin/bash

if [ "${#}" -ne 0 ]; then
    echo "incorrect number of command line arguments"
    echo "usage: ref_etf_basket_mysql_to_s3.py"
    exit 1
fi

echo "---Running ref_etf_basket_mysql_to_s3.py script"

if python3.4 ref_polist_web_to_s3.py; then
	echo '---ref_polist_web_to_s3.py successfully completed---'
else
	echo '---Running ref_polist_web_to_s3.py failed---'
fi

