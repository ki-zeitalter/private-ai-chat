import {Injectable} from '@angular/core';
import {Observable} from "rxjs";
import {Assistant} from "../model/assistant.model";
import {ChatService} from "./chat.service";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class AssistantService {

  constructor(private chatService: ChatService,
              private router: Router,
              private httpClient: HttpClient) {
  }

  getAssistants(): Observable<Assistant[]> {
    return this.httpClient.get<Assistant[]>("http://localhost:8080/agents")

  }

  saveAssistant(card: Assistant): Observable<Assistant> {
    return this.httpClient.post<Assistant>("http://localhost:8080/agents", card)
  }

  activate(assistant: Assistant): void {
    if (assistant.type === 'assistant') {
      this.router.navigate(['analyzer']).then(() =>
        this.chatService.activateThread(null, assistant.agent_id)
      )
    } else if (assistant.type === 'image_generator') {
      this.router.navigate(['text-to-image']).then(() =>
        this.chatService.activateThread(null, assistant.agent_id)
      )

    }
  }

}
