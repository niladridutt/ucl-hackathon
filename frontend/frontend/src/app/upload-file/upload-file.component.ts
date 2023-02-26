import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';


interface ApiResponse {
  q0: string;
  q1: string;
  q2: string;
  q3: string;
  q4: string;
  q5: string;
  q6: string;
  q7: string;
  q8: string;
  q9: string;
}

@Component({
  selector: 'app-upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.scss']
})

export class UploadFileComponent {

  fileName: string = '';
  selectedFile?: File;
  isLoading = false;

  constructor(private http: HttpClient, private router: Router) { }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }  

  onSubmit(): void {
    if (!this.selectedFile) {
      console.log('No file selected!');
      return;
    }

    this.isLoading = true;

    const formData = new FormData();
    formData.append('files', this.selectedFile, this.selectedFile.name); // Use the correct parameter name

    this.http.post<ApiResponse[]>('http://127.0.0.1:8000/uploadfiles', formData).subscribe(
      (response) => {
        console.log(response);
        localStorage.setItem('questions', JSON.stringify(response));
        this.isLoading = false;
        this.router.navigate(['/dashboard']);
      },
      (error) => {
        console.log(error);
        this.isLoading = false;
      }
    );
  }
}
