import threading
import random
import time

AFORO_MAXIMO = 5


class Caseta:
    def __init__(self, personas_extra=0):
        # Semáforo de aforo
        self.aforo = threading.Semaphore(AFORO_MAXIMO)

        # Estado del portero
        self.portero_activo = True
        self.lock = threading.Lock()

        # Personas que ya estaban dentro (no madrileños)
        self.dentro = 0

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

            # 5% probabilidad de que el portero pierda la paciencia
            if random.random() < 0.05:
                self.portero_activo = False
                print(" El portero pierde la paciencia y llama a la policía.")
                return False

        # Esperar hueco en la caseta
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
    def __init__(self, nombre, caseta):
        super().__init__(name=nombre)
        self.caseta = caseta

    def run(self):
        while self.caseta.abierta():
            entro = self.caseta.intentar_entrar(self.name)
            if not entro:
                break

            # Tiempo dentro: 1–5 segundos
            time.sleep(random.randint(1, 5))

            self.caseta.salir(self.name)

            # 75% de probabilidad de volver
            if random.random() > 0.75:
                print(f" {self.name} se va definitivamente.")
                break

            # Espera antes de reintentarlo
            time.sleep(random.uniform(0.5, 2))


def main():
    NUM_MADRILENOS = 12  # mínimo 10
    PERSONAS_EXTRA = random.randint(0, 3)  # gente que ya estaba dentro

    caseta = Caseta(personas_extra=PERSONAS_EXTRA)

    hilos = []
    for i in range(NUM_MADRILENOS):
        t = Madrileno(f"Madrileño-{i+1}", caseta)
        t.start()
        hilos.append(t)

    for t in hilos:
        t.join()

    print("\n Fin de la simulación.")


if __name__ == "__main__":
    main()
