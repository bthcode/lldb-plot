###############################################
# script to build examples - 
#   These examples are thin samples and 
#   don't really warrant a build system
###############################################

echo "Building a few examples - "
echo "  - If any build fails, that's probably ok - these are just examples"

echo "Building example with arrays, pointer arrays and stl vectors"
g++ examples/example.cpp -g -o examples/example
