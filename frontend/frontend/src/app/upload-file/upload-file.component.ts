import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-upload-file',
  templateUrl: './upload-file.component.html',
  styleUrls: ['./upload-file.component.scss']
})
export class UploadFileComponent {

  fileName: string = '';
  selectedFile?: File;

  constructor(private http: HttpClient) { }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
  }  

  onSubmit(): void {
    if (!this.selectedFile) {
      console.log('No file selected!');
      return;
    }

    const formData = new FormData();
    formData.append('pdfFile', this.selectedFile, this.selectedFile.name);

    formData.append('fileName', this.fileName);

    this.http.post('http://your-api-endpoint.com/upload', formData).subscribe(
      (response) => {
        console.log(response);
      },
      (error) => {
        console.log(error);
      }
    );
  }
}
