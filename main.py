
import chess
import subprocess
import time
import os
import sys
import pygame
import threading

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105)
TEXT_COLOR = (0, 0, 0)


class ChessGame:
    def __init__(self):
        # Inicializar pygame
        pygame.init()
        self.screen_width = 800
        self.screen_height = 850
        self.square_size = self.screen_width // 8
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Stockfish vs Crafty")

        # Fuente para el texto
        self.font = pygame.font.SysFont("Arial", 24)

        # Tablero de ajedrez
        self.board = chess.Board()

        # Rutas de los motores - comprobar varias ubicaciones posibles
        self.stockfish_paths = [
            "/usr/games/stockfish",
            "/usr/bin/stockfish",
            "/usr/local/bin/stockfish"
        ]

        self.crafty_paths = [
            "/usr/games/crafty",
            "/usr/bin/crafty",
            "/usr/local/bin/crafty"
        ]

        # Probar cada ruta
        self.stockfish_path = None
        for path in self.stockfish_paths:
            if os.path.exists(path):
                self.stockfish_path = path
                break

        self.crafty_path = None
        for path in self.crafty_paths:
            if os.path.exists(path):
                self.crafty_path = path
                break

        # Verificar que se encontraron los motores
        if not self.stockfish_path:
            print("Error: No se encontró Stockfish en el sistema")
            print("Intenta instalarlo con: sudo apt-get install stockfish")
            pygame.quit()
            sys.exit()

        if not self.crafty_path:
            print("Error: No se encontró crafty en el sistema")
            print("Intenta instalarlo con: sudo apt-get install crafty")
            pygame.quit()
            sys.exit()

        print(f"Stockfish encontrado en: {self.stockfish_path}")
        print(f"Crafty encontrado en: {self.crafty_path}")

        # Estado del juego
        self.info_text = "Iniciando juego..."
        self.running = True
        self.last_move = None

    def draw_board(self):
        # Dibujar el tablero
        for row in range(8):
            for col in range(8):
                x = col * self.square_size
                y = row * self.square_size
                if (row + col) % 2 == 0:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE
                pygame.draw.rect(self.screen, color, pygame.Rect(x, y, self.square_size, self.square_size))

                # Coordenadas
                if col == 0:
                    text = self.font.render(str(8 - row), True, TEXT_COLOR if color == LIGHT_SQUARE else WHITE)
                    self.screen.blit(text, (5, y + 5))
                if row == 7:
                    text = self.font.render(chr(97 + col), True, TEXT_COLOR if color == LIGHT_SQUARE else WHITE)
                    self.screen.blit(text, (x + self.square_size - 15, self.screen_height - 800 + 5))

    def draw_pieces(self):
        # Dibujar las piezas
        piece_symbols = {
            chess.PAWN: 'P', chess.ROOK: 'R', chess.KNIGHT: 'N',
            chess.BISHOP: 'B', chess.QUEEN: 'Q', chess.KING: 'K'
        }

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                x = col * self.square_size
                y = row * self.square_size

                # Dibujar pieza como texto con círculo de fondo
                symbol = piece_symbols[piece.piece_type]
                text_color = BLACK if not piece.color else WHITE
                bg_color = WHITE if not piece.color else BLACK

                # Círculo de fondo
                pygame.draw.circle(
                    self.screen,
                    bg_color,
                    (x + self.square_size // 2, y + self.square_size // 2),
                    self.square_size // 3
                )

                # Dibujar el símbolo
                text = self.font.render(symbol, True, text_color)
                text_rect = text.get_rect(center=(x + self.square_size // 2, y + self.square_size // 2))
                self.screen.blit(text, text_rect)

    def highlight_last_move(self):
        # Resaltar el último movimiento
        if self.last_move:
            from_square = self.last_move.from_square
            to_square = self.last_move.to_square

            # Resaltar casilla de origen
            col_from = chess.square_file(from_square)
            row_from = 7 - chess.square_rank(from_square)
            x_from = col_from * self.square_size
            y_from = row_from * self.square_size
            pygame.draw.rect(self.screen, HIGHLIGHT, pygame.Rect(x_from, y_from, self.square_size, self.square_size), 4)

            # Resaltar casilla de destino
            col_to = chess.square_file(to_square)
            row_to = 7 - chess.square_rank(to_square)
            x_to = col_to * self.square_size
            y_to = row_to * self.square_size
            pygame.draw.rect(self.screen, HIGHLIGHT, pygame.Rect(x_to, y_to, self.square_size, self.square_size), 4)

    def update_display(self):
        # Limpiar pantalla
        self.screen.fill(WHITE)

        # Dibujar tablero
        self.draw_board()
        self.highlight_last_move()
        self.draw_pieces()

        # Mostrar información
        info_surface = self.font.render(self.info_text, True, BLACK)
        self.screen.blit(info_surface, (10, self.screen_height - 40))

        # Actualizar pantalla
        pygame.display.flip()

    def get_stockfish_move(self, fen, time_limit=1000):
        """Obtener un movimiento de Stockfish usando comunicación directa"""
        try:
            # Iniciar Stockfish como subproceso
            process = subprocess.Popen(
                self.stockfish_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

            # Configurar el motor
            commands = [
                "uci",
                "isready",
                f"position fen {fen}",
                f"go movetime {time_limit}",
            ]

            # Enviar comandos
            for cmd in commands:
                process.stdin.write(cmd + "\n")
                process.stdin.flush()

            # Esperar y leer la salida
            best_move = None
            start_time = time.time()

            while time.time() - start_time < (time_limit / 1000) + 1:
                if process.stdout.readable():
                    line = process.stdout.readline().strip()
                    if line.startswith("bestmove"):
                        best_move = line.split()[1]
                        break

            # Cerrar el proceso
            process.terminate()

            if best_move:
                return chess.Move.from_uci(best_move)

            return None
        except Exception as e:
            print(f"Error al obtener movimiento de Stockfish: {e}")
            return None

    def get_crafty_move(self, fen, time_limit=1000):
        """Obtener un movimiento de crafty usando xboard"""
        try:
            # Iniciar crafty como subproceso
            process = subprocess.Popen(
                self.crafty_path,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

            # Configurar el motor usando protocolo xboard
            commands = [
                "xboard",
                "protover 2",
                f"setboard {fen}",
                f"st {time_limit / 1000}",
                "go",
            ]

            # Enviar comandos
            for cmd in commands:
                process.stdin.write(cmd + "\n")
                process.stdin.flush()

            # Esperar y leer la salida
            best_move = None
            start_time = time.time()

            while time.time() - start_time < (time_limit / 1000) + 3:
                if process.stdout.readable():
                    line = process.stdout.readline().strip()
                    if line.startswith("move"):
                        best_move = line.split()[1]
                        break

            # Cerrar el proceso
            process.terminate()

            if best_move:
                # Convertir notación algebraica a UCI si es necesario
                try:
                    return chess.Move.from_uci(best_move)
                except ValueError:
                    # Intentar interpretar como movimiento algebraico
                    legal_moves = list(self.board.legal_moves)
                    for move in legal_moves:
                        if self.board.san(move) == best_move:
                            return move

            # Si no se encontró movimiento, usar un enfoque alternativo
            try:
                # Iniciar proceso alternativo usando UCI
                process = subprocess.Popen(
                    [self.crafty_path, "-u"],  # -u para UCI
                    universal_newlines=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )

                # Configurar similar a Stockfish
                commands = [
                    "uci",
                    "isready",
                    f"position fen {fen}",
                    f"go movetime {time_limit}",
                ]

                for cmd in commands:
                    process.stdin.write(cmd + "\n")
                    process.stdin.flush()

                # Leer salida
                start_time = time.time()
                while time.time() - start_time < (time_limit / 1000) + 1:
                    line = process.stdout.readline().strip()
                    if line.startswith("bestmove"):
                        return chess.Move.from_uci(line.split()[1])

                process.terminate()
            except Exception as e:
                print(f"Error en enfoque alternativo: {e}")

            # En caso de fallo, usar un movimiento legal aleatorio
            legal_moves = list(self.board.legal_moves)
            if legal_moves:
                import random
                return random.choice(legal_moves)

            return None
        except Exception as e:
            print(f"Error al obtener movimiento de crafty: {e}")
            return None

    def start_game(self):
        try:
            print("Iniciando juego...")
            self.info_text = "Iniciando juego..."
            self.update_display()

            # Bucle principal
            clock = pygame.time.Clock()
            current_player = "Stockfish"

            while not self.board.is_game_over() and self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                if self.running:
                    try:
                        # Obtener FEN actual
                        current_fen = self.board.fen()

                        if current_player == "Stockfish":
                            self.info_text = f"Turno de Stockfish (blancas), pensando..."
                            self.update_display()

                            move = self.get_stockfish_move(current_fen)
                            if not move or move not in self.board.legal_moves:
                                print("Stockfish devolvió un movimiento inválido o ninguno")
                                # Usar un movimiento legal aleatorio
                                legal_moves = list(self.board.legal_moves)
                                if legal_moves:
                                    import random
                                    move = random.choice(legal_moves)
                                else:
                                    break

                            current_player = "Crafty"
                        else:
                            self.info_text = f"Turno de Crafty (negras), pensando..."
                            self.update_display()

                            move = self.get_crafty_move(current_fen)
                            if not move or move not in self.board.legal_moves:
                                print("Crafty devolvió un movimiento inválido o ninguno")
                                # Usar un movimiento legal aleatorio
                                legal_moves = list(self.board.legal_moves)
                                if legal_moves:
                                    import random
                                    move = random.choice(legal_moves)
                                else:
                                    break

                            current_player = "Stockfish"

                        # Realizar movimiento
                        self.last_move = move
                        san_move = self.board.san(move)
                        self.board.push(move)

                        move_text = f"{san_move}"
                        self.info_text = f"Último movimiento: {move_text} | Turno: {current_player}"
                        self.update_display()

                        # Pausa para ver el movimiento
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Error en movimiento: {str(e)}")
                        self.info_text = f"Error: {str(e)}"
                        self.update_display()
                        time.sleep(2)

                        # Intentar recuperarse
                        legal_moves = list(self.board.legal_moves)
                        if legal_moves:
                            import random
                            move = random.choice(legal_moves)
                            self.last_move = move
                            self.board.push(move)
                            self.info_text = f"Recuperado con movimiento aleatorio"
                            self.update_display()
                            time.sleep(1)
                            current_player = "Crafty" if current_player == "Stockfish" else "Stockfish"
                        else:
                            break

                clock.tick(30)

            # Fin del juego
            if self.board.is_game_over():
                result = self.board.result()
                if result == "1-0":
                    winner = "Stockfish (blancas)"
                elif result == "0-1":
                    winner = "Crafty (negras)"
                else:
                    winner = "Empate"

                self.info_text = f"Fin del juego: {result} - Ganador: {winner}"
                self.update_display()

                # Esperar antes de salir
                waiting = True
                while waiting and self.running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            waiting = False
                    clock.tick(30)

        except Exception as e:
            print(f"Error general: {str(e)}")
            self.info_text = f"Error: {str(e)}"
            self.update_display()
            time.sleep(5)

        finally:
            pygame.quit()


if __name__ == "__main__":
    try:
        game = ChessGame()
        game.start_game()
    except Exception as e:
        print(f"Error de inicialización: {str(e)}")
        pygame.quit()