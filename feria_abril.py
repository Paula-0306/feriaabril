import threading
import random
import time

AFORO_MAXIMO = 5
TIEMPO_SIMULACION = 30  # segundos que dura la fiesta


class Caseta:
    def __init__(self, personas_extra=0):
        self.aforo = threading.Semaphore(AFORO_MAXIMO)
        self.portero_activo = True
        self.lock = threading.Lock()
        self.dentro = 0

        # Personas que ya estaban dentro
        for _ in range(personas_extra):
            if self.aforo.acquire(blocking=False):
                self.dentro += 1

        if self.dentro > 0:
            print(f" Ya había {self.dentro} personas dentro de la caseta.")

    def intentar_entrar(self, nombre):
        print(f"{nombre} intenta entrar...")

        with self.lock:
            if not self.portero_activo:
                return False

            # 3% probabilidad de perder la paciencia (más raro para alargar)
            if random.random() < 0.03:
                self.portero_activo = False
                print(" El portero pierde la paciencia y llama a la policía.")
                return False

        self.aforo.acquire()

        with self.lock:
            if not self.portero_activo:
                self.aforo.release()
                return False
            self.dentro += 1
            print(f" {nombre} ha entrado. (Dentro: {self.dentro})")

        return True

    def salir(self, nombre):
        with self.lock:
            self.dentro -= 1
            print(f" {nombre} ha salido. (Dentro: {self.dentro})")
        self.aforo.release()

    def abierta(self):
        return self.portero_activo


class Madrileno(threading.Thread):
    def __init__(self, nombre, caseta, fin_simulacion):
        super().__init__(name=nombre)
        self.caseta = caseta
        self.fin_simulacion = fin_simulacion
        self.entradas = 0

    def run(self):
        # Llegada escalonada inicial
        time.sleep(random.uniform(0, 3))

        while time.time() < self.fin_simulacion and self.caseta.abierta():
            entro = self.caseta.intentar_entrar(self.name)
            if not entro:
                break

            self.entradas += 1

            # Tiempo dentro: 1–5 segundos
            time.sleep(random.randint(1, 5))

            self.caseta.salir(self.name)

            # 75% probabilidad de volver
            if random.random() > 0.75:
                print(f" {self.name} se va definitivamente tras {self.entradas} rebujitos.")
                break

            # Descanso antes de volver a la cola
            time.sleep(random.uniform(0.5, 2.5))

        print(f"{self.name} termina con {self.entradas} entradas.")


def main():
    nombres_madrilenos = [
        "Carlos", "Lucía", "Javier", "Marta", "Sergio", "Laura",
        "David", "Paula", "Álvaro", "Elena", "Raúl", "Carmen",
        "Diego", "Sara", "Iván"
    ]

    NUM_MADRILENOS = 12
    PERSONAS_EXTRA = random.randint(0, 3)

    fin_simulacion = time.time() + TIEMPO_SIMULACION
    caseta = Caseta(personas_extra=PERSONAS_EXTRA)

    hilos = []
    for i in range(NUM_MADRILENOS):
        nombre = nombres_madrilenos[i % len(nombres_madrilenos)]
        t = Madrileno(nombre, caseta, fin_simulacion)
        t.start()
        hilos.append(t)

    for t in hilos:
        t.join()

    print("\n Fin de la simulación. ¡Viva la Feria!")


if __name__ == "__main__":
    main()
