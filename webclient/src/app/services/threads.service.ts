import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class ThreadsService {

  constructor(private httpClient: HttpClient) { }


}
