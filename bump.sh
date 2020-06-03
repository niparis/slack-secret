#!/bin/sh

run()
{

    semver=$1

    if  [ $semver == 'patch' ];
    then
        echo "patch"
    elif  [ $semver == 'minor' ];
    then
        echo "minor"
    elif  [ $semver == 'major' ];
    then
        echo "major"
    else
        echo "$1 is not a valid semver argument. Use path, minor or major"
        exit
    fi

    git checkout master
	git pull
    poetry version $semver
    git add pyproject.toml
	git commit -m "bumped version using $semver"
	git push --quiet
	git tag $(slacksecrets version)
	git push --tags --quiet
	echo "Version bumped."

}

run $1

# git add pyproject.toml
# git commit -m "bumped version using minor"
# git push --quiet
# git tag $(slacksecrets version)
# git push --tags --quiet
# echo "Version bumped."
