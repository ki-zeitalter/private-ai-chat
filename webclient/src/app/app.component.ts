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
import {MessageContent} from "deep-chat/dist/types/messages";


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
    HttpClientModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements AfterViewInit, OnInit {

  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  userId: string;

  currentThreadId?: string;

  threads: History[] = []

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

    this.loadThreadNames();
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
  }

  newThread(): void {
    this.currentThreadId = uuidv4();

    this.deepChatElement?.nativeElement.clearMessages();
  }

  loadThreadNames() {
    this.threadsService.loadThreads(this.userId).subscribe(history => {
      console.log(history)

      this.threads = history;
    })
  }

  activateThread(thread: History){
    this.currentThreadId = thread.thread_id;

// TODO: pass a copy of the messages
    this.deepChatElement.nativeElement.initialMessages = thread.messages;
  }
}
