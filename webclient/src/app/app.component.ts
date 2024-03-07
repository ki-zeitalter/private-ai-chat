import {Component, CUSTOM_ELEMENTS_SCHEMA, inject, OnInit} from '@angular/core';
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
import {ThreadsService} from "./services/threads.service";
import {HttpClientModule} from "@angular/common/http";
import {History} from "./model/history.model";
import {MessageContent} from "deep-chat/dist/types/messages";
import {MatGridList, MatGridTile, MatGridTileText} from "@angular/material/grid-list";
import {
  MatCard,
  MatCardActions,
  MatCardContent,
  MatCardHeader,
  MatCardImage,
  MatCardSubtitle,
  MatCardTitle
} from "@angular/material/card";
import {AICard} from "./model/ai-card.model";
import './code_highlight';
import {HighlightModule} from "ngx-highlightjs";
import {ChatComponent} from "./components/chat/chat.component";
import {ChatService} from "./services/chat.service";

@Component({
  selector: 'app-root',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
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
    MatCardImage,
    ChatComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  threads: History[] = []
  aiCards: AICard[] = [];

  private breakpointObserver = inject(BreakpointObserver);


  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor(private threadsService: ThreadsService, private chatService: ChatService) {
  }

  ngOnInit() {
    this.newThread();

    this.loadThreads();

    this.aiCards = this.constructDemoCards();

    this.chatService.onNewMessage.subscribe(() => {
      window.setTimeout(() => this.loadThreads(), 2000);
    });
  }


  newThread(initialMessages?: MessageContent[]): void {
    this.chatService.newThread(initialMessages);
  }

  loadThreads() {
    this.threadsService.loadThreads(this.chatService.userId).subscribe(history => {
      this.threads = history;
    })
  }

  activateThread(thread: History) {
    this.chatService.activateThread(thread);

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

        //this.deepChatElement.nativeElement.introMessage = {'text': 'Please enter the topic of the email!'} as IntroMessage

        // TODO
        //this.deepChatElement.nativeElement.textInput = {placeholder: {'text': 'Insert topic of the email here!'}}
      }
    })

    return result;
  }
}
