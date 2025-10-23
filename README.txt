README
This file allow the creation of useful files for MD-PMM calculations.
You need to load the ORCA .out file with the TD-DFT calculation
The program is still modular, further version will be more user-friendly and automatic.

1)Launch the parser.py. it will create the geomtry with converted symbols to mass
python3 parser.py name.out

2)Create a file called "off_diagonal.txt" with the off-diagonal terms.
You can simpli cut & cupy with vi. from the output. it is very easy operation
In futher version it will be directly implemented in matrix.py but for the moment a manual effort is required.

3)Edit matrix.py
Here you can insert the name of the output and the name of the off_diagonal elementrs.
Launch as
python3 matrix.py > out.txt
It will generate you the full dipole matrix ready to use in a PMM calculation !
4)order.py
It could be useful if you need to switch some lines to maintain the MD order.
The script is very efficient in exchanging rows.
Be careful when you use, switches are done sequentally !

