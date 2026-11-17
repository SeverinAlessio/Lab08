from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """

        risultati = []
        for distributore in self._distributori or []:
          prezzi_mese = [
            prezzo.prezzo_litro
            for prezzo in distributore.get_prezzi()
            if prezzo.data.month == mese
           ]
          if prezzi_mese:
              media = sum(prezzi_mese) / len(prezzi_mese)
              risultati.append((distributore.nome, media))
        return risultati

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        for id_distributore, prezzi_giornalieri in prezzi_settimana.items():
            costo_carburante = prezzi_giornalieri[giorno - 1] * 100

            costo_spostamento = 0
            if (
                    ultimo_distributore is not None
                    and id_distributore != ultimo_distributore
            ):
                costo_spostamento = 5

            sequenza_parziale.append(id_distributore)

            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                costo_corrente + costo_carburante + costo_spostamento,
                prezzi_settimana
            )

            sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for distributore in self._distributori or []:
            prezzi = [
                prezzo
                for prezzo in distributore.get_prezzi()
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7
            ]

            prezzi.sort(key=lambda prezzo: prezzo.data)

            prezzi_settimana[distributore.id] = [
                prezzo.prezzo_litro for prezzo in prezzi
            ]

        return prezzi_settimana