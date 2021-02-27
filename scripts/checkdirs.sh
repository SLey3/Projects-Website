echo "Checking if necessary directory's exist..."

if [ "${PWD##*/}"  == "Projects_Website" ] ;
then
  PARENT_DIR=$PWD ;
else
    cd .. ;
    PARENT_DIR=$PWD ;
fi

echo "checking if cert directory exists..."

if [ -d "cert" ] ;
then
    echo "cert directory exists" ;
else
    echo "Creating cert directory.." ;
    mkdir cert --verbose ;
    echo "Created directory: cert" ;

echo "checking if sess directory exists"
fi

cd ProjectsWebsite/static

if [ -d "sess" ] ;
then
    echo "sess directory exists" ;
else
    echo "Creating sess directory" ;
    mkdir sess --verbose ;
    echo "Created directory: sess" ;
fi

cd $PARENT_DIR

echo "Check Complete. End of Checkdirs."