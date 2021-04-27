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
fi

echo "checking if sess directory exists.."

cd $PARENT_DIR/ProjectsWebsite/static

if [ -d "sess" ] ;
then
    echo "sess directory exists" ;
else
    echo "Creating sess directory..." ;
    mkdir sess --verbose ;
    echo "Created directory: sess" ;
fi

echo "checking if unverified folder exists.."

if [ -d "unverified" ] ;
then
    cd unverified ;

    echo "unverified directory exists" ;

    echo "Checking if unverfied-logs file exists" ;

    if [ -f "unverfied-log.txt" ] ;
    then
        echo "log file exists" ;
    else 
        echo "creating log file..." ;
        touch unverfied-log.txt ;
        echo "log file created" ;
    fi
else
    echo "Creating unverified directory..." ;
    mkdir unverified --verbose ;
    echo "unverified directory created" ;

    echo "Creating log file..." ;
    cd unverified ;
    touch unverfied-log.txt ;
    echo "log file created" ;
fi

cd $PARENT_DIR

echo "Check Complete. End of Checkdirs."