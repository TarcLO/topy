# Various ToPy examples

Go to the 'scripts' directory and find the 'optimise.py' file, it
reads and loads a TPD (ToPy Problem Definition) file.

You can (obviously) change `optimise.py` to suit your needs. Be aware that it uses MPI.

You can check the folder 'new' for examples using the new algorithm. All of the examples
used in the original ToPy are present in the 'legacy' folder and left unchanged. They
should be working just the same.

## Note to Windows users
> You have to copy the 'optimise.py' type files to each example directory. Under
> Linux (and I suspect OS X too) you can make use of symbolic links - I don't know
> if there's a similar mechanism in Windows to accomplish this.

# Running the 'optimise.py' script
In a terminal/console, type:

	$ python optimise.py <filename>.tpd

for single threaded FEA, or:

    $ mpirun -n 2 python3 -m mpi4py optimise.py <filename>.tpd

for multiprocessing (2 processes, in this case), in the relevant example directory.

# Animations
All 3D animations were created with the help of *ParaView 3* and *ImageMagick*. In *ParaView*, save the animation as a sequence of PNGs, or directly as an AVI (produces larger files). *gifsicle* is another option to produce GIFs from stills.

I found the least painful way to get animations to be via *convert* (or *gifsicle*).

## GIFs
Create with: *ImageMagick's convert*, a command-line tool.

View with: Just about any web browser should display GIFs without any problem.

A typical command:

	convert -delay 35 *.png anim.gif
	
This will convert all the PNGs in the folder into a single GIF.
