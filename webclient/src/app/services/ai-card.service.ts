import {Injectable} from '@angular/core';
import {Observable} from "rxjs";
import {AICard} from "../model/ai-card.model";
import {ChatService} from "./chat.service";
import {Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class AiCardService {

  constructor(private chatService: ChatService,
              private router: Router,
              private httpClient: HttpClient) {
  }

  getAiCards(): Observable<AICard[]> {

    //const headers = new HttpHeaders().set('User-Id', user_id);

    return this.httpClient.get<AICard[]>("http://localhost:8080/agents")

  }

  activate(card: AICard): void {
    if (card.type === 'assistant') {
      this.router.navigate(['analyzer']).then(() =>
        this.chatService.activateThread(null)
      )
    } else if (card.type === 'image_generator') {
      this.router.navigate(['text-to-image']).then(() =>
        this.chatService.activateThread(null)
      )

    }
  }

}
