##
# @file process.py
# @package openmoc.process
# @brief
# @author William Boyd (wboyd@mit.edu)
# @date April 27, 2013

import matplotlib.pyplot as plt
import openmoc
from log import *
import numpy
import os


## A static variable for the output directory in which to save plots
subdirectory = "/plots/"


#
# @brief Returns an array of the center values for a tally's bins.
# @details A wrapper function to make it easier to access a tally's bin center
#          data array through SWIG. This would be invoked a PINSPEC Python
#          input file as follows:
#
# @code
#          bin_center_array = pinspec.process.getTallyCenters(tally)
# @endcode
#
# @param tally the tally of interest
# @return a numpy array with the tally bin centers
def strongScalingStudy(geometry, num_azim=48, track_spacing=0.1, 
                       num_threads=None, max_iters=10, 
                       compiler='gnu', precision='double', 
                       title='', filename=''):

    global subdirectory

    directory = openmoc.getOutputDirectory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    if (num_threads is None):
        num_threads = numpy.linspace(1,12,12)
    else:
        num_threads = numpy.array(num_threads)

    if compiler == 'all':
        compiler = ['gnu', 'intel']
    elif compiler == 'intel':
        compiler = ['intel']
    else:
        compiler = ['gnu']

    if precision == 'all':
        precision = ['single', 'double']
    elif precision == 'double':
        precision = ['double']
    else:
        precision = ['single']

    legend = []
    times = numpy.zeros((len(precision), len(compiler), num_threads.size))

    for i in range(len(precision)):
        for j in range(len(compiler)):
            
            fp = precision[i]
            cc = compiler[j]

            if fp == 'single' and cc == 'gnu':
                import gnu.single as openmoc
            elif fp == 'single' and cc == 'intel':
                import intel.single as openmoc
            elif fp == 'double' and cc == 'gnu':
                import gnu.double as openmoc
            elif fp == 'double' and cc == 'intel':
                import intel.double as openmoc

            track_generator = openmoc.TrackGenerator(geometry, num_azim, 
                                                     track_spacing)
            track_generator.generateTracks()

            py_printf('NORMAL', '# FSRs = %d, # tracks = %d, # segments = %d',
                      geometry.getNumFSRs(), track_generator.getNumTracks(),
                      track_generator.getNumSegments())

            solver = openmoc.Solver(geometry, track_generator)

            timer = openmoc.Timer()
            
            legend.append('' + cc + '-' + fp)

            for k in range(num_threads.size):
                
                solver.setNumThreads(int(num_threads[k]))

                timer.resetTimer()
                timer.startTimer()
                solver.convergeSource(max_iters)
                timer.stopTimer()
                timer.recordSplit('' + str(num_threads[k]) + ' threads' + ' ' 
                                  + cc + '-' + fp)
                times[i][j][k] = timer.getTime()
                timer.printSplits()

            timer.printSplits()

    times /= max_iters

    # Plot Runtime
    if title == '':
        title1 = 'OpenMOC OpenMP Strong Scaling Time per Iteration'
    else:
        title1 = title + ' Runtime'

    if filename == '':
        filename1 = directory + 'strong-scaling-runtime.png'
    else:
        filename1 = directory + filename + '-runtime.png'

    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, times[i][j], linewidth=3)

    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, times[i][j], linewidth=3 )
    plt.xlabel('# threads')
    plt.ylabel('Runtime [sec]')
    plt.title(title1)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.grid()
    plt.savefig(filename1, bbox_inches='tight')

    # Plot Speedup
    if title == '':
        title2 = 'OpenMOC OpenMP Strong Scaling Speedup'
    else:
        title2 = title + ' Speedup'

    if filename == '':
        filename2 = directory + 'strong-scaling-speedup.png'
    else:
        filename2 = directory + filename + '-speedup.png'

    speedup = times[:,:,0][:,:,numpy.newaxis] / times
    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, speedup[i][j], linewidth=3)
    plt.xlabel('# threads')
    plt.ylabel('Speedup')
    plt.title(title2)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.grid()
    plt.savefig(filename2, bbox_inches='tight')

    # Plot parallel efficiency
    if title == '':
        title3 = 'OpenMOC OpenMP Strong Scaling Parallel Efficiency'
    else:
        title3 = title + ' Parallel Efficiency'

    if filename == '':
        filename3 = directory + 'strong-scaling-efficiency.png'
    else:
        filename3 = directory + filename + '-efficiency.png'
    
    efficiency = (times[:,:,0][:,:,numpy.newaxis] * num_threads[0]) / \
                 (num_threads * times)
    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, efficiency[i][j], linewidth=3)
    plt.xlabel('# threads')
    plt.ylabel('Efficiency')
    plt.title(title3)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.grid()
    plt.savefig(filename3, bbox_inches='tight')


#
# @brief Returns an array of the center values for a tally's bins.
# @details A wrapper function to make it easier to access a tally's bin center
#          data array through SWIG. This would be invoked a PINSPEC Python
#          input file as follows:
#
# @code
#          bin_center_array = pinspec.process.getTallyCenters(tally)
# @endcode
#
# @param tally the tally of interest
# @return a numpy array with the tally bin centers
def weakScalingStudy(geometry, num_azim=4, track_spacing=0.1, 
                     num_threads=None, max_iters=10, 
                     compiler='gnu', precision='double', 
                     title='', filename=''):

    global subdirectory

    directory = openmoc.getOutputDirectory() + subdirectory

    # Make directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    if (num_threads is None):
        num_threads = numpy.linspace(1,12,12)
    else:
        num_threads = numpy.array(num_threads)

    if compiler == 'all':
        compiler = ['gnu', 'intel']
    elif compiler == 'intel':
        compiler = ['intel']
    else:
        compiler = ['gnu']

    if precision == 'all':
        precision = ['single', 'double']
    elif precision == 'double':
        precision = ['double']
    else:
        precision = ['single']

    legend = []
    times = numpy.zeros((len(precision), len(compiler), num_threads.size))
    num_azim *= num_threads

    for i in range(len(precision)):
        for j in range(len(compiler)):
            
            fp = precision[i]
            cc = compiler[j]

            if fp == 'single' and cc == 'gnu':
                import gnu.single as openmoc
            elif fp == 'single' and cc == 'intel':
                import intel.single as openmoc
            elif fp == 'double' and cc == 'gnu':
                import gnu.double as openmoc
            elif fp == 'double' and cc == 'intel':
                import intel.double as openmoc

            timer = openmoc.Timer()
            
            legend.append('' + cc + '-' + fp)

            for k in range(len(num_azim)):

                track_generator = openmoc.TrackGenerator(geometry, 
                                                         int(num_azim[k]),
                                                         track_spacing)
                track_generator.generateTracks()

                py_printf('NORMAL', '# FSRs = %d, # tracks = %d, # ' + \
                          'segments = %d', geometry.getNumFSRs(), 
                          track_generator.getNumTracks(),
                          track_generator.getNumSegments())

                solver = openmoc.Solver(geometry, track_generator)
                solver.setNumThreads(int(num_threads[k]))
        
                timer.resetTimer()
                timer.startTimer()
                solver.convergeSource(max_iters)
                timer.stopTimer()
                timer.recordSplit('' + str(num_threads[k]) + ' threads' + ' ' 
                                  + cc + '-' + fp)
                times[i][j][k] = timer.getTime()
                timer.printSplits()

            timer.printSplits()

    times /= max_iters

    # Plot Runtime
    if title == '':
        title1 = 'OpenMOC OpenMP Weak Scaling Time per Iteration'
    else:
        title1 = title + ' Runtime'

    if filename == '':
        filename1 = directory + 'weak-scaling-runtime.png'
    else:
        filename1 = directory + filename + '-runtime.png'

    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, times[i][j], linewidth=3)
    plt.xlabel('# threads')
    plt.ylabel('Runtime [sec]')
    plt.title(title1)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.grid()
    plt.savefig(filename1, bbox_inches='tight')

    # Plot Speedup
    if title == '':
        title2 = 'OpenMOC OpenMP Weak Scaling Speedup'
    else:
        title2 = title + ' Speedup'

    if filename == '':
        filename2 = directory + 'weak-scaling-speedup.png'
    else:
        filename2 = directory + filename + '-speedup.png'

    speedup = num_threads * (times[:,:,0][:,:,numpy.newaxis] / times)
    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, speedup[i][j], linewidth=3)
    plt.xlabel('# threads')
    plt.ylabel('Speedup')
    plt.title(title2)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.savefig(filename2, bbox_inches='tight')

    # Plot parallel efficiency
    if title == '':
        title3 = 'OpenMOC OpenMP Weak Scaling Parallel Efficiency'
    else:
        title3 = title + ' Parallel Efficiency'

    if filename == '':
        filename3 = directory + 'weak-scaling-efficiency.png'
    else:
        filename3 = directory + filename + '-efficiency.png'
    
    efficiency = times[:,:,0][:,:,numpy.newaxis] / times
    fig = plt.figure()
    for i in range(len(precision)):
        for j in range(len(compiler)):
            plt.plot(num_threads, efficiency[i][j], linewidth=3)
    plt.xlabel('# threads')
    plt.ylabel('Efficiency')
    plt.title(title3)
    if (len(legend) > 1):
        plt.legend(legend)
    plt.grid()
    plt.savefig(filename3, bbox_inches='tight')


##
# @brief
# @param
# @param
#
def computeFSRPinPowers(solver, geometry, use_hdf5=False):

    # Error checking of input parameters

    directory = openmoc.getOutputDirectory() + '/pin-powers/'

    # Determine which universes and lattices contain fissionable materials
    geometry.computeFissionability()

    # Compute the volume-weighted FSR fission rates for each FSR
    fission_rates = solver.computeFSRFissionRates(geometry.getNumFSRs())

    # Initialize a new HDF5 file to store the pin power data
    if use_hdf5:

        # Import h5py 
        import h5py

        # Make directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        f = h5py.File(directory + 'fission-rates.hdf5', 'w')
        f.close()


    # Get the base universe in the geometry and compute pin powers for each
    # level of nested universes and lattices
    universe = geometry.getUniverse(0)
    computeUniverseFissionRate(geometry, universe, 0, fission_rates, use_hdf5,
                               directory=directory)


##
# @brief
# @param
# @param
# @param
# @param
# @param
# @return
#
def computeUniverseFissionRate(geometry, universe, FSR_id, 
                               FSR_fission_rates, use_hdf5=False, 
                               attributes = [], directory=''):

    fission_rate = 0.0

    # If the universe is not fissionable, the fission rate within it
    # is zero
    if not universe.isFissionable():
        return fission_rate

    # If the universe is a fissionable SIMPLE type universe
    elif universe.getType() is openmoc.SIMPLE:

        # Create a directory/file for this universe's total fission rate
        attributes.append('universe' + str(universe.getId()))

        num_cells = universe.getNumCells()
        cell_ids = universe.getCellIds(int(num_cells))

        # For each of the cells inside the universe, check if it is 
        # MATERIAL or FILL type
        for cell_id in cell_ids:
        
            cell = universe.getCell(int(cell_id))
            
            # If the current cell is a MATERIAL type cell, 
            if cell.getType() is openmoc.MATERIAL:
                cell = openmoc.castCellToCellBasic(cell)
                fsr_id = universe.getFSR(cell.getId()) + FSR_id
                fission_rate += FSR_fission_rates[fsr_id]
            
            # The current cell is a FILL type cell
            else:
                cell = openmoc.castCellToCellFill(cell)
                universe_fill = cell.getUniverseFill()
                fsr_id = universe.getFSR(cell.getId()) + FSR_id
                fission_rate += \
                    computeUniverseFissionRate(geometry, universe_fill, 
                                               fsr_id, FSR_fission_rates, 
                                               use_hdf5, attributes, directory)

        # Remove the subdirectory structure attribute for this universe
        attributes.pop()


    # This is a fissionable LATTICE type universe
    else:

        # Add a new attribute for this lattice in the pin power hierarchy
        attributes.append('lattice' + str(universe.getId()))

        # Retrieve a pointer to this lattice and its dimensions
        lattice = openmoc.castUniverseToLattice(universe)
        num_x = lattice.getNumX()
        num_y = lattice.getNumY()

        # Create a numpy array to store all of this lattice's pin powers
        lattice_cell_powers = numpy.zeros((num_x, num_y))

        attributes.append('x')
        attributes.append('y')

        # Loop over all lattice cells in this lattice
        for i in range(num_y-1, -1, -1):
            for j in range(num_x):

                # Get a pointer to the current lattice cell
                cell_universe = lattice.getUniverse(j,i)
                
                # Get the FSR Id prefix for this lattice cell
                fsr_id = lattice.getFSR(j,i) + FSR_id

                attributes[-1] = 'y' + str(i)
                attributes[-2] = 'x' + str(j)

                # Compute the fission rate within this lattice cell
                lattice_cell_powers[j,i] = \
                    computeUniverseFissionRate(geometry, cell_universe, fsr_id, 
                                               FSR_fission_rates, use_hdf5,
                                               attributes, directory)

                # Increment total lattice power
                fission_rate += lattice_cell_powers[j,i]

        # Remove subdirectory attributes for x, y lattice cell indices
        attributes.pop()
        attributes.pop()
        attributes.pop()

        # Flip the x-dimension of the array so that it is indexed 
        # starting from the top left corner as
        lattice_cell_powers = numpy.fliplr(lattice_cell_powers)


        #######################################################################
        #######################  STORE PIN CELL DATA  #########################
        #######################################################################

        # If using HDF5, store data categorized by attributes in an HDF5 file
        if use_hdf5:

            # Import h5py 
            import h5py
            
            # Create a h5py file handle for the file
            f = h5py.File(directory + 'fission-rates.hdf5', 'a')

            # Create the group for this lattice, universe combination
            curr_group = f.require_group(str.join('/', attributes))

            # Create a new dataset for this lattice's pin powers
            curr_group.create_dataset('fission-rates', data=lattice_cell_powers)

            f.close()


        # If not using HDF5, store data categorized by subdirectory in txt files
        else:

            subdirectory = directory + str.join('/', attributes) + '/'

            # Make directory if it does not exist
            if not use_hdf5 and not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

            numpy.savetxt(subdirectory + 'fission-rates.txt', 
                          lattice_cell_powers, delimiter=',')

    # Return the total fission rate for this lattice
    return fission_rate