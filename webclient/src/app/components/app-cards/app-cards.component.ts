import {Component, OnInit} from '@angular/core';
import {MatButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {NgForOf} from "@angular/common";
import {AICard} from "../../model/ai-card.model";
import {MessageContent} from "deep-chat/dist/types/messages";
import {Thread} from "../../model/thread.model";
import {ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-app-cards',
  standalone: true,
  imports: [
    MatButton,
    MatCard,
    MatCardActions,
    MatCardContent,
    MatCardHeader,
    MatCardTitle,
    NgForOf
  ],
  templateUrl: './app-cards.component.html',
  styleUrl: './app-cards.component.scss'
})
export class AppCardsComponent implements OnInit {

  aiCards: AICard[] = [];

  constructor(
    private chatService: ChatService,
    private router: Router) {
  }

  ngOnInit() {
    this.aiCards = this.constructDemoCards();
  }

  constructDemoCards(): AICard[] {
    const result: AICard[] = [];

    result.push({
      name: 'Email assistant',
      description: 'Write an email with the help of an ai assistant',
      icon: '',
      action: () => {

        const appMessages: MessageContent[] = [];

        appMessages.push({
          role: 'ai',
          'text': 'Hello! I am your AI assistant for writing professional sounding emails!'
        })

        this.newThread(appMessages);

        //this.deepChatElement.nativeElement.introMessage = {'text': 'Please enter the topic of the email!'} as IntroMessage

        // TODO
        //this.deepChatElement.nativeElement.textInput = {placeholder: {'text': 'Insert topic of the email here!'}}


      }
    })

    result.push({
      name: 'Generate images',
      description: 'Generate images by DALL-E 3',
      icon: '',
      action: () => {
        this.router.navigate(['text-to-image']).then(() =>
          this.chatService.activateThread(null)
        )
      }
    })

    result.push({
      name: 'Analyze files',
      description: 'Analyze files like CSV, Excel, PDF, etc.',
      icon: '',
      action: () => {
        this.router.navigate(['analyzer']).then(() =>
          this.chatService.activateThread(null)
        )
      }
    })

    return result;
  }

  newThread(initialMessages?: MessageContent[]): void {
    let thread: Thread | null = null;

    if (initialMessages) {
      thread = {} as Thread
      thread.messages = initialMessages || [];
    }


    this.router.navigate(['chat']).then(() => {
      this.chatService.activateThread(thread)
    })
  }
}
