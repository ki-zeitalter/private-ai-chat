import {Component, NgZone, OnInit} from '@angular/core';
import {MatListItem, MatNavList} from "@angular/material/list";
import {NgForOf} from "@angular/common";
import {MessageContent} from "deep-chat/dist/types/messages";
import {History} from "../../model/history.model";
import {ThreadsService} from "../../services/threads.service";
import {ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-threads',
  standalone: true,
  imports: [
    MatListItem,
    MatNavList,
    NgForOf
  ],
  templateUrl: './threads.component.html',
  styleUrl: './threads.component.scss'
})
export class ThreadsComponent implements OnInit {
  threads: History[] = []

  constructor(private ngZone: NgZone,
              private threadsService: ThreadsService,
              private chatService: ChatService,
              private router: Router) {
  }

  ngOnInit() {
    this.newThread();

    this.loadThreads();


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
}
