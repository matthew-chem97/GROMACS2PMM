import numpy as np
import sys

# --- Impostazioni ---
n_states = 11          # Dimensione della matrice N x N
orca_filename = "Lumi0gradi.out" # File per leggere gli elementi diagonali (i=j)
dipoli_filename = "dipole_matrix.txt" # File per leggere gli elementi off-diagonali (0, j)

# --- Inizializzazione ---
# Crea una matrice N x N x 3 riempita di zeri.
# Soddisfa la Regola 3 (elementi i,j con i,j > 0 e i!=j sono zero).
matrix = np.zeros((n_states, n_states, 3))

# --- 1) Lettura Elementi Diagonali da orca.out ---
diagonal_index = 0
try:
    with open(orca_filename, 'r') as f_orca:
        print(f"Lettura elementi diagonali da '{orca_filename}'...")
        for line_num, line in enumerate(f_orca):
            line_content = line.strip()
            if "Total Dipole Moment" in line_content:
                if diagonal_index < n_states:
                    try:
                        parts = line_content.split()
                        dipole_x = float(parts[-3])
                        dipole_y = float(parts[-2])
                        dipole_z = float(parts[-1])
                        matrix[diagonal_index, diagonal_index] = [dipole_x, dipole_y, dipole_z]
                        # print(f"DEBUG: Trovato diagonale {diagonal_index},{diagonal_index}: {matrix[diagonal_index, diagonal_index]}")
                        diagonal_index += 1
                    except (IndexError, ValueError) as e:
                        print(f"Attenzione [orca.out]: Impossibile estrarre il momento di dipolo dalla riga {line_num+1}: '{line_content}'. Errore: {e}", file=sys.stderr)
    print(f"Letti {diagonal_index} elementi diagonali.")
    # Controllo se sono stati trovati abbastanza elementi diagonali
    if diagonal_index < n_states:
         print(f"Attenzione: Trovati solo {diagonal_index} elementi diagonali in '{orca_filename}', ma ne erano attesi {n_states}.", file=sys.stderr)

except FileNotFoundError:
    print(f"Errore: Il file '{orca_filename}' non è stato trovato. Impossibile leggere gli elementi diagonali.", file=sys.stderr)
    # Si potrebbe decidere di uscire qui o continuare con diagonali a zero
    # sys.exit(1) # Decommenta per uscire se orca.out è essenziale
except Exception as e:
    print(f"Errore inaspettato durante la lettura di '{orca_filename}': {e}", file=sys.stderr)


# --- 2) Lettura Elementi Riga 0 (0,j) da dipoli.txt ---
transition_j = 1 # Indice per gli stati 0->1, 0->2, ... (parte da 1)
lines_read_dipoli = 0
try:
    with open(dipoli_filename, 'r') as f_dipoli:
        print(f"Lettura elementi riga 0 da '{dipoli_filename}'...")
        for line_num, line in enumerate(f_dipoli):
            line_content = line.strip()
            if not line_content: # Salta righe vuote
                continue

            # Controlla se abbiamo già letto abbastanza transizioni
            if transition_j >= n_states:
                print(f"Nota [dipoli.txt]: Raggiunto n_states ({n_states}). Ignoro riga {line_num+1} e successive.")
                break # Esce dal ciclo for

            try:
                parts = line_content.split()
                # Verifica che ci siano esattamente 3 colonne
                if len(parts) == 3:
                    trans_x = float(parts[0])
                    trans_y = float(parts[1])
                    trans_z = float(parts[2])
                    matrix[0, transition_j] = [trans_x, trans_y, trans_z]
                    # print(f"DEBUG: Trovato transizione 0,{transition_j}: {matrix[0, transition_j]}")
                    transition_j += 1
                    lines_read_dipoli += 1
                else:
                    print(f"Attenzione [dipoli.txt]: Riga {line_num+1} non contiene esattamente 3 colonne: '{line_content}'. Riga ignorata.", file=sys.stderr)
            except ValueError as e:
                print(f"Attenzione [dipoli.txt]: Impossibile convertire in numeri i valori sulla riga {line_num+1}: '{line_content}'. Errore: {e}. Riga ignorata.", file=sys.stderr)

    print(f"Letti {lines_read_dipoli} elementi per la riga 0.")
    # Controllo se sono state lette abbastanza righe da dipoli.txt
    expected_dipoli_lines = n_states - 1
    if lines_read_dipoli < expected_dipoli_lines:
        print(f"Attenzione: Lette solo {lines_read_dipoli} righe valide da '{dipoli_filename}', ma ne erano attese {expected_dipoli_lines} per popolare la riga 0 fino a j={n_states-1}.", file=sys.stderr)

except FileNotFoundError:
    print(f"Errore: Il file '{dipoli_filename}' non è stato trovato. Impossibile leggere gli elementi della riga 0.", file=sys.stderr)
    # Si potrebbe decidere di uscire qui o continuare con la riga 0 a zero
    # sys.exit(1)
except Exception as e:
    print(f"Errore inaspettato durante la lettura di '{dipoli_filename}': {e}", file=sys.stderr)


# --- 4) Simmetria per la Colonna 0 (i, 0 con i > 0) ---
# Questo si basa sui valori letti da dipoli.txt e messi in matrix[0, j]
print("Applicazione simmetria per colonna 0...")
for i in range(1, n_states):
    matrix[i, 0] = matrix[0, i] # Copia M(0,i) in M(i,0)


# --- 5) Stampa della Matrice ---
print(f"\n--- Matrice dei Momenti di Transizione ({n_states}x{n_states}) ---")
for i in range(n_states):
    for j in range(n_states):
        # Formatta i valori con una precisione fissa per leggibilità
        val_x = matrix[i, j, 0]
        val_y = matrix[i, j, 1]
        val_z = matrix[i, j, 2]
        # Usa f-string per formattazione allineata
        print(f"{i:<3} {j:<3}  {val_x: 12.8f} {val_y: 12.8f} {val_z: 12.8f}")
print("--- Fine Matrice ---")
