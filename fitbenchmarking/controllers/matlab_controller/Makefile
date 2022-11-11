all: mex lib #main exe

mex:
	# Compile the MEX-file which allows calling back into the C code
	mex -R2018a evalfunction.c

lib:
	# Compile the library using the MATLAB Compiler
	mcc -W 'lib:libmatlabcontroller' -T link:lib min_wrapper.m

# main:
# 	# Compiler the "driver" library called by python
# 	mbuild -output libcontrollerpyiface pyiface.c -L. -libmatlabcontroller

# exe:
# 	# Compiler the "driver" library as an executable
# 	mbuild optimmatlab.c -L. -loptimize

clean:
	rm -f *~ *.log *.mexa64 *.pyc *.o *.so liboptimize.* optimmatlab
