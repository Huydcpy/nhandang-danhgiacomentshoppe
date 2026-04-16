from streamlit.components.v1 import html


def render_snake_game() -> None:
    html(
        """
        <div class="snake-shell">
          <div class="snake-meta">
            <div>
              <strong>Score:</strong> <span id="score">0</span>
            </div>
            <div>
              <strong>Status:</strong> <span id="status">Running</span>
            </div>
          </div>
          <div id="board" class="snake-board" aria-label="Snake board"></div>
          <div class="snake-actions">
            <button id="pause-btn" type="button">Pause</button>
            <button id="restart-btn" type="button">Restart</button>
          </div>
          <div class="snake-controls">
            <button class="control up" data-direction="up" type="button">↑</button>
            <button class="control left" data-direction="left" type="button">←</button>
            <button class="control down" data-direction="down" type="button">↓</button>
            <button class="control right" data-direction="right" type="button">→</button>
          </div>
          <p class="snake-help">Use arrow keys or WASD. Eat food, avoid walls and your own body.</p>
        </div>

        <style>
          :root {
            color-scheme: light;
          }

          body {
            margin: 0;
            font-family: sans-serif;
            background: transparent;
          }

          .snake-shell {
            max-width: 420px;
            margin: 0 auto;
            color: #1f2937;
          }

          .snake-meta {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 14px;
          }

          .snake-board {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 3px;
            background: #d1d5db;
            padding: 3px;
            border-radius: 10px;
            box-sizing: border-box;
            touch-action: none;
            user-select: none;
          }

          .cell {
            aspect-ratio: 1;
            background: #f9fafb;
            border-radius: 4px;
          }

          .cell.snake {
            background: #2563eb;
          }

          .cell.head {
            background: #1d4ed8;
          }

          .cell.food {
            background: #dc2626;
          }

          .snake-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
          }

          .snake-actions button,
          .snake-controls button {
            border: 1px solid #cbd5e1;
            background: #ffffff;
            color: #111827;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
          }

          .snake-controls {
            display: grid;
            grid-template-columns: repeat(3, 56px);
            grid-template-areas:
              ". up ."
              "left down right";
            gap: 8px;
            justify-content: center;
            margin-top: 14px;
          }

          .control.up { grid-area: up; }
          .control.left { grid-area: left; }
          .control.down { grid-area: down; }
          .control.right { grid-area: right; }

          .snake-help {
            margin: 12px 0 0;
            font-size: 13px;
            color: #4b5563;
          }

          @media (max-width: 480px) {
            .snake-shell {
              max-width: 100%;
            }
          }
        </style>

        <script>
          const boardSize = 12;
          const tickMs = 180;
          const directions = {
            up: { x: 0, y: -1 },
            down: { x: 0, y: 1 },
            left: { x: -1, y: 0 },
            right: { x: 1, y: 0 },
          };
          const opposites = {
            up: "down",
            down: "up",
            left: "right",
            right: "left",
          };
          const keyMap = {
            ArrowUp: "up",
            ArrowDown: "down",
            ArrowLeft: "left",
            ArrowRight: "right",
            w: "up",
            a: "left",
            s: "down",
            d: "right",
            W: "up",
            A: "left",
            S: "down",
            D: "right",
          };

          const board = document.getElementById("board");
          const scoreLabel = document.getElementById("score");
          const statusLabel = document.getElementById("status");
          const pauseButton = document.getElementById("pause-btn");
          const restartButton = document.getElementById("restart-btn");
          const controlButtons = document.querySelectorAll("[data-direction]");

          let intervalId = null;
          let pendingDirection = null;
          let state = null;

          function createInitialState() {
            const center = Math.floor(boardSize / 2);
            const snake = [
              { x: center, y: center },
              { x: center - 1, y: center },
              { x: center - 2, y: center },
            ];
            return {
              snake,
              direction: "right",
              food: placeFood(snake),
              score: 0,
              paused: false,
              gameOver: false,
            };
          }

          function placeFood(snake) {
            const occupied = new Set(snake.map((cell) => `${cell.x},${cell.y}`));
            const available = [];
            for (let y = 0; y < boardSize; y += 1) {
              for (let x = 0; x < boardSize; x += 1) {
                const key = `${x},${y}`;
                if (!occupied.has(key)) {
                  available.push({ x, y });
                }
              }
            }
            return available[Math.floor(Math.random() * available.length)];
          }

          function setDirection(nextDirection) {
            if (!nextDirection || state.gameOver) {
              return;
            }
            const currentDirection = pendingDirection || state.direction;
            if (nextDirection === opposites[currentDirection]) {
              return;
            }
            pendingDirection = nextDirection;
          }

          function step() {
            if (state.paused || state.gameOver) {
              return;
            }

            const directionName = pendingDirection || state.direction;
            pendingDirection = null;
            const vector = directions[directionName];
            const head = state.snake[0];
            const nextHead = { x: head.x + vector.x, y: head.y + vector.y };

            const hitsWall =
              nextHead.x < 0 ||
              nextHead.y < 0 ||
              nextHead.x >= boardSize ||
              nextHead.y >= boardSize;

            if (hitsWall) {
              state = { ...state, direction: directionName, gameOver: true };
              render();
              return;
            }

            const grows = nextHead.x === state.food.x && nextHead.y === state.food.y;
            const collisionBody = grows ? state.snake : state.snake.slice(0, -1);
            const hitsSelf = collisionBody.some(
              (segment) => segment.x === nextHead.x && segment.y === nextHead.y
            );

            if (hitsSelf) {
              state = { ...state, direction: directionName, gameOver: true };
              render();
              return;
            }

            const nextSnake = [nextHead, ...state.snake];
            if (!grows) {
              nextSnake.pop();
            }

            state = {
              ...state,
              snake: nextSnake,
              direction: directionName,
              score: grows ? state.score + 1 : state.score,
              food: grows ? placeFood(nextSnake) : state.food,
            };

            render();
          }

          function render() {
            board.innerHTML = "";
            const snakeCells = new Map(
              state.snake.map((segment, index) => [`${segment.x},${segment.y}`, index])
            );
            for (let y = 0; y < boardSize; y += 1) {
              for (let x = 0; x < boardSize; x += 1) {
                const cell = document.createElement("div");
                cell.className = "cell";
                const key = `${x},${y}`;
                if (x === state.food.x && y === state.food.y) {
                  cell.classList.add("food");
                }
                if (snakeCells.has(key)) {
                  cell.classList.add("snake");
                  if (snakeCells.get(key) === 0) {
                    cell.classList.add("head");
                  }
                }
                board.appendChild(cell);
              }
            }

            scoreLabel.textContent = String(state.score);
            if (state.gameOver) {
              statusLabel.textContent = "Game over";
              pauseButton.textContent = "Pause";
            } else if (state.paused) {
              statusLabel.textContent = "Paused";
              pauseButton.textContent = "Resume";
            } else {
              statusLabel.textContent = "Running";
              pauseButton.textContent = "Pause";
            }
          }

          function restart() {
            pendingDirection = null;
            state = createInitialState();
            render();
          }

          pauseButton.addEventListener("click", () => {
            if (state.gameOver) {
              return;
            }
            state = { ...state, paused: !state.paused };
            render();
          });

          restartButton.addEventListener("click", restart);
          controlButtons.forEach((button) => {
            button.addEventListener("click", () => {
              setDirection(button.dataset.direction);
            });
          });

          window.addEventListener("keydown", (event) => {
            const nextDirection = keyMap[event.key];
            if (nextDirection) {
              event.preventDefault();
              setDirection(nextDirection);
            }
            if (event.key === " " && !state.gameOver) {
              event.preventDefault();
              state = { ...state, paused: !state.paused };
              render();
            }
            if ((event.key === "r" || event.key === "R") && state.gameOver) {
              event.preventDefault();
              restart();
            }
          });

          restart();
          intervalId = window.setInterval(step, tickMs);
        </script>
        """,
        height=620,
    )
