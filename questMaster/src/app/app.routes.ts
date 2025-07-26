import { Routes } from '@angular/router';
import { DashboardComponent } from './admin/dashboard/dashboard.component';
import { GameComponent } from './game/game.component';

export const routes: Routes = [
  {
    path: 'admin/dashboard',
    component: DashboardComponent
  },
  {
    path: '',
    component: GameComponent
  }
];