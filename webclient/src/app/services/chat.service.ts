import {Injectable} from '@angular/core';
import {v4 as uuidv4} from "uuid";
import {BehaviorSubject, Subject} from "rxjs";
import {History} from "../model/history.model";
import {MessageContent} from "deep-chat/dist/types/messages";

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  userId: string;

  currentThreadId?: string;

  onNewThread = new Subject<MessageContent[] | undefined>();
  onActivateThread = new BehaviorSubject<History|null>(null);
  onNewMessage = new Subject();

  constructor() {
    const userId = localStorage.getItem('User-Id');

    if (userId) {
      this.userId = userId;
    } else {
      this.userId = uuidv4();
      localStorage.setItem('User-Id', this.userId);
    }
  }

  public newThread(initialMessages?: MessageContent[]): void{
    this.currentThreadId = uuidv4();
    this.onNewThread.next(initialMessages);
  }

  public activateThread(thread: History): void {
    this.currentThreadId = thread.thread_id;
    this.onActivateThread.next(thread);
  }
}
