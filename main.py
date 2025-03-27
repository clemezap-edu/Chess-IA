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
CHECK_COLOR = (255, 0, 0, 128)  # Rojo semi-transparente para indicar jaque
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
        self.small_font = pygame.font.SysFont("Arial", 16)

        # Tablero de ajedrez
        self.board = chess.Board()

        # Historial de posiciones para detectar repeticiones
        self.position_history = {}

        # Contador de movimientos para la regla de los 50 movimientos
        self.halfmove_clock = 0

        # Historial de movimientos
        self.move_history = []

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
        self.status_text = ""
        self.running = True
        self.last_move = None

        # Cargar imágenes
        self.load_piece_images()

    def load_piece_images(self):
        """Cargar imágenes de las piezas desde la carpeta 'pieces'"""
        self.piece_images = {}

        # Verificar si existe el directorio de piezas
        pieces_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pieces")
        if not os.path.exists(pieces_dir):
            print(f"Directorio de piezas no encontrado en {pieces_dir}")
            print("Usando representación de texto para las piezas")
            return

        try:
            # Mapeo de piezas a archivos de imagen
            piece_files = {
                'P': 'white_pawn.png',
                'R': 'white_rook.png',
                'N': 'white_knight.png',
                'B': 'white_bishop.png',
                'Q': 'white_queen.png',
                'K': 'white_king.png',
                'p': 'black_pawn.png',
                'r': 'black_rook.png',
                'n': 'black_knight.png',
                'b': 'black_bishop.png',
                'q': 'black_queen.png',
                'k': 'black_king.png'
            }

            for piece, file_name in piece_files.items():
                file_path = os.path.join(pieces_dir, file_name)
                if os.path.exists(file_path):
                    image = pygame.image.load(file_path)
                    # Escalar la imagen al tamaño del cuadrado
                    image = pygame.transform.scale(image, (self.square_size, self.square_size))
                    self.piece_images[piece] = image
                else:
                    print(f"Imagen no encontrada: {file_path}")

            print(f"Se cargaron {len(self.piece_images)} imágenes de piezas")
        except Exception as e:
            print(f"Error al cargar imágenes: {e}")
            # Si hay error, usaremos la representación de texto

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
                    text = self.small_font.render(str(8 - row), True, TEXT_COLOR if color == LIGHT_SQUARE else WHITE)
                    self.screen.blit(text, (5, y + 5))
                if row == 7:
                    text = self.small_font.render(chr(97 + col), True, TEXT_COLOR if color == LIGHT_SQUARE else WHITE)
                    self.screen.blit(text, (x + self.square_size - 15, self.screen_height - 800 + 5))

    def draw_pieces(self):
        # Dibujar las piezas
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                x = col * self.square_size
                y = row * self.square_size

                # Si tenemos imágenes cargadas, usarlas
                if hasattr(self, 'piece_images') and self.piece_images:
                    piece_symbol = piece.symbol()
                    if piece_symbol in self.piece_images:
                        self.screen.blit(self.piece_images[piece_symbol], (x, y))
                    else:
                        self.draw_text_piece(piece, x, y)
                else:
                    self.draw_text_piece(piece, x, y)

    def draw_text_piece(self, piece, x, y):
        # Dibujar pieza como texto con círculo de fondo
        piece_symbols = {
            chess.PAWN: 'P', chess.ROOK: 'R', chess.KNIGHT: 'N',
            chess.BISHOP: 'B', chess.QUEEN: 'Q', chess.KING: 'K'
        }

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

        # Resaltar casilla del rey en jaque
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            if king_square is not None:
                col = chess.square_file(king_square)
                row = 7 - chess.square_rank(king_square)
                x = col * self.square_size
                y = row * self.square_size

                # Crear superficie con transparencia para indicar jaque
                s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                s.fill(CHECK_COLOR)
                self.screen.blit(s, (x, y))

    def update_display(self):
        # Limpiar pantalla
        self.screen.fill(WHITE)

        # Dibujar tablero
        self.draw_board()
        self.highlight_last_move()
        self.draw_pieces()

        # Mostrar información principal
        info_surface = self.font.render(self.info_text, True, BLACK)
        self.screen.blit(info_surface, (10, self.screen_height - 40))

        # Mostrar estado adicional (jaque, reglas, etc.)
        if self.status_text:
            status_surface = self.small_font.render(self.status_text, True, BLACK)
            self.screen.blit(status_surface, (10, self.screen_height - 70))

        # Mostrar último movimiento en notación algebraica
        if self.move_history:
            last_move_text = f"Último: {self.move_history[-1]}"
            last_move_surface = self.small_font.render(last_move_text, True, BLACK)
            self.screen.blit(last_move_surface, (self.screen_width - 150, self.screen_height - 70))

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

    def update_game_state(self, move):
        """Actualiza el estado del juego tras un movimiento"""
        # Actualizar el contador de movimientos para la regla de 50 movimientos
        if self.board.is_capture(move) or self.board.piece_at(move.from_square).piece_type == chess.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Actualizar historial de posiciones para detectar repeticiones
        fen_position = self.board.fen().split(' ')[0]  # Solo la posición, no el turno ni otros datos
        if fen_position in self.position_history:
            self.position_history[fen_position] += 1
        else:
            self.position_history[fen_position] = 1

        # Guardar el movimiento en el historial
        san_move = self.board.san(move)
        move_number = (len(self.move_history) // 2) + 1

        if self.board.turn == chess.BLACK:  # Si el turno es negro, el movimiento lo hizo blanco
            self.move_history.append(f"{move_number}.{san_move}")
        else:  # Si el turno es blanco, el movimiento lo hizo negro
            self.move_history.append(f"{move_number}...{san_move}")

        # Realizar el movimiento
        self.board.push(move)

        # Actualizar el estado de juego
        self.update_status_text()

    def update_status_text(self):
        """Actualiza el texto de estado con información sobre la situación del juego"""
        status = []

        # Verificar jaque
        if self.board.is_check():
            status.append("JAQUE")

        # Verificar jaque mate o ahogado
        if self.board.is_checkmate():
            status.append("JAQUE MATE")
        elif self.board.is_stalemate():
            status.append("TABLAS POR AHOGADO")

        # Verificar repetición de posición
        current_pos = self.board.fen().split(' ')[0]
        if current_pos in self.position_history and self.position_history[current_pos] >= 3:
            status.append(f"REPETICIÓN ({self.position_history[current_pos]})")

        # Verificar regla de 50 movimientos
        if self.halfmove_clock >= 100:  # 50 movimientos completos = 100 medios movimientos
            status.append("REGLA 50 MOVIMIENTOS")

        # Verificar material insuficiente
        if self.board.is_insufficient_material():
            status.append("MATERIAL INSUFICIENTE")

        # Actualizar text
        self.status_text = " | ".join(status)

    def check_game_over_reason(self):
        """Verifica si el juego ha terminado y devuelve la razón"""
        if self.board.is_checkmate():
            return "Jaque mate"
        elif self.board.is_stalemate():
            return "Tablas por ahogado"
        elif self.board.is_insufficient_material():
            return "Tablas por material insuficiente"
        elif self.halfmove_clock >= 100:
            return "Tablas por regla de 50 movimientos"

        current_pos = self.board.fen().split(' ')[0]
        if current_pos in self.position_history and self.position_history[current_pos] >= 3:
            return "Tablas por repetición triple de posición"

        return None

    def is_game_over_custom(self):
        """Verifica si el juego ha terminado según reglas de ajedrez"""
        # Verificar fin de juego según python-chess
        if self.board.is_game_over():
            return True

        # Verificar regla de 50 movimientos
        if self.halfmove_clock >= 100:
            return True

        # Verificar repetición triple
        current_pos = self.board.fen().split(' ')[0]
        if current_pos in self.position_history and self.position_history[current_pos] >= 3:
            return True

        return False

    def start_game(self):
        try:
            print("Iniciando juego...")
            self.info_text = "Iniciando juego..."
            self.update_display()

            # Bucle principal
            clock = pygame.time.Clock()
            current_player = "Stockfish"

            while not self.is_game_over_custom() and self.running:
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
                        self.update_game_state(move)

                        # Actualizar información
                        self.info_text = f"Último: {self.move_history[-1]} | Turno: {current_player}"
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
                            self.update_game_state(move)
                            self.info_text = f"Recuperado con movimiento aleatorio"
                            self.update_display()
                            time.sleep(1)
                            current_player = "Crafty" if current_player == "Stockfish" else "Stockfish"
                        else:
                            break

                clock.tick(30)

            # Fin del juego
            if self.is_game_over_custom():
                game_over_reason = self.check_game_over_reason()
                result = self.board.result()

                if result == "1-0":
                    winner = "Stockfish (blancas)"
                elif result == "0-1":
                    winner = "Crafty (negras)"
                else:
                    winner = "Empate"

                self.info_text = f"Fin del juego: {result} - Ganador: {winner}"
                if game_over_reason:
                    self.status_text = f"Razón: {game_over_reason}"
                self.update_display()

                print(f"Juego terminado: {result}")
                print(f"Razón: {game_over_reason}")
                print(f"Ganador: {winner}")
                print("Historial de movimientos:")
                for move in self.move_history:
                    print(move, end=" ")
                print("\n")

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
