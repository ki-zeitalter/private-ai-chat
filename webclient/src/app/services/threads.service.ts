import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {Observable} from "rxjs";
import {Thread} from "../model/thread.model";

@Injectable({
  providedIn: 'root'
})
export class ThreadsService {

  constructor(private httpClient: HttpClient) {
  }

  loadThreads(user_id: string): Observable<Thread[]> {
    const headers = new HttpHeaders().set('User-Id', user_id);

    return this.httpClient.get<Thread[]>("http://localhost:8080/history", {headers})
  }
}
