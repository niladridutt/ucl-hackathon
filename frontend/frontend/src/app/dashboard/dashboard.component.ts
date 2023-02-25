import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

interface Pdf {
  id: number;
  title: string;
  thumbnail: string;
  pdfUrl: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})

export class DashboardComponent implements OnInit {

  constructor(private http: HttpClient, private router: Router) { }

  name = "Andrei";
  score = 0;

  pdfList: Pdf[] = [];
  selectedPdfIds: number[] = [];

  ngOnInit(): void {
    console.log('haha');
    this.http.get<Pdf[]>('http://127.0.0.1:8000/list_of_pdfs').subscribe(
      (response) => {
        this.pdfList = response;
      },
      (error) => {
        console.log(error);
      }
    );
  }

  uploadPdf() {
    this.router.navigate(['/upload-file']);
  }

  onCheckboxChange(event: any) {
    const pdfId = parseInt(event.target.id);
    if (event.target.checked) {
      this.selectedPdfIds.push(pdfId);
    } else {
      const index = this.selectedPdfIds.indexOf(pdfId);
      if (index !== -1) {
        this.selectedPdfIds.splice(index, 1);
      }
    }

    console.log(this.selectedPdfIds);
  }

  startQuiz() {
    
  }
}
