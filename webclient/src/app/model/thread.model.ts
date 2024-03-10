import {MessageContent} from "deep-chat/dist/types/messages";

export interface Thread {
  user_id: string;
  thread_id: string;
  messages: MessageContent[]
  app_type: string;
}
