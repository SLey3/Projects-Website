read -n1 -p "Do you wish to proceed? (Please make sure to remove the current certificate before proceeding) [Y,N]" responce

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
    if [[ -f $PWD/cert/server.cert ]] && [[ -f $PWD/cert/server.key ]] ;
    then
        rm $PWD/cert/server.cert -v ;
        rm $PWD/cert/server.key -v ;
        echo "expired certifficates succefully removed" ;
    else
        echo "No expired files found" ;
    fi
else
    if [[ -f server.cert ]] && [[ -f server.key ]] ;
    then
        rm server.cert -v ;
        rm server.key -v ;
        echo "expired certifficates succefully removed" ;
    else
        echo "No expired files found" ;
    fi
fi


openssl req  -nodes -new -x509  -keyout server.key -out server.cert

echo "Certifficate created. Moving certifficates to correct folder"
if [ "${PWD##*/}"  == "Projects_Website" ] ;
then
    cp server.cert cert ;
    rm server.cert --verbose ;
    cp server.key cert ; 
    rm server.key --verbose ;
else 
    cd .. ;
    cp server.crt cert ;
    rm server.crt --verbose ;
    cp server.key cert ; 
    rm server.key --verbose ;
fi

echo "Certifficates moved"

echo "End of Certifficate Creation"

exit 0