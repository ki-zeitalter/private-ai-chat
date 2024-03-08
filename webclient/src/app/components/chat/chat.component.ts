import {
  AfterViewInit,
  Component,
  CUSTOM_ELEMENTS_SCHEMA,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild
} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat'
import {DeepChat} from "deep-chat";
import {RequestDetails} from "deep-chat/dist/types/interceptors";
import {ChatService} from "../../services/chat.service";
import {Subscription} from "rxjs";
import {MessageContent} from "deep-chat/dist/types/messages";

@Component({
  selector: 'app-chat',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  @ViewChild('welcomePanel') welcomePanel!: ElementRef;

  private onNewThreadSubscription?: Subscription;
  private onActivateThreadSubscription?: Subscription;

  initialMessages: MessageContent[] | undefined;

  constructor(private chatService: ChatService) {
  }

  ngOnDestroy(): void {
    if (this.onNewThreadSubscription) {
      this.onNewThreadSubscription.unsubscribe();
    }

    if (this.onActivateThreadSubscription) {
      this.onActivateThreadSubscription.unsubscribe();
    }
  }

  ngAfterViewInit(): void {
    this.deepChatElement.nativeElement.initialMessages = this.initialMessages;

    this.deepChatElement.nativeElement.requestInterceptor = (requestDetails: RequestDetails) => {
      if (requestDetails.headers) {
        requestDetails.headers['User-Id'] = this.chatService.userId;

        if (this.chatService.currentThreadId)
          requestDetails.headers['Thread-Id'] = this.chatService.currentThreadId;
      }

      return requestDetails;
    };

    this.deepChatElement.nativeElement.onNewMessage = (message) => {
      if (!message.isInitial) {
        this.chatService.onNewMessage.next(message);

        this.deepChatElement.nativeElement.refreshMessages();
      }
    };
  }

  ngOnInit(): void {
    this.onNewThreadSubscription = this.chatService.onNewThread.subscribe(initialMessages => {
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

    this.onActivateThreadSubscription = this.chatService.onActivateThread.subscribe(thread => {
      if (thread) {
        this.initialMessages = thread.messages;
      } else {
        this.initialMessages = undefined;
      }

      if(this.deepChatElement){
        this.deepChatElement.nativeElement.initialMessages = this.initialMessages;
      }
    })
  }
}
