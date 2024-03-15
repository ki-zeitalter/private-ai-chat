import {Component, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat'
import {ChatService} from "../../services/chat.service";
import {BaseChatComponent} from "../base-chat/base-chat.component";
import {environment} from "../../../environments/environment";

@Component({
  selector: 'app-chat',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent extends BaseChatComponent {
  constructor(private _chatService: ChatService) {
    super(_chatService)
  }

  protected readonly environment = environment;
}
