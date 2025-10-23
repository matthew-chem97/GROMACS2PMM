import sys

def swap_specific_lines(input_filename, output_filename):
    """
    Legge un file, scambia specifiche righe secondo una mappa predefinita,
    e scrive il risultato in un nuovo file, preservando le altre righe.

    Args:
        input_filename (str): Percorso del file di input.
        output_filename (str): Percorso del file di output.
    """
    content_source_map = {
        # new_index: old_index
        30: 19,  # Riga 31 (new) <- Riga 20 (old)
        19: 30, 
    }

    # Trova l'indice più alto necessario per lo scambio
    max_index_needed = -1
    indices_involved = set(content_source_map.keys()) | set(content_source_map.values())
    if indices_involved:
         max_index_needed = max(indices_involved)

    try:
        # Leggi tutte le righe dal file di input
        with open(input_filename, 'r', encoding='utf-8') as infile:
            original_lines = infile.readlines() # Legge tutte le righe, mantenendo i caratteri di newline '\n'

        num_lines = len(original_lines)
        print(f"File '{input_filename}' letto, {num_lines} righe trovate.")

        # Controlla se il file ha abbastanza righe per eseguire tutti gli scambi
        required_lines = max_index_needed + 1
        if num_lines < required_lines:
            print(f"Errore: Il file ha solo {num_lines} righe, ma lo scambio richiede almeno {required_lines} righe "
                  f"(l'indice più alto coinvolto è {max_index_needed}, corrispondente alla riga {required_lines}).", file=sys.stderr)
            return # Interrompe l'esecuzione della funzione

        # Crea una copia della lista originale su cui lavorare
        # È importante usare la lista originale come sorgente per tutti gli scambi
        new_lines = original_lines[:]

        # Esegui gli scambi specificati nella mappa
        print("Inizio scambi:")
        for new_idx, old_idx in content_source_map.items():
            # Prende il contenuto dalla riga 'old_idx' della lista *originale*
            # e lo mette alla posizione 'new_idx' nella lista *nuova*.
            print(f"  - La nuova riga {new_idx + 1} prenderà il contenuto dalla vecchia riga {old_idx + 1}")
            new_lines[new_idx] = original_lines[old_idx]

        # Scrivi le righe modificate (e quelle non modificate) nel file di output
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            outfile.writelines(new_lines)

        print("-" * 20)
        print(f"Scambi completati con successo.")
        print(f"Il risultato è stato salvato nel file: '{output_filename}'.")
        if 22 in content_source_map and content_source_map[22] == 24:
             print("\nNOTA sull'assunzione:")
             print("  È stato assunto che la riga 23 dovesse ricevere il contenuto originale della riga 25")
             print("  per completare logicamente il ciclo di scambi 23 -> 24 -> 25 -> 23.")
             print("  Se l'intenzione era diversa, la mappa `content_source_map` nello script va modificata.")

    except FileNotFoundError:
        print(f"Errore: File di input '{input_filename}' non trovato.", file=sys.stderr)
    except IndexError:
         # Questo errore non dovrebbe verificarsi grazie al controllo preliminare sul numero di righe,
         # ma è una buona pratica includerlo.
        print(f"Errore: Tentativo di accedere a un indice di riga non valido. Assicurati che il file '{input_filename}' "
              f"abbia almeno {required_lines} righe.", file=sys.stderr)
    except Exception as e:
        print(f"Si è verificato un errore imprevisto: {e}", file=sys.stderr)

# --- Blocco Principale: Imposta i nomi dei file e chiama la funzione ---
if __name__ == "__main__":
    # <<< MODIFICA QUESTI NOMI SE NECESSARIO >>>
    nome_file_input = "input.txt"
    nome_file_output = "output.txt"
    # <<< ---------------------------------- >>>

    # --- Opzionale: Crea un file di input di esempio se non esiste ---
    try:
        with open(nome_file_input, 'x', encoding='utf-8') as f:
            print(f"Creato file di esempio '{nome_file_input}'.")
            print("Riempilo con almeno 31 righe di testo per un test corretto.")
            # Creiamo un file con 40 righe per sicurezza
            for i in range(1, 41):
                f.write(f"Contenuto originale della riga {i}\n")
    except FileExistsError:
        print(f"Il file di input '{nome_file_input}' esiste già.")
        pass # File già esistente, va bene così
    # --- Fine creazione file di esempio ---

    # Chiama la funzione per eseguire gli scambi
    swap_specific_lines(nome_file_input, nome_file_output)
