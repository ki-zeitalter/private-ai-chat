import {Component, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

import 'deep-chat-dev'
import {ChatService} from "../../services/chat.service";
import {BaseChatComponent} from "../base-chat/base-chat.component";
import {environment} from "../../../environments/environment";
import {MatButton, MatIconButton} from "@angular/material/button";
import {MatButtonToggle, MatButtonToggleGroup, MatButtonToggleModule} from "@angular/material/button-toggle";
import {MatIcon} from "@angular/material/icon";

@Component({
  selector: 'app-chat',
  standalone: true,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  imports: [
    HighlightModule,
    CommonModule,
    MatIconButton,
    MatButton,
    MatButtonToggleGroup,
    MatButtonToggle,
    MatButtonToggleModule,
    MatIcon
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
