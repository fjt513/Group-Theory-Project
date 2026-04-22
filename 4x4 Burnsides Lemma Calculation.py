from collections import defaultdict
from itertools import permutations


#check if a grid is valid for creating all the 288 solutions
def check_valid_grid(grid):
    # Check if each column is invalid, if valid then check each box
    for col in range(4):
        column = []
        for row in range(4):
            column.append(grid[row][col])
        if len(set(column)) != 4: #if length less than 4 means theres a duplicate digit in a line, so invalid grid
            return False

    # Check if each 2x2 box is invalid, if valid then return True
    for numofbox in range(4): #goes through each 2x2 box
        (x,y) = (numofbox % 2, numofbox // 2) # gets the coordinates of each box as if whole sudoku is 2x2 grid of boxes
        box = grid[2*x][2*y:2*y+2] + grid[2*x+1][2*y:2*y+2] #puts both columns of the box together to make whole box as a single list
        if len(set(box)) != 4: # same as before,set removes duplicates, so if length less than 4 means there is duplicate and therfore invalid grid
            return False
    return True

#function to apply a transformation to the given grid
def apply_grid_transformation(grid, bandperm, rowperm, stackperm, columnperm, digitperm, transpose):
    if transpose:
        grid = [[grid[column][row] for column in range(4)] for row in range(4)]  # Switches the rows and columns to transpose the grid
    
    order_of_rows = [band*2 + row for band in bandperm for row in rowperm[band]] #creates the order of how the rows should be sorted, eg if we get [3,1,4,2], the 3rd row becomes the first, 1st becomes 2nd....
    grid = [grid[row] for row in order_of_rows] # puts the rows in order
    
    order_of_columns = [stack*2 + column for stack in stackperm for column in columnperm[stack]] # Does the same for the columns
    grid = [[row[column] for column in order_of_columns] for row in grid] #switch the order of every digit in each row so that the whole column is permuted uniformly
    
    grid = [[digitperm[cell-1] for cell in row] for row in grid] # permutes each digit, not by normal layout (1,3,2,4) that send 1 to 3 to 2 to 4 to 1, but here (1,3,2,4) 1 to 1, 2 becomes 3, 3 becomes 2 and 4 to 4, so is permuted by position not its digit.

    return tuple(tuple(row) for row in grid)

#breaks up 16 cell grid permutation into individual cycles
def permutation_cycles_from_full_cell_permutation(permutation):
    visited = [False] * len(permutation) # to check if we've visited the grid yet, if we have then cycle is finished
    full_cycles = []
    for i in range(len(permutation)): # goes through each cell, creating any cycles it has or skipping onto next cell
        if not visited[i]: # makes sure we havent already created a cycle with this cell
            single_cycle = []
            currentcell = i
            while not visited[currentcell]: # builds the indivual cycle until it loops
                visited[currentcell] = True
                currentcell = permutation[currentcell]
                single_cycle.append(currentcell)
            full_cycles.append(tuple(single_cycle))
    return tuple(sorted(full_cycles, key=len)) # gives the permutation sorted by length


#Function to turn our tranformation being represented as what order row, columns should go in, into a full permutation of the 16 cells

def transformation_to_permutation_of_cells(transformation):
    bandperm, rowperm, stackperm, columnperm, _digitperm, transpose = transformation
    order_of_rows = [band*2 + row for band in bandperm for row in rowperm[band]] # gives order of how to arrange rows eg (2, 3, 1, 4), 2nd row fist, 3rd second, 1st third and 4th stays last
    order_of_columns = [stack*2 + column for stack in stackperm for column in columnperm[stack]]

    cells = [0] * 16 # 4x4 grid as single list of its 16 cells
    for new_row in range(4):
        for new_column in range(4):
            if transpose: # have to switch rows and columns
                old_row, old_column = order_of_columns[new_column], order_of_rows[new_row]
            else:
                old_row, old_column = order_of_rows[new_row], order_of_columns[new_column]
            cells[new_row * 4 + new_column] = old_row * 4 + old_column
    return tuple(cells)


#First generate all 4x4 grids using inefficient Brute force
grids = []
digit_permutations = list(permutations([1,2,3,4]))  #lists all permutations of the numbers 1-4
single_permutations = list(permutations([0,1]))
for row1 in digit_permutations:  #goes through each possible permutation of the 4 numbers in each row, inneficient but brute force to check absolute validity
    for row2 in digit_permutations:
        for row3 in digit_permutations:
            for row4 in digit_permutations:
                grid = (row1, row2, row3, row4) # 
                if check_valid_grid(grid): 
                    grids.append(grid) # creates a list of all valid grids
print("\nNumber of valid 4x4 Sudoku grids: " + str(len(grids)))

indexofallgrids = {grid: i for i, grid in enumerate(grids)}  # a dictionary to list all the 288 grids and label them 


#Next build the set of all 3072 possible transformations in the symmetry group

symmetry_group = []
alltransformationstoeachgrid = []
for bandperm in single_permutations:      # all of these single permutations say what order the band,stack,rows or columns should be in eg [1,0] means the 2nd band comes first and 1st comes 2nd. 0 or 1 because of list indexing
        for row0perm in single_permutations:
            for row1perm in single_permutations:
                rowperm = [row0perm,row1perm] # puts together the permutations of the rows in both bands 
                for stackperm in single_permutations:
                    for column0perm in single_permutations:
                        for column1perm in single_permutations:
                            columnperm = [column0perm,column1perm] # same as with the rows and bands for columns and stacks
                            for digitperm in digit_permutations:
                                for transpose in [False, True]: # says if it needs transposing
                                    transformation = (bandperm,rowperm,stackperm,columnperm,digitperm,transpose)
                                    symmetry_group.append(transformation)
                                    transformationtoeachgrid = [indexofallgrids[apply_grid_transformation(grid, bandperm, rowperm, stackperm, columnperm, digitperm, transpose)] for grid in grids] # applies each transformation to all grids and results in the permutating of the grids by index
                                    alltransformationstoeachgrid.append(transformationtoeachgrid) # list of each transformations being applied to all grids
print("Number of transformations in the symmetry group: " + str(len(symmetry_group)))



#Next we find the number of grids fixed when the tranformations are applyed to the grids

total_fixed_grids = 0
for transformation in symmetry_group: # goes through each possible transformation
    bandperm, rowperm, stackperm, columnperm, digitperm, transpose = transformation
    for grid in grids: # goes through each grid and applies each transformation to all of them
        if apply_grid_transformation(grid, bandperm, rowperm, stackperm, columnperm, digitperm, transpose) == grid:
            total_fixed_grids += 1
print("Total number of fixed grids from all transformations, claculated without using conjugacy classes: " + str(total_fixed_grids))

print("\nNow we want to try claculating it using the theory of the conjugacy classes.\n")


#creating the conjugacy classes sorting the transformations of the symmetry group by there cycle type
conjugacy_classes = defaultdict(list) # has to be a list for all the transformations in the same conjugacy class
for i, permutationofgrids in enumerate(alltransformationstoeachgrid):
    conjugacy_classes[tuple(len(cycle) for cycle in permutation_cycles_from_full_cell_permutation(permutationofgrids))].append(i)

print("The number of conjugacy classes: " + str(len(conjugacy_classes)))

print(f"\n{'#':<4} {'Class size':>10} {'Grids fixed':>13} {'Representative'}") # graphing
print("-------------------------------------------------------------------------------------------------")


total_grids_fixed_by_class = 0
for conjugacy_class_num, (cycle_type, transformations_in_conjguacy_class) in enumerate(sorted(conjugacy_classes.items(), key=lambda x: -x[0].count(1)), start=1): # take information from each conjugacy class to display result
    conjugacy_class_size = len(transformations_in_conjguacy_class)

    number_of_grids_fixed = cycle_type.count(1)

    list_of_cell_cycles = permutation_cycles_from_full_cell_permutation(transformation_to_permutation_of_cells(symmetry_group[transformations_in_conjguacy_class[0]]))
    
    cycle_notation_of_cell_permutation = ""
    if len(list_of_cell_cycles) == 16: # check for identity permutation
        cycle_notation_of_cell_permutation = "()"
    else:
        for cycle in list_of_cell_cycles: #remove all single cycles
            if len(cycle) > 1:
                cycle_notation_of_cell_permutation += str(sorted([digit + 1 for digit in cycle])) #shows the permutation of the cells 1-16 and not the index of the 16 cells 0-15
    cycle_notation_of_cell_permutation = cycle_notation_of_cell_permutation.replace(",", "")
    cycle_notation_of_cell_permutation = cycle_notation_of_cell_permutation.replace("[", "(")
    cycle_notation_of_cell_permutation = cycle_notation_of_cell_permutation.replace("]", ")")

    total_grids_fixed_by_class += conjugacy_class_size * number_of_grids_fixed

    print(f"{conjugacy_class_num:<4} {conjugacy_class_size:<12} {number_of_grids_fixed:<10}  {cycle_notation_of_cell_permutation}")
           

print("-------------------------------------------------------------------------------------------------\n")
print("Burnside's Sum total - Total fixed grids by all transformations: " + str(total_grids_fixed_by_class))
print("Burnside's Lemma - Number of distinct 4x4 Sudoku grids: " + str(total_grids_fixed_by_class) + "/" + str(len(symmetry_group)) + " = " + str(total_grids_fixed_by_class/len(symmetry_group)) + '\n')