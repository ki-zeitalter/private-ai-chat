import {AfterViewInit, Component, CUSTOM_ELEMENTS_SCHEMA, ElementRef, inject, OnInit, ViewChild} from '@angular/core';
import {RouterOutlet} from '@angular/router';

import {AsyncPipe, CommonModule} from "@angular/common";
import {MatIcon, MatIconModule} from "@angular/material/icon";
import {MatButtonModule, MatIconButton} from "@angular/material/button";
import {MatListItem, MatListModule, MatNavList} from "@angular/material/list";
import {MatSidenav, MatSidenavContainer, MatSidenavContent, MatSidenavModule} from "@angular/material/sidenav";
import {MatToolbar, MatToolbarModule} from "@angular/material/toolbar";
import {BreakpointObserver, Breakpoints} from "@angular/cdk/layout";
import {Observable} from "rxjs";
import {map, shareReplay} from "rxjs/operators";

import 'deep-chat'
import {DeepChat} from "deep-chat";
import {RequestDetails} from "deep-chat/dist/types/interceptors";

import {v4 as uuidv4} from 'uuid';
import {ThreadsService} from "./services/threads.service";
import {HttpClientModule} from "@angular/common/http";
import {History} from "./model/history.model";
import {IntroMessage, MessageContent} from "deep-chat/dist/types/messages";
import {MatGridList, MatGridTile, MatGridTileText} from "@angular/material/grid-list";
import {
  MatCard,
  MatCardActions,
  MatCardContent,
  MatCardHeader, MatCardImage,
  MatCardSubtitle,
  MatCardTitle
} from "@angular/material/card";
import {AICard} from "./model/ai-card.model";


@Component({
  selector: 'app-root',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    CommonModule,
    RouterOutlet,
    AsyncPipe,
    MatIcon,
    MatIconButton,
    MatListItem,
    MatNavList,
    MatSidenav,
    MatSidenavContainer,
    MatSidenavContent,
    MatToolbar,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    AsyncPipe,
    HttpClientModule,
    MatGridList,
    MatGridTile,
    MatGridTileText,
    MatCardActions,
    MatCardContent,
    MatCardSubtitle,
    MatCardTitle,
    MatCardHeader,
    MatCard,
    MatCardImage
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements AfterViewInit, OnInit {

  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  userId: string;

  currentThreadId?: string;

  threads: History[] = []

  aiCards: AICard[] = [];

  private breakpointObserver = inject(BreakpointObserver);

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor(private threadsService: ThreadsService) {
    const userId = localStorage.getItem('User-Id');
    if (userId) {
      this.userId = userId;
    } else {
      this.userId = uuidv4();
      localStorage.setItem('User-Id', this.userId);
    }
  }

  ngOnInit() {
    this.newThread();

    this.loadThreads();

    this.aiCards = this.constructDemoCards();
  }

  ngAfterViewInit(): void {
    this.deepChatElement.nativeElement.requestInterceptor = (requestDetails: RequestDetails) => {
      if (requestDetails.headers) {
        requestDetails.headers['User-Id'] = this.userId;

        if (this.currentThreadId)
          requestDetails.headers['Thread-Id'] = this.currentThreadId;
      }

      return requestDetails;
    };

    this.deepChatElement.nativeElement.onNewMessage = (message) => {
      this.loadThreads();
    };
  }

  newThread(initialMessages?: MessageContent[]): void {
    this.currentThreadId = uuidv4();

    if (this.deepChatElement) {
      this.deepChatElement.nativeElement.initialMessages = []
      this.deepChatElement.nativeElement.introMessage = {'text': 'Welcome!'};
      this.deepChatElement.nativeElement.textInput = {placeholder: {'text': 'Your message...'}}
      this.deepChatElement.nativeElement.clearMessages(true);

      if (initialMessages) {
        this.deepChatElement.nativeElement.initialMessages = initialMessages;
      }
    }
  }

  loadThreads() {
    this.threadsService.loadThreads(this.userId).subscribe(history => {
      this.threads = history;
    })
  }

  activateThread(thread: History) {
    this.currentThreadId = thread.thread_id;

    this.deepChatElement.nativeElement.initialMessages = thread.messages;
  }

  constructDemoCards(): AICard[] {
    const result: AICard[] = [];

    result.push({
      name: 'Email assistant',
      description: 'Write an email with the help of a ai assistant',
      icon: '',
      action: () => {
        console.log("Email assistant app activated");
        const appMessages: MessageContent[] = [];

        appMessages.push({
          role: 'ai',
          'text': 'Hello! I am your AI assistant for writing professional sounding emails!'
        })

        this.newThread(appMessages);

        this.deepChatElement.nativeElement.introMessage = {'text': 'Please enter the topic of the email!'} as IntroMessage

        this.deepChatElement.nativeElement.textInput = {placeholder: {'text': 'Insert topic of the email here!'}}
      }
    })

    return result;
  }
}
