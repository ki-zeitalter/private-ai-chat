import {Component, CUSTOM_ELEMENTS_SCHEMA, ElementRef, OnInit, ViewChild} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat'
import {DeepChat} from "deep-chat";
import {RequestDetails} from "deep-chat/dist/types/interceptors";
import {ChatService} from "../../services/chat.service";

@Component({
  selector: 'app-text-to-image',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
  ],
  templateUrl: './text-to-image.component.html',
  styleUrl: './text-to-image.component.scss'
})
export class TextToImageComponent implements OnInit {
  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  @ViewChild('welcomePanel') welcomePanel!: ElementRef;

  constructor(private chatService: ChatService) {
  }

  ngAfterViewInit(): void {
    this.deepChatElement.nativeElement.requestInterceptor = (requestDetails: RequestDetails) => {
      if (requestDetails.headers) {
        requestDetails.headers['User-Id'] = this.chatService.userId;

        if (this.chatService.currentThreadId)
          requestDetails.headers['Thread-Id'] = this.chatService.currentThreadId;
      }

      return requestDetails;
    };

    this.deepChatElement.nativeElement.onNewMessage = (message) => {
      this.chatService.onNewMessage.next(message);

      this.deepChatElement.nativeElement.refreshMessages();
    };
  }

  ngOnInit(): void {
    this.chatService.onNewThread.subscribe(initialMessages => {
      if (this.deepChatElement) {
        this.deepChatElement.nativeElement.initialMessages = []
        this.deepChatElement.nativeElement.introMessage = {'text': 'Welcome!'};
        this.deepChatElement.nativeElement.textInput = {placeholder: {'text': 'Your message...'}}
        this.deepChatElement.nativeElement.clearMessages(true);


        if (initialMessages) {
          this.deepChatElement.nativeElement.initialMessages = initialMessages;
        }

        this.welcomePanel.nativeElement.display = "block";
      }
    });

    this.chatService.onActivateThread.subscribe(thread => {
      this.deepChatElement.nativeElement.initialMessages = thread.messages;
    })
  }
}
