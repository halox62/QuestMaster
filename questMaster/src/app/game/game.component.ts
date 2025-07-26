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
  <!-- Animated background elements -->
  <div class="background-animation">
    <div class="floating-element" style="--delay: 0s; --duration: 8s; --x: 10%; --y: 20%"></div>
    <div class="floating-element" style="--delay: 2s; --duration: 10s; --x: 80%; --y: 10%"></div>
    <div class="floating-element" style="--delay: 4s; --duration: 12s; --x: 60%; --y: 70%"></div>
    <div class="floating-element" style="--delay: 6s; --duration: 9s; --x: 20%; --y: 80%"></div>
  </div>

  <!-- Particle effects -->
  <div class="particles">
    <div class="particle" *ngFor="let p of particles; let i = index"
         [style.left.px]="p.x"
         [style.top.px]="p.y"
         [style.animation-delay]="p.delay + 's'"></div>
  </div>

  <div class="content-wrapper">
    <!-- Enhanced title with typewriter effect -->
    <h1 *ngIf="gameState === 'playing'" class="game-title" [class.typing]="titleAnimation">
      <span class="title-text">{{ displayTitle }}</span>
      <span class="cursor" [class.blink]="titleAnimation">|</span>
    </h1>

    <!-- Enhanced initial screen -->
    <div *ngIf="gameState === 'initial'" class="initial-screen fade-in">
      <div class="welcome-message">
        <div class="subtitle">Prepare for an Epic Adventure</div>
        <div class="description">
          Explore mysterious worlds, solve puzzles, and discover hidden treasures
          in this interactive text adventure.
        </div>
      </div>

      <div class="button-container">
        <button
          class="game-button primary-button glow-effect"
          (click)="loadAndStartGame()"
          [disabled]="isLoading">
          <span class="button-icon">🎮</span>
          <span class="button-text">{{ isLoading ? 'Loading...' : 'Start Adventure' }}</span>
          <div class="button-shine"></div>
        </button>
      </div>

      <div *ngIf="error" class="error-message slide-in">
        <span class="error-icon">⚠️</span>
        {{ error }}
      </div>
    </div>

    <!-- Enhanced game screen -->
    <div *ngIf="gameState === 'playing'" class="game-screen fade-in">
      <!-- Progress indicator -->
      <div class="progress-bar">
        <div class="progress-fill" [style.width.%]="getProgressPercentage()"></div>
      </div>

      <div class="story-container">
        <!-- Story text with typewriter effect -->
        <div class="story-text"
             [class.typing-text]="isTyping"
             [innerHTML]="getFormattedDescription()"></div>

        <!-- Enhanced options -->
        <div class="options-container" *ngIf="currentNode?.options && hasOptions()">
          <div class="options-title">What do you want to do?</div>
          <div class="options-grid">
            <button
              *ngFor="let option of getOptionKeys(); let i = index"
              class="option-button"
              [class.option-hover]="!isTransitioning"
              (click)="selectOption(option)"
              [disabled]="isTransitioning"
              [style.animation-delay]="(i * 0.1) + 's'">
              <div class="option-icon">{{ getOptionIcon(i) }}</div>
              <div class="option-text">{{ getOptionText(option) }}</div>
              <div class="option-arrow">→</div>
            </button>
          </div>
        </div>

        <!-- Enhanced game over screen -->
        <div *ngIf="isGameOver" class="game-over fade-in">
          <div class="game-over-content">
            <div class="game-over-icon">
              <div class="icon-container" [class.victory]="isWin" [class.defeat]="!isWin">
                <span>{{ isWin ? '👑' : '💀' }}</span>
              </div>
            </div>

            <h2 class="game-over-title">
              {{ isWin ? 'Epic Victory!' : 'Adventure Ended!' }}
            </h2>

            <div class="game-result">
              <p *ngIf="isWin">
                🎉 Congratulations! You have successfully completed the adventure and claimed the legendary treasure!
              </p>
              <p *ngIf="!isWin">
                ⚔️ Your adventure ends here, but every end is a new beginning...
              </p>
            </div>



            <button class="game-button secondary-button pulse-effect" (click)="restartGame()">
              <span class="button-icon">🔄</span>
              <span class="button-text">New Adventure</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div *ngIf="isTransitioning" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <div class="loading-text">Loading...</div>
      </div>
    </div>
  </div>
</div>
  `,
  styles: [`
    :host {
      display: block;
      width: 100%;
      height: 100vh;
      overflow: hidden;
    }

    .game-container {
      position: relative;
      width: 100%;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
      overflow-x: hidden;
      overflow-y: auto;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Animated background */
    .background-animation {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 1;
    }

    .floating-element {
      position: absolute;
      width: 60px;
      height: 60px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50%;
      animation: float var(--duration) ease-in-out infinite;
      animation-delay: var(--delay);
      left: var(--x);
      top: var(--y);
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-20px) rotate(180deg); }
    }

    /* Particle effects */
    .particles {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 2;
    }

    .particle {
      position: absolute;
      width: 3px;
      height: 3px;
      background: rgba(255, 255, 255, 0.8);
      border-radius: 50%;
      animation: particle 8s linear infinite;
    }

    @keyframes particle {
      0% { transform: translateY(100vh) scale(0); opacity: 0; }
      10% { opacity: 1; }
      90% { opacity: 1; }
      100% { transform: translateY(-100px) scale(1); opacity: 0; }
    }

    .content-wrapper {
      position: relative;
      z-index: 10;
      max-width: 1000px;
      margin: 0 auto;
      padding: 20px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Enhanced title */
    .game-title {
  text-align: center;
  font-size: 3.5em;
  font-weight: 900;
  margin-bottom: 30px;
  color: #ffeaa7;
  position: relative;
  /* Rimuove completamente l'effetto luminoso */
}

.title-text {
  display: inline-block;
  color: inherit;
}

    .cursor {
      color: #ffeaa7;
      animation: blink 1s infinite;
    }

    @keyframes titleGlow {
      from {
        filter: brightness(1) drop-shadow(0 0 10px rgba(255, 234, 167, 0.7));
        text-shadow:
          0 0 20px rgba(255, 234, 167, 0.8),
          0 0 40px rgba(255, 234, 167, 0.6),
          0 0 60px rgba(255, 234, 167, 0.4),
          2px 2px 4px rgba(0, 0, 0, 0.5);
      }
      to {
        filter: brightness(1.3) drop-shadow(0 0 20px rgba(255, 234, 167, 0.9));
        text-shadow:
          0 0 30px rgba(255, 234, 167, 1),
          0 0 50px rgba(255, 234, 167, 0.8),
          0 0 80px rgba(255, 234, 167, 0.6),
          2px 2px 4px rgba(0, 0, 0, 0.5);
      }
    }

    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }

    /* Enhanced initial screen */
    .initial-screen {
      text-align: center;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      gap: 40px;
    }

    .welcome-message {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(15px);
      border-radius: 20px;
      padding: 40px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .subtitle {
      font-size: 1.5em;
      color: #ffeaa7;
      margin-bottom: 15px;
      font-weight: 600;
    }

    .description {
      font-size: 1.1em;
      line-height: 1.6;
      color: rgba(255, 255, 255, 0.9);
      max-width: 500px;
    }

    /* Enhanced buttons */
    .button-container {
      display: flex;
      gap: 20px;
      justify-content: center;
      flex-wrap: wrap;
    }

    .game-button {
      position: relative;
      padding: 18px 36px;
      font-size: 1.1em;
      border: none;
      border-radius: 50px;
      cursor: pointer;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      transition: all 0.3s ease;
      overflow: hidden;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .primary-button {
      background: linear-gradient(45deg, #ff6b6b, #ee5a24, #ff6b6b);
      color: white;
      background-size: 200% 200%;
      animation: gradientShift 3s ease infinite;
    }

    .secondary-button {
      background: linear-gradient(45deg, #4ecdc4, #44a08d, #4ecdc4);
      color: white;
      background-size: 200% 200%;
      animation: gradientShift 3s ease infinite;
    }

    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    .glow-effect:hover:not(:disabled) {
      transform: translateY(-3px);
      box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4);
    }

    .pulse-effect {
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    .button-shine {
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
      transition: left 0.5s;
    }

    .game-button:hover .button-shine {
      left: 100%;
    }

    .button-icon {
      font-size: 1.2em;
    }

    .game-button:disabled {
      opacity: 0.7;
      cursor: not-allowed;
      transform: none;
    }

    /* Enhanced game screen */
    .game-screen {
      flex: 1;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(15px);
      border-radius: 25px;
      padding: 30px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      margin-top: 20px;
    }

    .progress-bar {
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
      margin-bottom: 30px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(45deg, #4ecdc4, #44a08d);
      border-radius: 3px;
      transition: width 0.8s ease;
      position: relative;
    }

    .progress-fill::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
      animation: progressShine 2s ease-in-out infinite;
    }

    @keyframes progressShine {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(100%); }
    }

    .story-container {
      text-align: center;
    }

    .story-text {
      font-size: 1.2em;
      line-height: 1.8;
      margin-bottom: 40px;
      background: rgba(255, 255, 255, 0.1);
      padding: 30px;
      border-radius: 15px;
      border-left: 4px solid #4ecdc4;
      text-align: left;
      max-height: 400px;
      overflow-y: auto;
      color: rgba(255, 255, 255, 0.95);
      box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .typing-text {
      animation: typeWriter 2s steps(40, end);
    }

    @keyframes typeWriter {
      from { width: 0; }
      to { width: 100%; }
    }

    .story-text ::ng-deep h3 {
      color: #ffeaa7;
      margin-top: 20px;
      margin-bottom: 15px;
      font-weight: 600;
    }

    .story-text ::ng-deep strong {
      color: #74b9ff;
      font-weight: 700;
    }

    /* Enhanced options */
    .options-container {
      margin-top: 30px;
    }

    .options-title {
      font-size: 1.3em;
      color: #ffeaa7;
      margin-bottom: 25px;
      font-weight: 600;
    }

    .options-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      max-width: 800px;
      margin: 0 auto;
    }

    .option-button {
      display: flex;
      align-items: center;
      gap: 15px;
      padding: 20px;
      background: linear-gradient(135deg, #ffeaa7, #fdcb6e);
      color: #2d3436;
      border: none;
      border-radius: 15px;
      cursor: pointer;
      font-size: 1.0em;
      font-weight: 600;
      transition: all 0.3s ease;
      text-align: left;
      position: relative;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
      animation: slideInUp 0.6s ease-out forwards;
      opacity: 0;
      transform: translateY(20px);
    }

    @keyframes slideInUp {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .option-button:hover:not(:disabled) {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(253, 203, 110, 0.4);
      background: linear-gradient(135deg, #fdcb6e, #ffeaa7);
    }

    .option-icon {
      font-size: 1.5em;
      min-width: 30px;
    }

    .option-text {
      flex: 1;
      line-height: 1.4;
    }

    .option-arrow {
      font-size: 1.2em;
      opacity: 0.7;
      transition: transform 0.3s ease;
    }

    .option-button:hover .option-arrow {
      transform: translateX(5px);
    }

    .option-button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    /* Enhanced game over */
    .game-over {
      margin-top: 40px;
      text-align: center;
    }

    .game-over-content {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(15px);
      padding: 40px;
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .game-over-icon {
      margin-bottom: 20px;
    }

    .icon-container {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 80px;
      height: 80px;
      border-radius: 50%;
      font-size: 2.5em;
      margin-bottom: 20px;
      animation: iconBounce 2s ease-in-out infinite;
    }

    .icon-container.victory {
      background: linear-gradient(45deg, #00b894, #00cec9);
      box-shadow: 0 0 30px rgba(0, 184, 148, 0.5);
    }

    .icon-container.defeat {
      background: linear-gradient(45deg, #e84393, #fd79a8);
      box-shadow: 0 0 30px rgba(232, 67, 147, 0.5);
    }

    @keyframes iconBounce {
      0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-10px); }
      60% { transform: translateY(-5px); }
    }

    .game-over-title {
      font-size: 2.2em;
      margin-bottom: 20px;
      background: linear-gradient(45deg, #ffeaa7, #fdcb6e);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-weight: 700;
    }

    .game-result {
      margin-bottom: 30px;
      font-size: 1.2em;
      line-height: 1.6;
      color: rgba(255, 255, 255, 0.9);
    }

    .game-stats {
      background: rgba(255, 255, 255, 0.1);
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 30px;
      display: inline-block;
    }

    .stat {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      margin-bottom: 10px;
    }

    .stat:last-child {
      margin-bottom: 0;
    }

    .stat-label {
      color: rgba(255, 255, 255, 0.8);
    }

    .stat-value {
      color: #ffeaa7;
      font-weight: 700;
      font-size: 1.1em;
    }

    /* Loading overlay */
    .loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(10px);
    }

    .loading-spinner {
      text-align: center;
      color: white;
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid rgba(255, 255, 255, 0.3);
      border-top: 4px solid #4ecdc4;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading-text {
      font-size: 1.2em;
      font-weight: 600;
    }

    /* Animations */
    .fade-in {
      animation: fadeIn 0.8s ease-out;
    }

    .slide-in {
      animation: slideIn 0.5s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to { opacity: 1; transform: translateX(0); }
    }

    .error-message {
      color: #ff6b6b;
      background: rgba(255, 107, 107, 0.1);
      padding: 20px;
      border-radius: 15px;
      border: 1px solid rgba(255, 107, 107, 0.3);
      backdrop-filter: blur(10px);
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
    }

    .error-icon {
      font-size: 1.2em;
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .game-title {
        font-size: 2.5em;
      }

      .content-wrapper {
        padding: 15px;
      }

      .game-screen {
        padding: 20px;
      }

      .options-grid {
        grid-template-columns: 1fr;
      }

      .option-button {
        padding: 15px;
        font-size: 0.9em;
      }

      .story-text {
        font-size: 1.0em;
        padding: 20px;
      }

      .welcome-message {
        padding: 25px;
      }

      .game-button {
        padding: 15px 25px;
        font-size: 1.0em;
      }
    }

    @media (max-width: 480px) {
      .game-title {
        font-size: 2em;
      }

      .button-container {
        flex-direction: column;
        align-items: center;
      }

      .game-button {
        width: 100%;
        max-width: 300px;
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
  isTyping = false;
  error = '';
  moveCount = 0;

  displayTitle = 'The Island';
  titleAnimation = true;
  particles: Array<{x: number, y: number, delay: number}> = [];

  private apiBaseUrl = 'http://localhost:8080';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.initializeParticles();
    this.startTitleAnimation();
  }

  initializeParticles() {
    for (let i = 0; i < 20; i++) {
      this.particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        delay: Math.random() * 8
      });
    }
  }

  startTitleAnimation() {
    setTimeout(() => {
      this.titleAnimation = false;
    }, 3000);
  }

  getProgressPercentage(): number {
    if (!this.gameGraph || Object.keys(this.gameGraph).length === 0) return 0;

    const totalNodes = Object.keys(this.gameGraph).length;
    const currentNodeNumber = parseInt(this.currentNodeId.replace('node_', '')) || 1;

    return Math.min((currentNodeNumber / totalNodes) * 100, 100);
  }

  getOptionIcon(index: number): string {
    const icons = ['⚔️', '🛡️', '🔍', '💎', '🗝️', '🌟', '🎯', '🔥'];
    return icons[index % icons.length];
  }

  generateStory() {
    this.isGenerating = true;
    this.error = '';

    this.http.get(`${this.apiBaseUrl}/genStory`).subscribe({
      next: () => {
        this.isGenerating = false;
        console.log('Story generated successfully!');
      },
      error: (err) => {
        this.isGenerating = false;
        this.error = 'Error generating the story. Please try again.';
        console.error('Error genStory:', err);
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
        this.error = 'Error loading the game. Ensure the story has been generated.';
        console.error('Error loadGraph:', err);
      }
    });
  }

  startGame() {
    this.currentNodeId = 'node_1';
    this.currentNode = this.gameGraph[this.currentNodeId];
    this.gameState = 'playing';
    this.isGameOver = false;
    this.isWin = false;
    this.moveCount = 0;
    this.isTyping = true;

    // Riavvia l'animazione del titolo
    this.titleAnimation = true;
    this.startTitleAnimation();

    // Stop typing animation after a delay
    setTimeout(() => {
      this.isTyping = false;
    }, 2000);

    if (!this.currentNode) {
      this.error = 'Error: Initial node not found in the graph.';
      this.gameState = 'initial';
    }
  }

  selectOption(optionKey: string) {
    if (!this.currentNode || this.isTransitioning) return;

    const option = this.currentNode.options[optionKey];
    if (!option) return;

    this.isTransitioning = true;
    this.moveCount++;

    setTimeout(() => {
      const nextNodeId = option.target;
      const cleanedNodeId = nextNodeId.replace(/\s*✅\s*$/, '').trim();

      if (this.gameGraph[cleanedNodeId]) {
        this.currentNodeId = cleanedNodeId;
        this.currentNode = this.gameGraph[cleanedNodeId];
        this.isTyping = true;

        // Stop typing animation
        setTimeout(() => {
          this.isTyping = false;
        }, 1500);

        this.checkGameEnd();
      } else {
        console.log('Target node not found in graph, ending game');
        this.isGameOver = true;
        this.isWin = this.isWinningCondition(option.text, nextNodeId);
      }

      this.isTransitioning = false;
    }, 800);
  }

  checkGameEnd() {
    if (!this.currentNode) return;

    const hasOptions = this.currentNode.options && Object.keys(this.currentNode.options).length > 0;

    if (!hasOptions) {
      this.isGameOver = true;
      this.isWin = this.isWinningNode();
    }
  }

  getOptionKeys(): string[] {
    if (!this.currentNode?.options) return [];
    return Object.keys(this.currentNode.options);
  }

  getOptionText(optionKey: string): string {
    if (this.currentNode?.options && this.currentNode.options[optionKey]) {
      let optionText = this.currentNode.options[optionKey].text;

      // Clean up option text
      optionText = optionText.replace(/\s*\([^)]*\)\s*$/, '');
      optionText = optionText.replace(/^\*+\s*/, '');
      optionText = optionText.replace(/:\s*$/, '');

      return optionText.trim();
    }
    return `Option ${optionKey}`;
  }

  hasOptions(): boolean {
    return !!(this.currentNode?.options && Object.keys(this.currentNode.options).length > 0);
  }

  isWinningNode(): boolean {
    const description = this.currentNode?.description || '';
    const hasWinSymbol = description.includes('✅');
    const hasWinText = this.containsWinningText(description);

    return hasWinSymbol || hasWinText;
  }

  isWinningCondition(optionText: string, targetNodeId: string): boolean {
    const nodeIdHasWinSymbol = targetNodeId.includes('✅');
    const optionHasWinText = this.containsWinningText(optionText);
    const puzzleRelated = optionText.toLowerCase().includes('puzzle') ||
                         optionText.toLowerCase().includes('solve');

    const currentDescription = this.currentNode?.description || '';
    const isInTreasureContext = currentDescription.toLowerCase().includes('treasure') ||
                               currentDescription.toLowerCase().includes('vault') ||
                               currentDescription.toLowerCase().includes('altar');

    if (isInTreasureContext && puzzleRelated && nodeIdHasWinSymbol) {
      return true;
    }

    return nodeIdHasWinSymbol || optionHasWinText;
  }

  containsWinningText(text: string): boolean {
    const winningKeywords = [
      'treasure', 'victory', 'success',
      'completed', 'won', 'triumph', 'achieve',
      'treasure_claimed: true', 'puzzle_solved: true'
    ];

    const lowerText = text.toLowerCase();
    return winningKeywords.some(keyword => lowerText.includes(keyword.toLowerCase()));
  }

  getFormattedDescription(): string {
    if (!this.currentNode) return '';

    let description = this.currentNode.description;

    // Extract narrative description
    const narrativeMatch = description.match(/\*\*Narrative Description:\*\*\s*([\s\S]*?)(?=\n\*\*|$)/);

    if (narrativeMatch) {
      description = narrativeMatch[1].trim();
    }

    // Convert markdown to HTML with enhanced formatting
    description = description
      .replace(/\*\*(.*?)\*\*/g, '<strong class="highlight">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="emphasis">$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');

    // Wrap in paragraph tags if not already wrapped
    if (!description.startsWith('<p>')) {
      description = `<p>${description}</p>`;
    }

    return description;
  }

  restartGame() {
    this.gameState = 'initial';
    this.currentNodeId = '';
    this.currentNode = null;
    this.isGameOver = false;
    this.isTransitioning = false;
    this.isTyping = false;
    this.error = '';
    this.gameGraph = {};
    this.isWin = false;
    this.moveCount = 0;

    // Regenerate particles for fresh start
    this.initializeParticles();
    this.startTitleAnimation();
  }
}