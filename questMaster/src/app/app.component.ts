import { Component } from '@angular/core';
import { GameComponent } from './game/game.component';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [GameComponent],
  template: `
    <app-adventure-game></app-adventure-game>
  `,
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'questMaster';
}