mutable struct b
	b1
	b2
	livecells
	iterations
end
using Images
using FileIO
water = Int8(1)
soil = Int8(2)
plant = Int8(3)
ded = Int8(0)
padding = parse(Int64,ARGS[3])
b1 = zeros(Int8, parse(Int64,ARGS[1]) + padding*2, parse(Int64,ARGS[1]) + padding*2)
b2 = zeros(Int8, parse(Int64,ARGS[1]) + padding*2, parse(Int64,ARGS[1]) + padding*2)
board = b(b1,b2,Set{Vector{Int64}}(),0)
function getcurboard(m::b)
	return (m.iterations % 2 == 0) ? m.b1 : m.b2
end
function getoldboard(m::b)
	return (m.iterations % 2 == 0) ? m.b2 : m.b1
end
sb = getoldboard(board)
for x in 1:parse(Int64,ARGS[1])
	for y in 1:parse(Int64,ARGS[1])
		if (x+y) % 2 == 0
			sb[x+padding,y+padding] = water
		else
			sb[x+padding,y+padding] = soil
		end
		push!(board.livecells,[x+padding,y+padding])
	end
end
function runiteration!(m::b)
	global ded,water,soil,plant
	oldboard = getoldboard(m)
	newboard = getcurboard(m)
	Threads.@threads for c in collect(m.livecells)
		for x in c[1]-1:c[1]+1
			for y in c[2]-1:c[2]+1
				begin
					curcell = oldboard[x,y]
					if curcell == plant
						newboard[x,y] = plant
						continue
					end
					counts = [0,0,0] # 1 for water, 2 for soil, 3 for plant
					for surrx in x-1:x+1
						for surry in y-1:y+1
							if [surrx,surry] == [x,y]
								continue
							end
							v = oldboard[surrx,surry]
							if v != 0
								counts[v] += 1
							end
						end
					end
					numwater = counts[1]
					numsoil = counts[2]
					numplant = counts[3]
					# full ruleset
					# if empty:
					# water can arise if 3 neighbohrs water, or surrounding water+surrounding plant = 3
					# soil can arise if 3 neighbohrs soil, or surrounding soil+surrounding plant = 3
					# plants arise if: 3 water and 3 soil
					# if water:
					# plants arise if water survives and soil grows
					# water survives if 2 or 3 neighbohrs
					# soil grows if 3 neighbohrs
					# if soil:
					# plants arise if soil survives and water grows
					# soil survives if 2 or 3 neighbohrs
					# water grows if 3 neighbohrs
					# if plant:
					# ignore cellpos
					if curcell == ded
						wat = numwater+numplant == 3
						sol = numsoil+numplant == 3
						if wat && sol
							newboard[x,y] = plant
						elseif wat
							newboard[x,y] = water
						elseif sol
							newboard[x,y] = soil
						else
							newboard[x,y] = ded
						end
					elseif curcell == water
						wat = 2 <= numwater+numplant <= 3
						sol = numsoil+numplant == 3
						if wat && sol
							newboard[x,y] = plant
						elseif wat
							newboard[x,y] = water
						elseif sol
							newboard[x,y] = soil
						else
							newboard[x,y] = ded
						end
					elseif curcell == soil
						sol = 2 <= numsoil+numplant <= 3
						wat = numwater+numplant == 3
						if wat && sol
							newboard[x,y] = plant
						elseif wat
							newboard[x,y] = water
						elseif sol
							newboard[x,y] = soil
						else
							newboard[x,y] = ded
						end
					end
				end
			end
		end
	end
	nrows, ncols = size(newboard)
	# Create an empty Set to hold the coordinates of non-zero elements
	nonzero_coords = Set{Tuple{Int, Int}}()

	# Create a lock to prevent race conditions when accessing nonzero_coords
	mutex = ReentrantLock()  # Renaming to 'mutex' to avoid conflict with lock function

	# Use multithreading to process each row in parallel
	Threads.@threads for row_idx in 1:nrows
		# For each row, check all columns
		row_coords = Set{Tuple{Int, Int}}()
		for col_idx in 1:ncols
			if newboard[row_idx, col_idx] != 0
				push!(row_coords, (row_idx, col_idx))
			end
		end
		# Merge the row's results into the global Set (safely)
		lock(mutex) do  # Lock the mutex to ensure safe access to nonzero_coords
			union!(nonzero_coords, row_coords)  # Correctly update nonzero_coords
		end
	end
	fill!(oldboard,ded)
	m.livecells = nonzero_coords
	m.iterations += 1
end
function renderboard(m::b)
	items = ["  ","░░","▒▒","██"]
	out = []
	ob=getoldboard(m)
	for x in 1:size(ob)[1]
		for y in 1:size(ob)[1]
			push!(out,items[ob[x,y]+1])
		end
		push!(out,"\n")
	end
	println(join(out))
	write("final.txt",join(out))
end
function progressbar(progress,size::Int64=50) # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
	k = round(progress*100, digits=1)
	j = "\e[A[" * "="^Int(floor(progress*size)) * ">" * " "^Int((size-floor(progress*size))) * "] $k%"
	println(j)
end
#renderboard(board)
println()
itr = parse(Int64, ARGS[2])
@time for i in 1:itr
	runiteration!(board)
	progressbar(i/itr,150)
end
save(ARGS[1]*".png",getoldboard(board)/3)