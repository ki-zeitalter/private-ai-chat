import {Injectable} from '@angular/core';
import {Observable, Subject} from "rxjs";
import {Assistant} from "../model/assistant.model";
import {ChatService} from "./chat.service";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class AssistantService {

  onNewAssistant = new Subject();

  constructor(private chatService: ChatService,
              private router: Router,
              private httpClient: HttpClient) {
  }

  getAssistants(): Observable<Assistant[]> {
    return this.httpClient.get<Assistant[]>("http://localhost:8080/assistants")

  }

  saveAssistant(card: Assistant): Observable<Assistant> {
    return this.httpClient.post<Assistant>("http://localhost:8080/assistants", card)
  }

  activate(assistant: Assistant): void {
    if (assistant.type === 'assistant') {
      this.router.navigate(['analyzer']).then(() =>
        this.chatService.activateThread(null, assistant.assistant_id)
      )
    } else if (assistant.type === 'image_generator') {
      this.router.navigate(['text-to-image']).then(() =>
        this.chatService.activateThread(null, assistant.assistant_id)
      )

    }
  }

}
