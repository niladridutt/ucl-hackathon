import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Feedback {
  [key: string]: string;
}

@Component({
  selector: 'app-quiz',
  templateUrl: './quiz.component.html',
  styleUrls: ['./quiz.component.scss']
})
export class QuizComponent {
  questions: any;
  qqs: any;
  answers: {[key: string]: string} = {};
  feedback = false;
  feedbacks : any;
  loading = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.qqs = localStorage.getItem('questions');
    if (this.qqs) {
      this.qqs = JSON.parse(this.qqs)[0];
    } else {
      console.log('Questions not found in local storage');
    }
    this.questions = [this.qqs['q0'], this.qqs['q1'], this.qqs['q2'], this.qqs['q3'], this.qqs['q4'], this.qqs['q5'], this.qqs['q6'], 
                    this.qqs['q7'], this.qqs['q8'], this.qqs['q9']];

    console.log(this.questions)
  }

  submitAnswers() {
    const body = [];
    this.loading = true;
    for (let i = 0; i < this.questions.length; i++) {
      body.push({ "answer": this.answers[i] });
    }
    console.log(body);
    this.http.post<any>('http://127.0.0.1:8000/check_answers/', body).subscribe(
    (response) => {
      console.log('response got')
      console.log(response);
      console.log(response[0]['f0'])
      this.feedbacks = [response[0]['f0'], response[0]['f1'], response[0]['f2'], response[0]['f3'], response[0]['f4'], response[0]['f5'],
                  response[0]['f6'], response[0]['f7'], response[0]['f8'], response[0]['f9']];
      this.loading = false;
      this.feedback = true;
    },
    error => console.log(error)
  );
  }
  
}
