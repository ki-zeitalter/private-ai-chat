import {Component, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat'
import {ChatService} from "../../services/chat.service";
import {BaseChatComponent} from "../base-chat/base-chat.component";

@Component({
  selector: 'app-text-to-image',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
  ],
  templateUrl: './text-to-image.component.html',
  styleUrl: './text-to-image.component.scss'
})
export class TextToImageComponent extends BaseChatComponent {
  constructor(private _chatService: ChatService) {
    super(_chatService)
  }
}
