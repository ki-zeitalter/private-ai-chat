import {Injectable} from '@angular/core';
import {v4 as uuidv4} from "uuid";
import {BehaviorSubject, Subject} from "rxjs";
import {History} from "../model/history.model";

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  userId: string;

  currentThreadId?: string;

  //onNewThread = new BehaviorSubject<MessageContent[] | undefined>(undefined);
  onActivateThread = new BehaviorSubject<History | null>(null);
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


  public activateThread(thread: History | null): void {
    if (thread) {
      const copy = Object.assign({}, thread)

      this.currentThreadId = copy.thread_id;
      this.onActivateThread.next(copy);
    } else {
      this.currentThreadId = uuidv4();
      this.onActivateThread.next(null);
    }
  }
}
