import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

interface GameOption {
  text: string;
  target: string;
}

interface GameNode {
  description: string;
  options: { [key: string]: GameOption };
}

interface GameGraph {
  [key: string]: GameNode;
}

@Component({
  selector: 'app-adventure-game',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  template: `
    <div class="game-container">
      <h1>Game</h1>

      <!-- Schermata iniziale -->
      <div *ngIf="gameState === 'initial'" class="initial-screen">
        <div class="button-container">
          <button
            class="game-button secondary-button"
            (click)="loadAndStartGame()"
            [disabled]="isLoading">
            {{ isLoading ? 'Caricamento...' : 'Play' }}
          </button>
        </div>

        <div *ngIf="error" class="error-message">
          {{ error }}
        </div>
      </div>

      <!-- Schermata di gioco -->
      <div *ngIf="gameState === 'playing'" class="game-screen">
        <div class="story-container">
          <div class="story-text" [innerHTML]="getFormattedDescription()"></div>

          <div class="options-container" *ngIf="currentNode?.options && hasOptions()">
            <button
              *ngFor="let option of getOptionKeys()"
              class="option-button"
              (click)="selectOption(option)"
              [disabled]="isTransitioning">
              {{ getOptionText(option) }}
            </button>
          </div>

          <div *ngIf="isGameOver" class="game-over">
            <h2 *ngIf="isWin">🎉 Vittoria!</h2>
            <h2 *ngIf="!isWin">💀 Fine del gioco!</h2>
            <div class="game-result">
              <p *ngIf="isWin">Hai completato con successo l'avventura e ottenuto il tesoro!</p>
              <p *ngIf="!isWin">La tua avventura è terminata qui...</p>
            </div>
            <button class="game-button" (click)="restartGame()">
              Ricomincia
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .game-container {
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      font-family: 'Georgia', serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      color: white;
    }

    h1 {
      text-align: center;
      font-size: 2.5em;
      margin-bottom: 30px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .initial-screen {
      text-align: center;
      margin-top: 100px;
    }

    .button-container {
      display: flex;
      gap: 20px;
      justify-content: center;
      margin-bottom: 20px;
    }

    .game-button {
      padding: 15px 30px;
      font-size: 1.2em;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s ease;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .primary-button {
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      color: white;
    }

    .primary-button:hover:not(:disabled) {
      background: linear-gradient(45deg, #ee5a24, #ff6b6b);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }

    .secondary-button {
      background: linear-gradient(45deg, #4ecdc4, #44a08d);
      color: white;
    }

    .secondary-button:hover:not(:disabled) {
      background: linear-gradient(45deg, #44a08d, #4ecdc4);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }

    .game-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .game-screen {
      background: rgba(255,255,255,0.1);
      border-radius: 15px;
      padding: 30px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.2);
    }

    .story-container {
      text-align: center;
    }

    .story-text {
      font-size: 1.1em;
      line-height: 1.8;
      margin-bottom: 30px;
      background: rgba(255,255,255,0.1);
      padding: 25px;
      border-radius: 10px;
      border-left: 4px solid #4ecdc4;
      text-align: left;
      max-height: 400px;
      overflow-y: auto;
    }

    .story-text ::ng-deep h3 {
      color: #ffeaa7;
      margin-top: 20px;
      margin-bottom: 10px;
    }

    .story-text ::ng-deep strong {
      color: #74b9ff;
    }

    .story-text ::ng-deep ul {
      margin: 10px 0;
      padding-left: 20px;
    }

    .story-text ::ng-deep li {
      margin: 5px 0;
    }

    .options-container {
      display: flex;
      flex-direction: column;
      gap: 15px;
      max-width: 500px;
      margin: 0 auto;
    }

    .option-button {
      padding: 15px 20px;
      background: linear-gradient(45deg, #ffeaa7, #fdcb6e);
      color: #2d3436;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 1.0em;
      font-weight: bold;
      transition: all 0.3s ease;
      text-align: left;
      word-wrap: break-word;
      line-height: 1.4;
    }

    .option-button:hover:not(:disabled) {
      background: linear-gradient(45deg, #fdcb6e, #ffeaa7);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }

    .option-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .error-message {
      color: #ff6b6b;
      background: rgba(255,107,107,0.1);
      padding: 15px;
      border-radius: 8px;
      margin-top: 20px;
      border: 1px solid rgba(255,107,107,0.3);
    }

    .game-over {
      margin-top: 30px;
      background: rgba(255,255,255,0.1);
      padding: 30px;
      border-radius: 10px;
    }

    .game-over h2 {
      color: #ffeaa7;
      margin-bottom: 20px;
      font-size: 2em;
    }

    .game-result {
      margin-bottom: 25px;
      font-size: 1.2em;
      line-height: 1.6;
    }

    .transition-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }

    .transition-message {
      background: rgba(255,255,255,0.9);
      color: #2d3436;
      padding: 20px;
      border-radius: 10px;
      font-size: 1.2em;
      font-weight: bold;
    }

    @media (max-width: 600px) {
      .button-container {
        flex-direction: column;
        align-items: center;
      }

      .game-container {
        padding: 10px;
      }

      .story-text {
        font-size: 1.0em;
        padding: 20px;
      }

      .option-button {
        font-size: 0.9em;
        padding: 12px 15px;
      }
    }
  `]
})
export class GameComponent implements OnInit {
  gameState: 'initial' | 'playing' = 'initial';
  gameGraph: GameGraph = {};
  currentNodeId: string = '';
  currentNode: GameNode | null = null;
  isGenerating = false;
  isLoading = false;
  isGameOver = false;
  isWin = false;
  isTransitioning = false;
  error = '';

  // Configura qui la base URL delle tue API
  private apiBaseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // Inizializzazione del componente
  }

  generateStory() {
    this.isGenerating = true;
    this.error = '';

    this.http.get(`${this.apiBaseUrl}/genStory`).subscribe({
      next: () => {
        this.isGenerating = false;
        console.log('Storia generata con successo!');
      },
      error: (err) => {
        this.isGenerating = false;
        this.error = 'Errore nella generazione della storia. Riprova.';
        console.error('Errore genStory:', err);
      }
    });
  }

  loadAndStartGame() {
    this.isLoading = true;
    this.error = '';

    this.http.get<GameGraph>(`${this.apiBaseUrl}/getGraph`).subscribe({
      next: (graph) => {
        this.gameGraph = graph;
        this.startGame();
        this.isLoading = false;
      },
      error: (err) => {
        this.isLoading = false;
        this.error = 'Errore nel caricamento del gioco. Assicurati che la storia sia stata generata.';
        console.error('Errore loadGraph:', err);
      }
    });
  }

  startGame() {
    this.currentNodeId = 'node_1';
    this.currentNode = this.gameGraph[this.currentNodeId];
    this.gameState = 'playing';
    this.isGameOver = false;
    this.isWin = false;

    if (!this.currentNode) {
      this.error = 'Errore: nodo iniziale non trovato nel grafo.';
      this.gameState = 'initial';
    }
  }

  selectOption(optionKey: string) {
    if (!this.currentNode || this.isTransitioning) return;

    const option = this.currentNode.options[optionKey];
    if (!option) return;

    this.isTransitioning = true;

    // Breve delay per migliorare l'esperienza utente
    setTimeout(() => {
      const nextNodeId = option.target;

      console.log('Trying to navigate to node:', nextNodeId);
      console.log('Node exists in graph:', !!this.gameGraph[nextNodeId]);

      // Clean the node ID by removing special characters and extra spaces
      const cleanedNodeId = nextNodeId.replace(/\s*✅\s*$/, '').trim();

      if (this.gameGraph[cleanedNodeId]) {
        // The node exists in the graph, navigate to it
        this.currentNodeId = cleanedNodeId;
        this.currentNode = this.gameGraph[cleanedNodeId];
        console.log('Successfully navigated to node:', cleanedNodeId);

        // Check if it's a terminal node
        this.checkGameEnd();
      } else {
        // The node doesn't exist in the graph
        console.log('Target node not found in graph, ending game');
        console.log('Option text:', option.text);
        console.log('Target node:', nextNodeId);

        this.isGameOver = true;
        // Determine win/loss based on multiple factors
        this.isWin = this.isWinningCondition(option.text, nextNodeId);

        console.log('Game ended - isWin:', this.isWin);
      }

      this.isTransitioning = false;
    }, 500);
  }

  checkGameEnd() {
    if (!this.currentNode) return;

    // Check if the node has options
    const hasOptions = this.currentNode.options && Object.keys(this.currentNode.options).length > 0;

    if (!hasOptions) {
      this.isGameOver = true;
      // Check if it's a winning node
      this.isWin = this.isWinningNode();
      console.log('Game ended - isWin:', this.isWin, 'isGameOver:', this.isGameOver);
    }
  }

  getOptionKeys(): string[] {
    if (!this.currentNode?.options) return [];
    return Object.keys(this.currentNode.options);
  }

  getOptionText(optionKey: string): string {
    if (this.currentNode?.options && this.currentNode.options[optionKey]) {
      let optionText = this.currentNode.options[optionKey].text;

      // Remove metadata from options (everything in parentheses at the end)
      optionText = optionText.replace(/\s*\([^)]*\)\s*$/, '');

      // Remove asterisks at the beginning
      optionText = optionText.replace(/^\*+\s*/, '');

      // Remove colons at the end
      optionText = optionText.replace(/:\s*$/, '');

      return optionText.trim();
    }
    return `Opzione ${optionKey}`;
  }

  hasOptions(): boolean {
    return !!(this.currentNode?.options && Object.keys(this.currentNode.options).length > 0);
  }

  isWinningNode(): boolean {
    // Check if the current node is a winning node (contains ✅ or winning indicators)
    console.log('Current node description:', this.currentNode?.description);

    const description = this.currentNode?.description || '';
    const hasWinSymbol = description.includes('✅');
    const hasWinText = this.containsWinningText(description);

    console.log('Contains ✅:', hasWinSymbol);
    console.log('Contains winning text:', hasWinText);

    return hasWinSymbol || hasWinText;
  }

  isWinningCondition(optionText: string, targetNodeId: string): boolean {
    // Check multiple indicators for winning condition

    // 1. Check if target node ID contains win symbol
    const nodeIdHasWinSymbol = targetNodeId.includes('✅');

    // 2. Check if option text contains winning indicators
    const optionHasWinText = this.containsWinningText(optionText);

    // 3. Check if option mentions puzzle solving (context-specific)
    const puzzleRelated = optionText.toLowerCase().includes('puzzle') ||
                         optionText.toLowerCase().includes('solve');

    // 4. Check current game state for treasure/success context
    const currentDescription = this.currentNode?.description || '';
    const isInTreasureContext = currentDescription.toLowerCase().includes('treasure') ||
                               currentDescription.toLowerCase().includes('vault') ||
                               currentDescription.toLowerCase().includes('altar');

    console.log('Win condition analysis:');
    console.log('- Node ID has ✅:', nodeIdHasWinSymbol);
    console.log('- Option has winning text:', optionHasWinText);
    console.log('- Puzzle related:', puzzleRelated);
    console.log('- In treasure context:', isInTreasureContext);

    // If we're in a treasure/altar context and the option is about solving a puzzle,
    // and the target node has a win symbol, it's likely a win
    if (isInTreasureContext && puzzleRelated && nodeIdHasWinSymbol) {
      return true;
    }

    // Otherwise, check for explicit winning indicators
    return nodeIdHasWinSymbol || optionHasWinText;
  }

  containsWinningText(text: string): boolean {
    const winningKeywords = [
      'tesoro', 'treasure', 'vittoria', 'victory', 'successo', 'success',
      'completato', 'completed', 'vinto', 'won', 'triumph', 'achieve',
      'treasure_claimed: true', 'puzzle_solved: true'
    ];

    const lowerText = text.toLowerCase();
    return winningKeywords.some(keyword => lowerText.includes(keyword.toLowerCase()));
  }

  getFormattedDescription(): string {
    if (!this.currentNode) return '';

    let description = this.currentNode.description;

    // Extract only the "Narrative Description" section
    const narrativeMatch = description.match(/\*\*Narrative Description:\*\*\s*([\s\S]*?)(?=\n\*\*|$)/);

    if (narrativeMatch) {
      description = narrativeMatch[1].trim();
    }

    // Convert markdown to basic HTML
    description = description
      // Convert **text** to <strong>text</strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Convert *text* to <em>text</em>
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Convert line breaks to <br>
      .replace(/\n/g, '<br>');

    return description;
  }

  restartGame() {
    this.gameState = 'initial';
    this.currentNodeId = '';
    this.currentNode = null;
    this.isGameOver = false;
    this.isTransitioning = false;
    this.error = '';
    this.gameGraph = {};
    this.isWin = false;
  }
}