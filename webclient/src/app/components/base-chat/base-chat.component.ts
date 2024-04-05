import {AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild} from "@angular/core";
import {DeepChat} from "deep-chat-dev";
import {Subscription} from "rxjs";
import {MessageContent} from "deep-chat-dev/dist/types/messages";
import {ChatService} from "../../services/chat.service";
import {RequestDetails} from "deep-chat-dev/dist/types/interceptors";

@Component({
  standalone: true,

  template: ``
})
export abstract class BaseChatComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  @ViewChild('welcomePanel') welcomePanel!: ElementRef;

  private onNewThreadSubscription?: Subscription;
  private onActivateThreadSubscription?: Subscription;

  initialMessages: MessageContent[] | undefined;

  providerId: string | undefined = "openai";

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
    this.deepChatElement.nativeElement.history = this.initialMessages;

    this.deepChatElement.nativeElement.requestInterceptor = (requestDetails: RequestDetails) => {
      return this.requestInterceptor(requestDetails);
    };

    this.deepChatElement.nativeElement.onMessage = (message) => {
      if (!message.isHistory) {
        this.chatService.onNewMessage.next(message);

        this.deepChatElement.nativeElement.refreshMessages();
      }
    };
  }

  protected requestInterceptor(requestDetails: RequestDetails): RequestDetails {

    if (!requestDetails.headers) requestDetails.headers = {};


    requestDetails.headers['User-Id'] = this.chatService.userId;

    if (this.chatService.currentThreadId)
      requestDetails.headers['Thread-Id'] = this.chatService.currentThreadId;

    if (this.chatService.currentAssistantId)
      requestDetails.headers['Assistant-Id'] = this.chatService.currentAssistantId;


    if (requestDetails.body && typeof requestDetails.body === 'object' && !(requestDetails.body instanceof FormData)) {
      requestDetails.body['provider'] = this.providerId;
    }

    //if (requestDetails.body instanceof FormData && this.providerId) {
    //  requestDetails.body.append('provider', this.providerId);
    //}




    return requestDetails;
  }

  ngOnInit(): void {
    this.onActivateThreadSubscription = this.chatService.onActivateThread.subscribe(thread => {
      if (thread) {
        this.initialMessages = thread.messages;
        this.providerId = thread.provider;
      } else {
        this.initialMessages = undefined;
        this.providerId = 'openai';
      }

      if (this.deepChatElement) {
       this.deepChatElement.nativeElement.history = this.initialMessages;
      }
    })
  }
}
