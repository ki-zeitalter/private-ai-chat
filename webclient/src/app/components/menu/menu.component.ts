import {Component, inject, NgZone, OnInit} from '@angular/core';
import {AsyncPipe, NgForOf, NgOptimizedImage} from "@angular/common";
import {ChatComponent} from "../chat/chat.component";
import {MatButton, MatIconButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {MatDivider} from "@angular/material/divider";
import {MatIcon} from "@angular/material/icon";
import {MatListItem, MatNavList} from "@angular/material/list";
import {MatSidenav, MatSidenavContainer, MatSidenavContent} from "@angular/material/sidenav";
import {MatToolbar} from "@angular/material/toolbar";
import {History} from "../../model/history.model";
import {AICard} from "../../model/ai-card.model";
import {BreakpointObserver, Breakpoints} from "@angular/cdk/layout";
import {Observable} from "rxjs";
import {map, shareReplay} from "rxjs/operators";
import {ThreadsService} from "../../services/threads.service";
import {ChatService} from "../../services/chat.service";
import {MessageContent} from "deep-chat/dist/types/messages";
import {Router, RouterOutlet} from "@angular/router";

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [
    AsyncPipe,
    ChatComponent,
    MatButton,
    MatCard,
    MatCardActions,
    MatCardContent,
    MatCardHeader,
    MatCardTitle,
    MatDivider,
    MatIcon,
    MatIconButton,
    MatListItem,
    MatNavList,
    MatSidenav,
    MatSidenavContainer,
    MatSidenavContent,
    MatToolbar,
    NgForOf,
    RouterOutlet,
    NgOptimizedImage
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss'
})
export class MenuComponent implements OnInit {
  threads: History[] = []
  aiCards: AICard[] = [];

  private breakpointObserver = inject(BreakpointObserver);


  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor(
    private ngZone: NgZone,
    private threadsService: ThreadsService,
    private chatService: ChatService,
    private router: Router) {
  }

  ngOnInit() {
    this.newThread();

    this.loadThreads();

    this.aiCards = this.constructDemoCards();

    this.chatService.onNewMessage.subscribe(() => {
      this.ngZone.run(() =>
        window.setTimeout(() => this.loadThreads(), 2000)
      )
    });
  }


  newThread(initialMessages?: MessageContent[]): void {
    this.router.navigate(['chat']).then(() => {

      this.chatService.activateThread(null)
    })
  }

  loadThreads() {
    this.threadsService.loadThreads(this.chatService.userId).subscribe(history => {
      console.log('Threads loaded', history)
      this.threads = history;
    })
  }

  activateThread(thread: History) {
    let target = 'chat'

    if (thread.app_type) {
      target = thread.app_type;
    }


    this.router.navigate([target]).then(() => {
      this.chatService.activateThread(thread);
    })

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

    return result;
  }
}
