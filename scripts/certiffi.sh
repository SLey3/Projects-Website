read -n1 -p "Do you wish to proceed? [Y,N]" responce

if [[ $responce == "Y" || $responce == "y" ]] ; 
then
    echo "   " ;
    echo "Proceeding..." ;
else
    exit 1 ;
fi

echo "Removing expired certifficates..."

if [ "${PWD##*/}"  == "Projects_Website" ] ;
then 
    if [[ -f $PWD/scripts/cert.pem ]] && [[ -f $PWD/scripts/key.pem ]] ;
    then
        rm $PWD/scripts/cert.pem -v ;
        rm $PWD/scripts/key.pem -v ;
        echo "expired certifficates succefully removed" ;
    else
        echo "No expired files found" ;
    fi
else
    if [[ -f cert ]] && [[ -f key ]] ;
    then
        rm cert.pem -v ;
        rm key.pem -v ;
        echo "expired certifficates succefully removed" ;
    else
        echo "No expired files found" ;
    fi
fi


openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

echo "Certifficate created. Moving certifficates to correct folder"
if [ "${PWD##*/}"  == "Projects_Website" ] ;
then
    python scripts/movecertiffi.py ;
else 
    python movecertiffi.py ;
fi

echo "Certifficates moved"

echo "End of Certifficate Creation"

exit 0