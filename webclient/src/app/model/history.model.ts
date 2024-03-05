import {MessageContent} from "deep-chat/dist/types/messages";

export interface History {
  user_id: string;
  thread_id: string;
  messages: MessageContent[]
}
