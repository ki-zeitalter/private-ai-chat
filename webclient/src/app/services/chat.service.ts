import {Injectable} from '@angular/core';
import {v4 as uuidv4} from "uuid";
import {BehaviorSubject, Subject} from "rxjs";
import {Thread} from "../model/thread.model";

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  userId: string;

  currentThreadId?: string;

  currentAssistantId?: string;

  //onNewThread = new BehaviorSubject<MessageContent[] | undefined>(undefined);
  onActivateThread = new BehaviorSubject<Thread | null>(null);
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


  public activateThread(thread: Thread | null, assistantId?: string): void {

    this.currentAssistantId = assistantId;

    if (thread) {
      const copy = Object.assign({}, thread)

      if (!copy.thread_id) {
        copy.thread_id = uuidv4();
      }

      this.currentThreadId = copy.thread_id;
      this.currentAssistantId = copy.assistant_id;
      this.onActivateThread.next(copy);
    } else {
      this.currentThreadId = uuidv4();
      this.onActivateThread.next(null);
    }
  }
}
