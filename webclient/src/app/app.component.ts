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
    AsyncPipe,],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements AfterViewInit, OnInit {

  @ViewChild('deepChat') deepChatElement!: ElementRef<DeepChat>;

  userId: string;

  currentThreadId?: string;

  threads: string[] = []

  private breakpointObserver = inject(BreakpointObserver);

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor() {
    this.userId = uuidv4();
  }

  ngOnInit() {
    this.newThread();
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

  loadThreadNames(){

  }

}
