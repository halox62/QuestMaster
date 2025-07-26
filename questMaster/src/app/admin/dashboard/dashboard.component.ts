import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  isGenerating = false;
  storyResult: any = null;
  error: string | null = null;

  constructor(private http: HttpClient) {}

  generateStory() {
    if (this.isGenerating) return;

    this.isGenerating = true;
    this.error = null;
    this.storyResult = null;

    this.http.get('http://localhost:8080/genStory', {}).subscribe({
      next: (response: any) => {
        this.storyResult = response.success;
        this.isGenerating = false;
      },
      error: (error) => {
        this.error = `Errore: ${error.message}`;
        this.isGenerating = false;
      }
    });
  }
}